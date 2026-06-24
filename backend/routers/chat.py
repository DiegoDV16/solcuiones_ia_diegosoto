import sys
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from backend.monitoring.logger import log_chat_interaction, log_error
from backend.monitoring.metrics import metrics
from backend.monitoring.tracing import tracer, trace_context
from backend.monitoring.security import sanitize_chat_message, ai_rate_limiter, sanitizer
from backend.monitoring.cache import response_cache

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    reply: str
    session_id: str


try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_core.tools import tool
    from langchain.agents import create_react_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    import numpy as np

    import importlib
    import Scripts.catalog_db as catalog_db
    importlib.reload(catalog_db)
    from Scripts.catalog_db import (
        query_product_db,
        get_all_skus,
        list_branches,
        create_order_by_branch_code,
        get_order_details,
    )

    token = os.getenv("GITHUB_TOKEN") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://models.inference.ai.azure.com")

    _HAS_LLM = bool(token)
    _chat_llm = None
    _app_agent = None

    if _HAS_LLM:
        _chat_llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=token,
            base_url=base_url,
            temperature=0.1,
        )

        _embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=token,
            base_url=base_url,
        )

        _doc = (
            "Notebook ideal para programación y gaming: Mínimo 16GB RAM, SSD 512GB, "
            "GPU RTX 3050+. En Chile (PC Factory): Gama media: 600.000 - 900.000 CLP. "
            "Gama alta: 900.000 - 1.500.000 CLP."
        )
        _chunks = [_doc[i:i+200] for i in range(0, len(_doc), 200)]
        _vectors = [{"texto": ch, "embedding": _embeddings.embed_query(ch)} for ch in _chunks]

        def _similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        def _get_context(query: str) -> str:
            eq = _embeddings.embed_query(query)
            ranked = sorted(
                [(s, t) for t in _vectors if (s := _similarity(eq, t["embedding"]))],
                reverse=True,
            )
            return ranked[0][1]["texto"] if ranked else ""

        def _format_currency(v: int) -> str:
            return f"${v:,} CLP"

        def _find_keyword(text: str, candidates: list) -> str | None:
            upper = text.upper()
            for c in candidates:
                if c.upper() in upper:
                    return c
            return None

        import re

        @tool
        def revisar_requisitos_teoricos_notebooks(consulta: str) -> str:
            """Usa esta herramienta cuando el usuario pida recomendaciones generales sobre notebooks."""
            return _get_context(consulta)

        @tool
        def consultar_producto_avanzado(termino_busqueda: str) -> str:
            """Busca un producto en la base de datos usando su SKU o palabras clave de su nombre."""
            query = termino_busqueda.strip()
            if not query:
                return "Por favor, proporciona un término de búsqueda válido."

            sku, producto = query_product_db(query)

            if not producto or producto.get("total_stock", 0) == 0:
                lines = []
                if not producto:
                    lines.append(f"El producto exacto '{termino_busqueda}' no figura en el catálogo.")
                else:
                    lines.append(f"'{producto['nombre']}' ({sku}) se encuentra agotado.")
                lines.append("\nALTERNATIVAS DISPONIBLES:")
                all_skus = get_all_skus()
                es_cpu = any(w in query.lower() for w in ["ryzen", "intel", "cpu", "procesador"])
                es_gpu = any(w in query.lower() for w in ["rtx", "gpu", "video", "nvidia", "amd"])
                alts = []
                for s in all_skus:
                    _, pi = query_product_db(s)
                    if pi and pi.get("total_stock", 0) > 0:
                        if es_cpu and "CPU" in s:
                            alts.append((s, pi))
                        elif es_gpu and "GPU" in s:
                            alts.append((s, pi))
                    if len(alts) >= 3:
                        break
                if not alts:
                    for s in all_skus[:4]:
                        _, pi = query_product_db(s)
                        if pi and pi.get("total_stock", 0) > 0:
                            alts.append((s, pi))
                for i, (s, info) in enumerate(alts, 1):
                    lines.append(f"{i}. **{s}** - {info['nombre']} | {_format_currency(info['precio_lista'])}")
                return "\n".join(lines)

            pl = producto["precio_lista"]
            desc = producto["descuento_efectivo"]
            pe = pl - int(pl * desc)
            lines = [
                f"DATOS DEL CATÁLOGO ({sku}):",
                f"- Componente: {producto['nombre']}",
                f"- Precio Lista: {_format_currency(pl)}",
                f"- Precio Efectivo: {_format_currency(pe)} ({int(desc * 100)}% descuento)",
                f"- Stock Consolidado: {producto['total_stock']} unidades.",
            ]
            for item in producto.get("inventory", []):
                lines.append(f"  - [{item['branch_codigo']}] {item['branch_nombre']}: {item['cantidad']} uds.")
            return "\n".join(lines)

        @tool
        def confirmar_compra_por_correo(orden_texto: str) -> str:
            """Procesa la compra real y descuenta stock."""
            texto = orden_texto.strip()
            candidates = [b["codigo"] for b in list_branches()]
            sku_candidates = get_all_skus()
            branch_code = _find_keyword(texto, candidates)
            sku = _find_keyword(texto, sku_candidates)
            cm = re.search(r"(\d+)", texto)
            cantidad = int(cm.group(1)) if cm else 1
            recipient = os.getenv("GMAIL_REMITENTE", "cliente@example.com")
            if not branch_code or not sku:
                return "No pude procesar. Indica sucursal (ej: SCL-CENTRO) y SKU."
            try:
                oid = create_order_by_branch_code(branch_code, [(sku, cantidad)], "Cliente Web")
                info = get_order_details(oid)
            except ValueError as e:
                return f"Error: {e}"
            total = _format_currency(info["order"]["total"])
            return (
                f"VENTA CONFIRMADA - Orden #{info['order']['id']}\n"
                f"Retiro: {branch_code}\n"
                f"Total: {total}\n"
                f"Factura enviada a: {recipient}"
            )

        tools = [revisar_requisitos_teoricos_notebooks, consultar_producto_avanzado, confirmar_compra_por_correo]

        prompt = """Eres el asesor virtual de PC Factory Chile. Tu objetivo es vender.
Usa tus herramientas para buscar productos, sugerir alternativas y procesar compras.
Si un producto no está disponible, ofrece alternativas reales del catálogo.
Si el cliente acepta una alternativa, llama confirmar_compra_por_correo con el SKU y la sucursal.
Formatea precios en pesos chilenos ($999,990 CLP)."""

        _app_agent = create_react_agent(_chat_llm, tools, prompt=prompt)

    import sqlite3
    from langchain_core.messages import HumanMessage, AIMessage

    DB_PATH = str(ROOT / "Scripts" / "catalogo_pc_factory.db")

    class SQLiteChatMessageHistory:
        def __init__(self, session_id: str):
            self.session_id = session_id
            conn = self._connect()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS chat_history ("
                "  session_id TEXT, message_idx INTEGER, role TEXT, content TEXT, "
                "  PRIMARY KEY (session_id, message_idx)"
                ")"
            )
            conn.close()

        def _connect(self):
            return sqlite3.connect(DB_PATH)

        @property
        def messages(self):
            conn = self._connect()
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT role, content FROM chat_history WHERE session_id=? ORDER BY message_idx",
                (self.session_id,),
            ).fetchall()
            conn.close()
            result = []
            for r in rows:
                if r["role"] == "human":
                    result.append(HumanMessage(content=r["content"]))
                elif r["role"] == "ai":
                    result.append(AIMessage(content=r["content"]))
            return result

        def add_user_message(self, text: str):
            conn = self._connect()
            max_idx = conn.execute(
                "SELECT COALESCE(MAX(message_idx), -1) AS m FROM chat_history WHERE session_id=?",
                (self.session_id,),
            ).fetchone()[0]
            conn.execute(
                "INSERT INTO chat_history (session_id, message_idx, role, content) VALUES (?, ?, ?, ?)",
                (self.session_id, max_idx + 1, "human", text),
            )
            conn.commit()
            conn.close()

        def add_ai_message(self, text: str):
            conn = self._connect()
            max_idx = conn.execute(
                "SELECT COALESCE(MAX(message_idx), -1) AS m FROM chat_history WHERE session_id=?",
                (self.session_id,),
            ).fetchone()[0]
            conn.execute(
                "INSERT INTO chat_history (session_id, message_idx, role, content) VALUES (?, ?, ?, ?)",
                (self.session_id, max_idx + 1, "ai", text),
            )
            conn.commit()
            conn.close()

        def clear(self):
            conn = self._connect()
            conn.execute("DELETE FROM chat_history WHERE session_id=?", (self.session_id,))
            conn.commit()
            conn.close()

    def _get_history(sid: str):
        return SQLiteChatMessageHistory(sid)

except ImportError:
    _HAS_LLM = False


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    import time

    sanitized_msg, injection_warning = sanitize_chat_message(req.message)
    if injection_warning:
        log_error(
            error_type="injection_attempt",
            message=injection_warning,
            endpoint="/api/chat",
            user_id=req.session_id,
        )
        return ChatResponse(
            reply="Lo siento, no puedo procesar mensajes con código malicioso.",
            session_id=req.session_id,
        )

    rate_key = f"chat:{req.session_id}"
    if not ai_rate_limiter.is_allowed(rate_key):
        log_error(
            error_type="rate_limit",
            message="Rate limit excedido para chat",
            endpoint="/api/chat",
            user_id=req.session_id,
        )
        return ChatResponse(
            reply="Has excedido el límite de mensajes. Espera un momento antes de continuar.",
            session_id=req.session_id,
        )

    cached = response_cache.get(sanitized_msg, req.session_id)
    if cached:
        metrics.record_cache(hit=True)
        return ChatResponse(reply=cached, session_id=req.session_id)

    metrics.record_cache(hit=False)
    start_time = time.perf_counter()
    trace_id = f"chat_{int(time.time())}"

    if not _HAS_LLM or _app_agent is None:
        duration = (time.perf_counter() - start_time) * 1000
        response = _fallback_chat(sanitized_msg, req.session_id)
        log_chat_interaction(
            user_id=req.session_id,
            prompt=sanitized_msg,
            response=response.reply,
            response_time_ms=duration,
            tokens=0,
            status="success",
            endpoint="/api/chat",
        )
        metrics.record_request("/api/chat", duration, req.session_id)
        return response

    history = _get_history(req.session_id)
    history.add_user_message(sanitized_msg)
    try:
        span_llm = tracer.start_span("agent_invoke", trace_id)
        with span_llm:
            result = _app_agent.invoke(
                {"messages": history.messages},
                {"configurable": {"thread_id": req.session_id}},
            )
        reply = result["messages"][-1].content
        history.add_ai_message(reply)
        tokens_used = 0
        try:
            if hasattr(result, "__getitem__") and "token_usage" in str(type(result)):
                usage = result.get("token_usage", {})
                tokens_used = usage.get("total_tokens", 0) if isinstance(usage, dict) else 0
        except Exception:
            pass

        duration = (time.perf_counter() - start_time) * 1000
        metrics.record_ai_interaction(duration, tokens_used, success=True)
        response_cache.set(sanitized_msg, reply, req.session_id)

        log_chat_interaction(
            user_id=req.session_id,
            prompt=sanitized_msg,
            response=reply,
            response_time_ms=duration,
            tokens=tokens_used,
            status="success",
            endpoint="/api/chat",
        )
        metrics.record_request("/api/chat", duration, req.session_id)
        return ChatResponse(reply=reply, session_id=req.session_id)

    except Exception as e:
        duration = (time.perf_counter() - start_time) * 1000
        error_msg = str(e)
        metrics.record_ai_interaction(duration, 0, success=False)
        metrics.record_error(type(e).__name__)
        log_chat_interaction(
            user_id=req.session_id,
            prompt=sanitized_msg,
            response="",
            response_time_ms=duration,
            tokens=0,
            status="error",
            error=error_msg,
            endpoint="/api/chat",
        )
        log_error(
            error_type=type(e).__name__,
            message=error_msg,
            endpoint="/api/chat",
            user_id=req.session_id,
        )
        return ChatResponse(reply=f"Error: {error_msg}", session_id=req.session_id)


@router.post("/chat/reset")
async def reset_chat(session_id: str = "default"):
    import sqlite3
    db_path = ROOT / "Scripts" / "catalogo_pc_factory.db"
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("DELETE FROM chat_history WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM session_data WHERE session_id=?", (session_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass
    response_cache.invalidate(session_id)
    return {"status": "reset"}


BUILD_STRATEGIES = [
    {"name": "Máximo Rendimiento", "desc": True,  "gpu_first": False},
    {"name": "Enfoque GPU",       "desc": True,  "gpu_first": True},
    {"name": "Balance calidad",   "desc": False, "gpu_first": False},
    {"name": "Enfoque CPU",       "desc": False, "gpu_first": True},
]


def _fallback_chat(message: str, session_id: str) -> ChatResponse:
    import sqlite3
    db_path = ROOT / "Scripts" / "catalogo_pc_factory.db"
    msg = message.lower().strip()

    reply = ""
    try:
        with sqlite3.connect(str(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute(
                "CREATE TABLE IF NOT EXISTS session_data ("
                "  session_id TEXT, key TEXT, value TEXT, "
                "  PRIMARY KEY (session_id, key)"
                ")"
            )

            def _sget(key: str, default=None):
                row = conn.execute(
                    "SELECT value FROM session_data WHERE session_id=? AND key=?",
                    (session_id, key),
                ).fetchone()
                if row is None:
                    return default
                val: str = row["value"]
                if default is False or default is True:
                    return val == "true"
                return val

            def _sset(key: str, value):
                conn.execute(
                    "INSERT OR REPLACE INTO session_data (session_id, key, value) VALUES (?, ?, ?)",
                    (session_id, key, str(value)),
                )

            def _sdel(key: str):
                conn.execute(
                    "DELETE FROM session_data WHERE session_id=? AND key=?",
                    (session_id, key),
                )

            def _sclear():
                conn.execute(
                    "DELETE FROM session_data WHERE session_id=?",
                    (session_id,),
                )

            def _has_any() -> bool:
                row = conn.execute(
                    "SELECT 1 FROM session_data WHERE session_id=? LIMIT 1",
                    (session_id,),
                ).fetchone()
                return row is not None

            CATEGORY_KEYWORDS = {
                1: ["procesador", "cpu"],
                2: ["gpu", "video", "rtx", "tarjeta grafica", "grafica", "nvidia", "radeon"],
                3: ["ram", "memoria", "ddr4", "ddr5"],
                4: ["almacenamiento", "disco", "ssd", "hdd", "nvm"],
                5: ["placa madre", "placa", "motherboard", "mother"],
                6: ["accesorio", "cable", "hdmi", "adaptador"],
                7: ["monitor", "pantalla"],
                8: ["periferico", "teclado", "mouse", "raton", "audifono", "auricular", "g203", "g502", "g413", "k552"],
                9: ["fuente", "psu", "power supply"],
                10: ["gabinete", "case", "chasis"],
                11: ["refrigeracion", "cooler", "ventilador", "liquida"],
            }

            CATEGORY_NAMES = {
                1: "Procesadores",
                2: "Tarjetas de Video",
                3: "Memorias RAM",
                4: "Almacenamiento",
                5: "Placas Madre",
                6: "Accesorios",
                7: "Monitores",
                8: "Periféricos",
                9: "Fuentes de Poder",
                10: "Gabinetes",
                11: "Refrigeración",
            }

            def _match_category(text: str) -> int | None:
                for cid, keywords in CATEGORY_KEYWORDS.items():
                    for kw in keywords:
                        if kw in text:
                            return cid
                return None

            def _format_product_stock(r) -> str:
                inv_rows = conn.execute(
                    "SELECT b.codigo, i.cantidad FROM inventory i JOIN branches b ON i.branch_id = b.id WHERE i.sku = ? AND i.cantidad > 0 ORDER BY i.cantidad DESC",
                    (r["sku"],),
                ).fetchall()
                stock_total = sum(i["cantidad"] for i in inv_rows)
                stock_str = f"Stock: {stock_total} uds."
                if inv_rows:
                    branches_detail = ", ".join(f"{i['codigo']}: {i['cantidad']}" for i in inv_rows[:3])
                    stock_str += f" ({branches_detail}{'...' if len(inv_rows) > 3 else ''})"
                return stock_str

            def _get_effective_price(sku: str) -> int:
                row = conn.execute("SELECT precio_lista, descuento_efectivo FROM products WHERE sku=?", (sku,)).fetchone()
                if row:
                    return row["precio_lista"] - int(row["precio_lista"] * row["descuento_efectivo"])
                return 0

            def _list_category(cat_id: int, exclude_skus: set = None, desc: bool = True) -> list[dict]:
                exclude_skus = exclude_skus or set()
                order = "DESC" if desc else "ASC"
                rows = conn.execute(
                    f"SELECT sku, nombre, precio_lista, descuento_efectivo FROM products WHERE category_id=? ORDER BY precio_lista {order}",
                    (cat_id,),
                ).fetchall()
                result = []
                for r in rows:
                    if r["sku"] not in exclude_skus:
                        ep = _get_effective_price(r["sku"])
                        result.append({**dict(r), "precio_efectivo": ep})
                return result

            PLATFORMS = [
                {
                    "name": "AMD AM4",
                    "cpus": ["CPU-AMD-R5-5600X", "CPU-AMD-R7-5700X"],
                    "mbs": ["MB-MSI-B550M"],
                    "ram_type": "DDR4",
                },
                {
                    "name": "AMD AM5",
                    "cpus": ["CPU-AMD-R7-7800X3D"],
                    "mbs": ["MB-GIGABYTE-B650"],
                    "ram_type": "DDR5",
                },
                {
                    "name": "Intel LGA1700",
                    "cpus": ["CPU-INTEL-I3-12100F", "CPU-INTEL-I5-12400F", "CPU-INTEL-I5-14600K", "CPU-INTEL-I7-14700K"],
                    "mbs": ["MB-ASUS-H610M", "MB-ASUS-B760M"],
                    "ram_type": "DDR4",
                },
            ]

            def _build_pc_by_budget(budget: int, conn, strategy: dict) -> str:
                CATEGORY_MAP = {"CPU": 1, "GPU": 2, "RAM": 3, "Storage": 4, "Motherboard": 5, "PSU": 9, "Case": 10, "Cooler": 11}
                COMPONENT_ORDER = ["GPU", "CPU", "Motherboard", "RAM", "Storage", "PSU", "Case", "Cooler"] if strategy["gpu_first"] else ["CPU", "Motherboard", "RAM", "GPU", "Storage", "PSU", "Case", "Cooler"]
                LABELS = {"CPU": "CPU", "Motherboard": "Placa Madre", "RAM": "RAM", "GPU": "Tarjeta de Video", "Storage": "Almacenamiento", "PSU": "Fuente de Poder", "Case": "Gabinete", "Cooler": "Refrigeración"}
                desc = strategy["desc"]

                best_build = None
                best_total = 0

                for platform in PLATFORMS:
                    used_skus = set()
                    build = {}
                    remaining = budget
                    platform_valid = True

                    def _pick(items: list, remaining: int, desc: bool) -> tuple | None:
                        items = sorted(items, key=lambda x: x[1], reverse=desc)
                        for sku, ep in items:
                            if ep <= remaining:
                                return (sku, ep)
                        return items[-1] if items else None

                    for comp in COMPONENT_ORDER:
                        if comp == "Motherboard":
                            mbs = [(sku, _get_effective_price(sku)) for sku in platform["mbs"] if sku not in used_skus]
                            chosen = _pick(mbs, remaining, desc)
                            if not chosen:
                                platform_valid = False
                                break
                            used_skus.add(chosen[0])
                            build[comp] = {"sku": chosen[0], "precio": chosen[1]}
                            remaining -= chosen[1]

                        elif comp == "CPU":
                            cpus = [(sku, _get_effective_price(sku)) for sku in platform["cpus"] if sku not in used_skus]
                            chosen = _pick(cpus, remaining, desc)
                            if not chosen:
                                platform_valid = False
                                break
                            used_skus.add(chosen[0])
                            build[comp] = {"sku": chosen[0], "precio": chosen[1]}
                            remaining -= chosen[1]

                        elif comp == "RAM":
                            ram_type = platform["ram_type"]
                            ram_rows = conn.execute(
                                "SELECT sku, nombre, precio_lista, descuento_efectivo FROM products WHERE category_id=3 ORDER BY precio_lista ASC"
                            ).fetchall()
                            rams = []
                            for r in ram_rows:
                                if r["sku"] not in used_skus:
                                    name_lower = r["nombre"].lower()
                                    if (ram_type == "DDR4" and "ddr4" in name_lower) or (ram_type == "DDR5" and "ddr5" in name_lower):
                                        rams.append((r["sku"], _get_effective_price(r["sku"])))
                            chosen = _pick(rams, remaining, desc)
                            if not chosen:
                                platform_valid = False
                                break
                            used_skus.add(chosen[0])
                            build[comp] = {"sku": chosen[0], "precio": chosen[1]}
                            remaining -= chosen[1]

                        else:
                            cat_id = CATEGORY_MAP[comp]
                            avail = _list_category(cat_id, used_skus, desc)
                            chosen = None
                            if not strategy["gpu_first"] and desc:
                                chosen = next((a for a in avail if a["precio_efectivo"] <= remaining), avail[-1] if avail else None)
                            else:
                                chosen = next((a for a in avail if a["precio_efectivo"] <= remaining), avail[-1] if avail else None)
                            if not chosen:
                                if comp in ["Cooler", "Case"]:
                                    continue
                                platform_valid = False
                                break
                            used_skus.add(chosen["sku"])
                            build[comp] = {"sku": chosen["sku"], "precio": chosen["precio_efectivo"]}
                            remaining -= chosen["precio_efectivo"]

                    if platform_valid:
                        total = budget - remaining
                        if total > best_total:
                            best_total = total
                            best_build = build
                            best_build["platform"] = platform["name"]
                            best_build["total"] = total
                            best_build["remaining"] = remaining

                if not best_build:
                    return (
                        f"Con un presupuesto de ${budget:,} CLP no fue posible armar una PC completa. "
                        "Intenta con un monto mayor o pregunta por componentes individuales."
                    )

                lines = [f"**PC Armada - {best_build['platform']} ({strategy['name']})**\n"]
                lines.append(f"Presupuesto: ${budget:,} CLP")
                lines.append(f"Total: ${best_build['total']:,} CLP")
                if best_build['remaining'] > 0:
                    lines.append(f"Sobrante: ${best_build['remaining']:,} CLP")
                lines.append("")
                for comp in ["CPU", "Motherboard", "RAM", "GPU", "Storage", "PSU", "Case", "Cooler"]:
                    if comp in best_build:
                        info = best_build[comp]
                        name_row = conn.execute("SELECT nombre FROM products WHERE sku=?", (info["sku"],)).fetchone()
                        name = name_row["nombre"] if name_row else info["sku"]
                        lines.append(f"• **{LABELS[comp]}:** {name} - ${info['precio']:,} CLP")
                lines.append("")
                lines.append("💡 _Escribe **otra opción** para ver una configuración alternativa._")
                lines.append("📧 ¿Quieres que envíe estos detalles a tu correo? Responde 'sí' o 'no'.")

                _sset("last_details", "\n".join(lines))
                _sset("last_budget", str(budget))
                return "\n".join(lines)

            if any(p in msg for p in ["envío al día siguiente", "next day shipping", "envio rapido", "despacho"]):
                reply = (
                    "**Información de Despacho PC Factory**\n\n"
                    "• **Despacho a domicilio:** 3-5 días hábiles ($4,990 CLP)\n"
                    "• **Retiro en tienda:** Gratis, 24 hrs después de la compra\n"
                    "• **Envío Express:** Antes de las 13:00 hrs, llega al día siguiente ($9,990 CLP)\n"
                    "• **Envío Gratis:** En compras sobre $100,000 CLP\n\n"
                    "¿Quieres verificar disponibilidad en alguna sucursal?"
                )
                return ChatResponse(reply=reply, session_id=session_id)

            if any(p in msg for p in ["verificar compatibilidad", "check compatibility", "compatible"]):
                reply = (
                    "**Verificador de Compatibilidad**\n\n"
                    "Puedo ayudarte a verificar si dos componentes son compatibles.\n"
                    "Dime qué componentes quieres revisar, por ejemplo:\n"
                    "• '¿El Ryzen 7 7800X3D es compatible con la B650?'\n"
                    "• '¿La RTX 4080 Super funciona con fuente de 750W?'\n"
                    "• '¿Qué RAM es compatible con mi placa madre?'\n\n"
                    "También puedes visitar la página del producto y usar el chat integrado."
                )
                return ChatResponse(reply=reply, session_id=session_id)

            greeting_words = ["hola", "buenas", "buen dia", "buena tarde", "buena noche", "saludos", "hey", "que tal"]
            if any(g in msg for g in greeting_words) and len(msg) < 40:
                _sclear()
                reply = (
                    "¡Hola! Soy TechAssist de PC Factory.\n\n"
                    "Puedo ayudarte con:\n"
                    "• Buscar productos por categoría (procesadores, GPUs, RAM, etc.)\n"
                    "• Consultar stock disponible\n"
                    "• Ver productos en oferta\n"
                    "• Recomendaciones de armado\n\n"
                    "¿Qué estás buscando el día de hoy?"
                )
                return ChatResponse(reply=reply, session_id=session_id)

            wants_cheapest = any(p in msg for p in ["mas barato", "más barato", "más económico", "mas economico", "menor precio", "menos precio", "mas economico"])
            wants_expensive = any(p in msg for p in ["mas caro", "más caro", "mayor precio", "más costoso", "mas costoso", "mas caro"])
            wants_sin_descuento = "sin descuento" in msg or "precio lista" in msg or "precio normal" in msg or "sin dcto" in msg
            wants_con_descuento = "con descuento" in msg or "en oferta" in msg or "con dcto" in msg

            if wants_cheapest or wants_expensive:
                cat_id = _match_category(msg)
                if cat_id is None:
                    cat_id = _sget("last_category")

                price_col = "precio_lista" if wants_sin_descuento else "(precio_lista - CAST(precio_lista * descuento_efectivo AS INT))"
                order = "ASC" if wants_cheapest else "DESC"
                label = "más barato" if wants_cheapest else "más caro"
                filter_clause = "AND descuento_efectivo = 0" if wants_sin_descuento else ""
                filter_clause += " AND descuento_efectivo > 0" if wants_con_descuento else ""

                if cat_id:
                    query = f"""
                        SELECT sku, nombre, precio_lista, descuento_efectivo,
                               (precio_lista - CAST(precio_lista * descuento_efectivo AS INT)) AS precio_final
                        FROM products
                        WHERE category_id = ? {filter_clause}
                        ORDER BY precio_final {order}
                        LIMIT 1
                    """
                    row = conn.execute(query, (cat_id,)).fetchone()
                    cat_name = CATEGORY_NAMES.get(cat_id, "Productos")
                else:
                    query = f"""
                        SELECT sku, nombre, precio_lista, descuento_efectivo,
                               (precio_lista - CAST(precio_lista * descuento_efectivo AS INT)) AS precio_final
                        FROM products
                        WHERE 1=1 {filter_clause}
                        ORDER BY precio_final {order}
                        LIMIT 1
                    """
                    row = conn.execute(query).fetchone()
                    cat_name = "Productos"

                if row:
                    desc = row["descuento_efectivo"]
                    price_str = f"${row['precio_lista']:,} CLP"
                    if desc > 0:
                        pe = row["precio_lista"] - int(row["precio_lista"] * desc)
                        price_str = f"~~${row['precio_lista']:,}~~ **${pe:,} CLP** ({int(desc*100)}% dcto)"
                    stock_info = _format_product_stock(row)
                    desc_label = " (sin descuento)" if wants_sin_descuento else (" (con descuento)" if wants_con_descuento else "")
                    reply = (
                        f"**{cat_name}: El {label}{desc_label}**\n\n"
                        f"- {row['nombre']} - {price_str} | {stock_info}"
                    )
                else:
                    reply = f"No encontré productos que coincidan con tu búsqueda."
                _sset("last_details", reply)
                reply += "\n\n📧 ¿Quieres que envíe estos detalles a tu correo? Responde 'sí' o 'no'."
                return ChatResponse(reply=reply, session_id=session_id)

            if "oferta" in msg or "descuento" in msg or "promo" in msg:
                rows = conn.execute(
                    "SELECT sku, nombre, precio_lista, descuento_efectivo FROM products WHERE descuento_efectivo > 0 ORDER BY descuento_efectivo DESC"
                ).fetchall()
                if rows:
                    lines = ["**Productos en Oferta:**\n"]
                    for r in rows:
                        desc = int(r["descuento_efectivo"] * 100)
                        pe = r["precio_lista"] - int(r["precio_lista"] * r["descuento_efectivo"])
                        lines.append(
                            f"- {r['nombre']}  ~~${r['precio_lista']:,}~~  **${pe:,} CLP** ({desc}% dcto)"
                        )
                    reply = "\n".join(lines)
                else:
                    reply = "Actualmente no hay productos con descuento activo."
                _sset("last_details", reply)
                reply += "\n\n📧 ¿Quieres que envíe estos detalles a tu correo? Responde 'sí' o 'no'."
                return ChatResponse(reply=reply, session_id=session_id)

            if "barato" in msg or "mejor precio" in msg:
                row = conn.execute("""
                    SELECT sku, nombre, precio_lista, descuento_efectivo,
                           (precio_lista - CAST(precio_lista * descuento_efectivo AS INT)) AS precio_final
                    FROM products ORDER BY precio_final ASC LIMIT 1
                """).fetchone()
                desc = row["descuento_efectivo"]
                price_str = f"${row['precio_lista']:,} CLP"
                if desc > 0:
                    pe = row["precio_lista"] - int(row["precio_lista"] * desc)
                    price_str = f"~~${row['precio_lista']:,}~~ **${pe:,} CLP** ({int(desc*100)}% dcto)"
                stock_info = _format_product_stock(row)
                reply = (
                    f"**Producto más barato del catálogo:**\n\n"
                    f"- {row['nombre']} - {price_str} | {stock_info}"
                )
                _sset("last_details", reply)
                reply += "\n\n📧 ¿Quieres que envíe estos detalles a tu correo? Responde 'sí' o 'no'."
                return ChatResponse(reply=reply, session_id=session_id)

            import re
            pure_number = re.match(r"^\d{4,}$", msg.replace(".", "").replace(" ", ""))
            wants_budget = any(p in msg for p in ["presupuesto", "armar", "arma una pc", "arma un pc", "armame", "build", "configuracion", "configuración", "arreglo", "nuevo armado", "nueva pc"])
            if wants_budget or "presupuesto" in msg or "presupuesto de" in msg or pure_number:
                budget = None
                raw_msg = msg.replace(",", "")
                millones = re.search(r"(\d+(?:\.\d+)?)\s*(?:millones|millón)", raw_msg)
                miles = re.search(r"(\d+(?:\.\d+)?)\s*(?:mil)", raw_msg)
                if millones:
                    budget = int(float(millones.group(1).replace(".", "")) * 1000000)
                elif miles:
                    budget = int(float(miles.group(1).replace(".", "")) * 1000)
                else:
                    match = re.search(r"(\d[\d.]*)", raw_msg)
                    if match:
                        raw = match.group(1).replace(".", "")
                        try:
                            budget = int(raw)
                        except ValueError:
                            pass

                if budget:
                    last_budget_key = f"build_count_{budget}"
                    build_count = int(_sget(last_budget_key, "0"))
                    strategy = BUILD_STRATEGIES[build_count % len(BUILD_STRATEGIES)]
                    _sset(last_budget_key, str(build_count + 1))
                    reply = _build_pc_by_budget(budget, conn, strategy)
                    return ChatResponse(reply=reply, session_id=session_id)
                else:
                    reply = "¿Cuál es tu presupuesto? Dime un monto como '300000' o '500 mil' y armaré una PC compatible."
                    return ChatResponse(reply=reply, session_id=session_id)

            # "otra opción" → request next build strategy
            if any(p in msg for p in ["otra opcion", "otra opción", "alternativa", "variante", "diferente", "otra configuracion", "otra configuración"]):
                last_budget = _sget("last_budget")
                if last_budget:
                    prev_budget = int(last_budget)
                    last_budget_key = f"build_count_{prev_budget}"
                    build_count = int(_sget(last_budget_key, "0"))
                    strategy = BUILD_STRATEGIES[build_count % len(BUILD_STRATEGIES)]
                    _sset(last_budget_key, str(build_count + 1))
                    reply = _build_pc_by_budget(prev_budget, conn, strategy)
                    return ChatResponse(reply=reply, session_id=session_id)

            last_details = _sget("last_details")
            if last_details:
                email_already_sent = _sget("email_sent", False)
                want_email = any(p in msg for p in ["sí", "si", "3", "enviar", "correo", "email", "envía", "manda", "detalles", "comprobante"])
                dont_email = any(p in msg for p in ["no", "no gracias", "no quiero", "nope", "2"])
                if want_email and not dont_email:
                    if email_already_sent:
                        reply = (
                            "⚠️ **Ya se enviaron los detalles a tu correo.**\n\n"
                            "Por seguridad, solo puedes enviar los detalles una vez por consulta. "
                            "Si necesitas otra copia, vuelve a realizar tu consulta y solicita el envío nuevamente."
                        )
                        _sdel("last_details")
                        return ChatResponse(reply=reply, session_id=session_id)
                    from backend.services.email_service import send_text_email, is_email_configured
                    if not is_email_configured():
                        reply = "El envío de correos no está configurado. Revisa el archivo .env con las credenciales SMTP."
                        return ChatResponse(reply=reply, session_id=session_id)
                    email_body = (
                        "¡Hola!\n\n"
                        "Gracias por consultar en PC Factory. Aquí están los detalles que solicitaste:\n\n"
                        + ("─" * 40) + "\n"
                        + last_details
                        + "\n" + ("─" * 40) + "\n\n"
                        "Si tienes más dudas, responde este correo o vuelve a escribirme en la web.\n\n"
                        "Saludos,\nTechAssist — PC Factory Chile"
                    )
                    try:
                        sent = send_text_email(
                            to_email=os.getenv("SMTP_FROM", "compus.factoryvd@gmail.com"),
                            subject="PC Factory - Detalles de tu consulta",
                            body=email_body,
                        )
                    except Exception as e:
                        sent = False
                    if sent:
                        _sset("email_sent", True)
                        reply = (
                            "✅ **Correo enviado con éxito**\n\n"
                            "Los detalles han sido enviados a tu bandeja de entrada. "
                            "Si no lo ves en los próximos minutos, revisa tu carpeta de spam.\n\n"
                            "¿Necesitas algo más?"
                        )
                    else:
                        reply = "No se pudo enviar el correo. Intenta más tarde o verifica la configuración SMTP."
                    _sdel("last_details")
                    return ChatResponse(reply=reply, session_id=session_id)
                if dont_email:
                    _sdel("last_details")
                    reply = "Entendido. ¿Necesitas algo más?"
                    return ChatResponse(reply=reply, session_id=session_id)

            wants_stock = "stock" in msg
            wants_stock_detail = "stock" in msg and ("de " in msg or len(msg) < 30)

            if wants_stock:
                cat_id = _match_category(msg.replace("stock", ""))
                if cat_id is None and "stock" in msg:
                    cat_id = _match_category(msg)

                if wants_stock_detail and cat_id:
                    rows = conn.execute(
                        "SELECT sku, nombre, precio_lista, descuento_efectivo FROM products WHERE category_id=? ORDER BY precio_lista",
                        (cat_id,),
                    ).fetchall()
                    cat_name = CATEGORY_NAMES[cat_id]
                    if rows:
                        lines = [f"**Stock de {cat_name}:**\n"]
                        for r in rows:
                            stock_info = _format_product_stock(r)
                            lines.append(f"- {r['nombre']} -- {stock_info}")
                        reply = "\n".join(lines)
                        _sset("last_category", str(cat_id))
                        _sset("last_details", reply)
                        reply += "\n\n📧 ¿Quieres que envíe estos detalles a tu correo? Responde 'sí' o 'no'."
                        return ChatResponse(reply=reply, session_id=session_id)

                if wants_stock and not wants_stock_detail and _sget("last_category") is not None:
                    cat_id = int(_sget("last_category"))
                    rows = conn.execute(
                        "SELECT sku, nombre, precio_lista, descuento_efectivo FROM products WHERE category_id=? ORDER BY precio_lista",
                        (cat_id,),
                    ).fetchall()
                    cat_name = CATEGORY_NAMES[cat_id]
                    if rows:
                        lines = [f"**Stock de {cat_name}:**\n"]
                        for r in rows:
                            stock_info = _format_product_stock(r)
                            lines.append(f"- {r['nombre']} -- {stock_info}")
                        reply = "\n".join(lines)
                        _sset("last_details", reply)
                        reply += "\n\n📧 ¿Quieres que envíe estos detalles a tu correo? Responde 'sí' o 'no'."
                        return ChatResponse(reply=reply, session_id=session_id)

                total = conn.execute("SELECT SUM(cantidad) AS s FROM inventory").fetchone()["s"]
                products_count = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
                branches = conn.execute("SELECT COUNT(*) AS c FROM branches").fetchone()["c"]
                low_stock = conn.execute(
                    "SELECT COUNT(*) AS c FROM (SELECT sku FROM inventory GROUP BY sku HAVING SUM(cantidad) < 5)"
                ).fetchone()["c"]
                reply = (
                    f"**Resumen de Stock PC Factory**\n\n"
                    f"• Total productos: {products_count}\n"
                    f"• Unidades en inventario: {total:,}\n"
                    f"• Sucursales activas: {branches}\n"
                    f"• Productos con stock bajo (<5 uds): {low_stock}\n\n"
                    f"Para ver stock por producto, pregúntame por una categoría o producto específico."
                )
                _sset("last_details", reply)
                reply += "\n\n📧 ¿Quieres que envíe estos detalles a tu correo? Responde 'sí' o 'no'."
                return ChatResponse(reply=reply, session_id=session_id)

            if "todo" in msg or "categoria" in msg or "list" in msg or "categoría" in msg:
                lines = ["**Categorias Disponibles:**\n"]
                for cid, cname in CATEGORY_NAMES.items():
                    count = conn.execute(
                        "SELECT COUNT(*) AS c FROM products WHERE category_id=?", (cid,)
                    ).fetchone()["c"]
                    lines.append(f"• **{cname}** ({count} productos)")
                lines.append("\n_Pregúntame por cualquier categoría para ver sus productos._")
                reply = "\n".join(lines)
                _sset("last_details", reply)
                reply += "\n\n📧 ¿Quieres que envíe estos detalles a tu correo? Responde 'sí' o 'no'."
                return ChatResponse(reply=reply, session_id=session_id)

            matched_category = _match_category(msg)
            if matched_category:
                _sset("last_category", str(matched_category))
                rows = conn.execute(
                    "SELECT sku, nombre, precio_lista, descuento_efectivo FROM products WHERE category_id=? ORDER BY precio_lista",
                    (matched_category,),
                ).fetchall()
                cat_name = CATEGORY_NAMES[matched_category]
                if rows:
                    lines = [f"**{cat_name} Disponibles:**\n"]
                    for r in rows:
                        desc = r["descuento_efectivo"]
                        price_str = f"${r['precio_lista']:,} CLP"
                        if desc > 0:
                            pe = r["precio_lista"] - int(r["precio_lista"] * desc)
                            price_str = f"~~${r['precio_lista']:,}~~ **${pe:,} CLP**"
                        stock_info = _format_product_stock(r)
                        lines.append(f"- {r['nombre']} - {price_str} | {stock_info}")
                    lines.append("\n_Pregunta por 'stock [categoría]' para ver detalle por sucursal._")
                    reply = "\n".join(lines)

            if not reply:
                rows = conn.execute(
                    "SELECT sku, nombre, precio_lista, descuento_efectivo FROM products WHERE LOWER(nombre) LIKE ? LIMIT 8",
                    (f"%{msg}%",),
                ).fetchall()
                if rows:
                    lines = ["**Resultados de búsqueda:**\n"]
                    for r in rows:
                        price_str = f"${r['precio_lista']:,} CLP"
                        if r["descuento_efectivo"] > 0:
                            pe = r["precio_lista"] - int(r["precio_lista"] * r["descuento_efectivo"])
                            price_str = f"~~${r['precio_lista']:,}~~ **${pe:,} CLP**"
                        stock_info = _format_product_stock(r)
                        lines.append(f"- {r['nombre']} - {price_str} | {stock_info}")
                    if len(rows) == 8:
                        lines.append("\n_Mostrando los primeros 8 resultados. Sé más específico._")
                    reply = "\n".join(lines)

            if reply and "¿Quieres que envíe" not in reply:
                _sset("last_details", reply)
                reply += "\n\n📧 ¿Quieres que envíe estos detalles a tu correo? Responde 'sí' o 'no'."

            if not reply:
                if _has_any():
                    _sclear()
                reply = (
                    "Hola, soy TechAssist de PC Factory.\n\n"
                    "Puedes preguntarme por:\n"
                    "• Categorías: procesadores, GPUs, RAM, almacenamiento, placas madre, etc.\n"
                    "• Ofertas y descuentos\n"
                    "• Stock disponible\n"
                    "• Productos específicos por nombre\n\n"
                    "¿Qué te gustaría conocer?"
                )
    except Exception as e:
        reply = f"Error al consultar: {e}"
    return ChatResponse(reply=reply, session_id=session_id)
