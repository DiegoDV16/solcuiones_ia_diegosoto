import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="PC Factory - Dashboard de Monitoreo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 PC Factory - Dashboard de Observabilidad")
st.markdown("---")

LOG_DIR = ROOT / "logs"


@st.cache_data(ttl=10)
def load_logs(filename: str) -> list[dict]:
    filepath = LOG_DIR / filename
    if not filepath.exists():
        return []
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


@st.cache_data(ttl=10)
def get_metrics():
    import requests
    try:
        resp = requests.get("http://localhost:8000/api/metrics", timeout=3)
        return resp.json()
    except Exception:
        return None


def main():
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📈 Visión General",
            "🤖 Métricas del Agente IA",
            "⚠️ Errores y Anomalías",
            "📝 Historial de Prompts",
            "🔄 Trazabilidad",
        ]
    )

    with tab1:
        show_overview()

    with tab2:
        show_ai_metrics()

    with tab3:
        show_errors()

    with tab4:
        show_prompt_history()

    with tab5:
        show_tracing()


def show_overview():
    st.subheader("📈 Visión General del Sistema")

    m = get_metrics()
    if m:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Solicitudes Totales", m.get("total_requests", 0))
        with col2:
            st.metric("Latencia Promedio", f"{m.get('avg_latency_ms', 0):.1f} ms")
        with col3:
            st.metric("Tasa de Error", f"{m.get('error_rate', 0)*100:.2f}%")
        with col4:
            st.metric("CPU", f"{m.get('cpu_percent', 0):.1f}%")
        with col5:
            st.metric("Memoria", f"{m.get('memory_used_mb', 0):.1f} MB")

        c1, c2 = st.columns(2)

        with c1:
            if m.get("daily_queries"):
                df_daily = pd.DataFrame(
                    list(m["daily_queries"].items()),
                    columns=["Fecha", "Consultas"],
                )
                fig = px.bar(df_daily, x="Fecha", y="Consultas", title="Consultas por Día")
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            if m.get("requests_by_endpoint"):
                df_ep = pd.DataFrame(
                    list(m["requests_by_endpoint"].items()),
                    columns=["Endpoint", "Solicitudes"],
                )
                fig = px.pie(df_ep, values="Solicitudes", names="Endpoint", title="Solicitudes por Endpoint")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("El servidor backend no está disponible. Conéctate a http://localhost:8000")

    st.subheader("Registros Recientes (API)")
    entries = load_logs("api.log")
    if entries:
        df = pd.DataFrame(entries[-50:])
        df["timestamp"] = pd.to_datetime(df.get("timestamp", ""))
        st.dataframe(df[["timestamp", "endpoint", "method", "http_status", "duration_ms"]].tail(20))
    else:
        st.info("No hay registros API disponibles.")


def show_ai_metrics():
    st.subheader("🤖 Métricas del Agente de IA")

    m = get_metrics()
    if m:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Latencia Promedio IA", f"{m.get('avg_ai_latency_ms', 0):.1f} ms")
        with col2:
            st.metric("P95 Latencia", f"{m.get('p95_latency_ms', 0):.1f} ms")
        with col3:
            st.metric("P99 Latencia", f"{m.get('p99_latency_ms', 0):.1f} ms")
        with col4:
            st.metric("Total Tokens", m.get("total_tokens", 0))

        col5, col6 = st.columns(2)
        with col5:
            st.metric("Cache Hit Ratio", f"{m.get('cache_hit_ratio', 0)*100:.1f}%")
        with col6:
            st.metric("Total Errores", m.get("total_errors", 0))

    st.subheader("Distribución de Latencia del Agente IA")

    entries = load_logs("chat.log")
    if entries:
        df = pd.DataFrame(entries)
        if "response_time_ms" in df.columns:
            times = df["response_time_ms"].dropna()
            fig = px.histogram(
                times,
                nbins=30,
                title="Distribución de Latencia en Chat",
                labels={"value": "Latencia (ms)", "count": "Frecuencia"},
            )
            st.plotly_chart(fig, use_container_width=True)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                y=times.tail(100),
                mode="lines+markers",
                name="Latencia",
            ))
            fig2.update_layout(
                title="Últimas 100 Respuestas - Latencia",
                xaxis_title="Solicitud #",
                yaxis_title="Latencia (ms)",
            )
            st.plotly_chart(fig2, use_container_width=True)

        if "tokens" in df.columns:
            tokens = df["tokens"].dropna()
            st.metric("Tokens Promedio por Consulta", f"{tokens.mean():.0f}")
            fig3 = px.histogram(
                tokens,
                nbins=20,
                title="Distribución de Tokens",
                labels={"value": "Tokens", "count": "Frecuencia"},
            )
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No hay registros de chat disponibles.")


def show_errors():
    st.subheader("⚠️ Análisis de Errores")

    m = get_metrics()
    if m and m.get("error_types"):
        df_err = pd.DataFrame(
            list(m["error_types"].items()),
            columns=["Tipo de Error", "Frecuencia"],
        )
        fig = px.bar(df_err, x="Tipo de Error", y="Frecuencia", title="Distribución de Errores")
        st.plotly_chart(fig, use_container_width=True)

    error_entries = load_logs("error.log")
    if error_entries:
        st.subheader(f"Últimos Errores ({len(error_entries)} total)")
        df = pd.DataFrame(error_entries[-50:])
        st.dataframe(df)
    else:
        st.info("No hay errores registrados.")

    st.subheader("Cuellos de Botella (Latencia > 5s)")
    chat_entries = load_logs("chat.log")
    if chat_entries:
        slow = [e for e in chat_entries if e.get("response_time_ms", 0) > 5000]
        if slow:
            st.warning(f"Se detectaron {len(slow)} consultas lentas")
            df_slow = pd.DataFrame(slow)
            st.dataframe(df_slow[["timestamp", "response_time_ms", "tokens", "prompt"]].head(20))
        else:
            st.success("No se detectaron cuellos de botella significativos.")

    st.subheader("Anomalías Detectadas")
    from backend.monitoring.analytics import LogAnalyzer
    analyzer = LogAnalyzer(LOG_DIR)
    anomalies = analyzer.detect_anomalies()
    if anomalies.get("high_latency"):
        st.warning(f"{len(anomalies['high_latency'])} anomalías de latencia detectadas")
    if anomalies.get("usage_anomalies"):
        st.warning(f"{len(anomalies['usage_anomalies'])} picos de uso detectados")
    if not anomalies.get("high_latency") and not anomalies.get("usage_anomalies"):
        st.success("Sin anomalías detectadas")


def show_prompt_history():
    st.subheader("📝 Historial de Prompts y Respuestas")

    entries = load_logs("chat.log")
    if not entries:
        st.info("No hay registros de chat disponibles.")
        return

    search = st.text_input("🔍 Buscar en prompts:", "")
    limit = st.slider("Mostrar últimos:", 10, 200, 50)

    df = pd.DataFrame(entries)
    if search:
        mask = df.get("prompt", "").str.contains(search, case=False, na=False)
        df = df[mask]

    df = df.tail(limit).iloc[::-1]

    for _, row in df.iterrows():
        ts = row.get("timestamp", "")
        user = row.get("user_id", "anon")
        prompt = row.get("prompt", "")[:300]
        response = row.get("response", "")[:300]
        lat = row.get("response_time_ms", 0)
        status = row.get("status", "unknown")
        tokens = row.get("tokens", 0)

        with st.expander(f"🕐 {ts} | 👤 {user} | ⏱ {lat:.0f}ms | {status}"):
            st.markdown(f"**Prompt:** {prompt}")
            st.markdown(f"**Respuesta:** {response}")
            st.caption(f"Tokens: {tokens} | Latencia: {lat:.0f}ms | Estado: {status}")
            if row.get("error"):
                st.error(f"Error: {row['error']}")


def show_tracing():
    st.subheader("🔄 Trazabilidad del Flujo")

    st.markdown(
        """
    ### Diagrama de Trazabilidad
    ```
    Usuario → FastAPI → Middleware → Router Chat → Agente IA → Herramientas → Base de Datos → Respuesta
       │          │            │            │             │            │              │            │
       ▼          ▼            ▼            ▼             ▼            ▼              ▼            ▼
     HTTP     Request ID   Observabilidad  Sanitización  LLM Call    SQL Query    SQLite DB    JSON Resp
     Request  Asignado     + Logging       + Rate Limit  + Metrics   + RAG        + Stock      + Cache
                            + Tracing
    ```
    """
    )

    trace_data = load_logs("chat.log")
    if not trace_data:
        st.info("No hay datos de trazabilidad disponibles aún.")
        return

    st.subheader("Muestras de Trazas")
    df = pd.DataFrame(trace_data[-20:])
    for _, row in df.iterrows():
        st.json(
            {
                "timestamp": row.get("timestamp", ""),
                "user_id": row.get("user_id", ""),
                "endpoint": row.get("endpoint", "/api/chat"),
                "response_time_ms": row.get("response_time_ms", 0),
                "tokens": row.get("tokens", 0),
                "status": row.get("status", ""),
                "http_status": row.get("http_status", 200),
            }
        )


if __name__ == "__main__":
    main()
