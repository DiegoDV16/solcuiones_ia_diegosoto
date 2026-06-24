# Informe Técnico — PC Factoría IA: Sistema Completo

**Asignatura:** ISY0101 Optativo Ingeniería de Soluciones con IA  
**Evaluación:** Informe Final  
**Fecha:** Junio 2026

---

## 1. Arquitectura General

### 1.1 Stack Tecnológico

| Componente | Tecnología | Rol |
|---|---|---|
| Frontend | React 19 + Vite + TypeScript | SPA con routing, carrito, chat, páginas de producto |
| Backend | FastAPI + Python 3.12 | API REST con endpoints para catálogo, órdenes, chat |
| Base de datos | SQLite (WAL mode) | Catálogo de productos, inventario, sucursales, sesiones |
| Proxy reverso | nginx | TLS, compresión, cabeceras de seguridad, proxy a SPA y API |
| Contenedores | Docker Compose | Frontend, backend, nginx, dashboard de monitoreo |
| LLM (opcional) | GPT-4o-mini (Azure/GitHub Models) | Agente conversacional para respuestas naturales |
| Dashboard | Streamlit + Plotly | Visualización de métricas en tiempo real |

### 1.2 Diagrama de Despliegue

```
Internet
   │
   ├─ HTTP :80 ──► nginx ──► /api/* ──► backend:8000 (uvicorn, 4 workers)
   │                              └── ► /* ──► frontend:4173 (Vite static)
   │
   └─ HTTPS :443 ─► nginx (TLS autofirmado)
                        │
                        └── SQLite (WAL mode, busy_timeout=5000)
```

---

## 2. Frontend — React SPA

### 2.1 Estructura de Componentes

```
App.tsx
├── Header
│   ├── Logo, nav (Ofertas, Recomendaciones, Órdenes, Soporte)
│   ├── Búsqueda, Carrito (con badge), Perfil (dropdown con enlaces)
│   └── Menú móvil con enlace a /cuenta
├── Routes
│   ├── / → HomePage (productos destacados, categorías)
│   ├── /categoria → CategoryPage (filtros, búsqueda, sort, paginación 9/pág)
│   ├── /producto/:sku → ProductDetailPage (stock por sucursal, mini chat)
│   ├── /asistente → AIAssistantPage (sidebar + chat terminal)
│   ├── /carrito → CartPage (checkout con sucursal)
│   ├── /ordenes → OrderTrackingPage (seguimiento + recomendaciones)
│   ├── /recomendaciones → RecommendationsPage (Paquete Inteligente IA)
│   ├── /nosotros → AboutPage (sucursales desde API)
│   ├── /cuenta → AccountPage (favoritos, enlaces rápidos)
│   └── * → NotFound
├── Footer
└── TechAssistAI (widget flotante global)
```

### 2.2 Funcionalidades Clave

| Funcionalidad | Implementación | Archivo |
|---|---|---|
| **Carrito** | CartContext + sessionStorage, persistencia entre sesiones | `context/CartContext.tsx` |
| **Checkout real** | simulateOrder + createOrder, formulario con sucursal desde API | `pages/CartPage.tsx` |
| **Búsqueda** | Query params `?search=` en CategoryPage + header | `pages/CategoryPage.tsx`, `components/Header.tsx` |
| **Paginación** | 9 productos por página con controles | `pages/CategoryPage.tsx` |
| **Favoritos** | localStorage, array de SKUs, toggle en ProductDetailPage | `pages/ProductDetailPage.tsx` |
| **Skeleton loaders** | Componente ProductSkeleton durante carga | `components/ProductCard.tsx` |
| **ErrorBoundary** | Clase ErrorBoundary envolviendo la app | `components/ErrorBoundary.tsx` |
| **Paquete Inteligente IA** | Recomendación de PC completa vía `/recommendations/bundle/:budget` | `pages/RecommendationsPage.tsx` |
| **Sucursales en AboutPage** | GET /branches desde API al cargar | `pages/AboutPage.tsx` |

### 2.3 Sidebar Interactivo (AIAssistantPage)

Los botones del panel lateral ahora ejecutan acciones reales:

| Botón | Acción |
|---|---|
| Asistente | Navega a `/asistente` |
| Especificaciones | Navega a `/categoria` |
| Compatibilidad | Envía "Quiero verificar compatibilidad de componentes" al chat |
| Estado de Orden | Navega a `/ordenes` |
| Soporte Humano | Abre `mailto:soporte@pcfactoria.cl` |
| + Nuevo Armado | Envía "Quiero armar una PC nueva" al chat |
| Quick actions | Envían su label directamente al chat como consulta |

### 2.4 Perfil de Usuario

- **Icono en header desktop**: Dropdown con "Mis Órdenes", "Favoritos", "Soporte"
- **Menú móvil**: Enlace "Cuenta" → `/cuenta`
- **Página `/cuenta`**: Muestra enlaces rápidos y lista de favoritos guardados en localStorage

---

## 3. Backend — FastAPI

### 3.1 Endpoints

| Endpoint | Método | Propósito |
|---|---|---|
| `/api/products` | GET | Listado con filtros opcionales (category, search) |
| `/api/products/:sku` | GET | Detalle de producto con inventario por sucursal |
| `/api/categories` | GET | Lista de categorías |
| `/api/branches` | GET | Sucursales activas |
| `/api/chat` | POST | Chat con TechAssist (LLM o fallback rule-based) |
| `/api/chat/reset` | POST | Reinicia sesión de chat |
| `/api/orders/simulate` | POST | Simula orden sin descontar stock |
| `/api/orders` | POST | Crea orden real y descuenta stock |
| `/api/orders/:id/track` | GET | Estado de seguimiento de orden |
| `/api/orders/:id` | GET | Detalle de orden |
| `/api/recommendations/:sku` | GET | Recomendaciones para un producto |
| `/api/recommendations/bundle/:budget` | GET | Paquete completo para un presupuesto |
| `/api/metrics` | GET | Snapshot de métricas en tiempo real |
| `/api/health/detailed` | GET | Healthcheck con métricas |

### 3.2 Motor de Chat (Fallback Rule-Based)

Cuando no hay token LLM configurado, el sistema usa `_fallback_chat()` con las siguientes capacidades:

#### 3.2.1 Detección de Intención

| Intención | Detección | Acción |
|---|---|---|
| **Saludo** | Palabras clave (hola, buenas, saludos) + longitud < 40 | Mensaje de bienvenida, limpia sesión |
| **Presupuesto/build** | "presupuesto", "armar", números ≥ 1000 | Construye PC con estrategias rotativas |
| **Otra opción** | "otra opcion", "alternativa", "variante" | Siguiente estrategia de build |
| **Ofertas** | "oferta", "descuento", "promo" | Productos con descuento > 0 |
| **Más barato/caro** | "mas barato", "mas caro" | Producto por precio según categoría |
| **Stock** | "stock" + categoría | Stock por sucursal o resumen global |
| **Categoría** | Keywords (procesador, GPU, RAM, etc.) | Listado de productos de esa categoría |
| **Búsqueda** | LIKE sobre nombre del producto | Hasta 8 resultados |
| **Email** | "sí"/"si"/"3" después de una consulta | Envía detalles por correo |

#### 3.2.2 Seguridad y Anti-Spam

| Mecanismo | Implementación |
|---|---|
| **Gibberish/repetido** | Mensajes de 1 carácter o idénticos al anterior → respuesta explicativa |
| **"no" sin contexto** | Si no hay `last_details`, responde amigablemente sin buscar |
| **Anti-spam email** | Flag `email_sent` impide reenvío múltiple en una consulta |
| **Rate limiting** | 20 req/60s por sesión en `/api/chat` |
| **Sanitización** | Detección de SQL injection, XSS, patrones maliciosos |

#### 3.2.3 Estrategias de Build (Rotativas)

Cuatro estrategias que rotan por presupuesto:

| Estrategia | Desc | GPU-First |
|---|---|---|
| Máximo Rendimiento | Sí | No |
| Enfoque GPU | Sí | Sí |
| Balance calidad | No | No |
| Enfoque CPU | No | Sí |

El contador se almacena en `session_data` con key `build_count_{budget}`, persistente entre workers.

### 3.3 Persistencia de Sesión

Migrada de in-memory a SQLite para soportar múltiples workers:

| Tabla | Propósito | Columnas |
|---|---|---|
| `session_data` | Estado de sesión del fallback chat | session_id, key, value |
| `chat_history` | Historial de mensajes para LLM | session_id, message_idx, role, content |

### 3.4 SMTP — Correos Transaccionales

Configuración con App Password de Gmail:

| Tipo | Formato | Contenido |
|---|---|---|
| **Detalles de consulta** | Multipart (plain + HTML) | Introducción amigable, build/presupuesto, branding PC Factoría |
| **Comprobante de orden** | Multipart (plain + HTML) | Orden #, sucursal, total, lista de productos |
| **HTML branding** | Template responsive | Header rojo (#e94560), footer con link, fondo gris |

---

## 4. Infraestructura y Seguridad

### 4.1 nginx

| Configuración | Valor |
|---|---|
| `server_tokens` | off |
| **Puerto 80** | Sirve SPA + proxy `/api/` directamente (sin redirect a HTTPS) |
| **Puerto 443** | TLS con cert autofirmado generado en build |
| **CSP** | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| **HSTS** | `max-age=31536000; includeSubDomains` |
| **X-Frame-Options** | DENY |
| **X-Content-Type-Options** | nosniff |
| **Referrer-Policy** | strict-origin-when-cross-origin |
| **Permissions-Policy** | `geolocation=(), microphone=(), camera=()` |
| **CORS headers** | `proxy_set_header Origin $http_origin` |

### 4.2 SQLite — Configuración Multi-Worker

```python
# WAL mode + busy timeout para concurrencia
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA busy_timeout=5000")
```

### 4.3 uvicorn

```bash
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

Cada worker ejecuta `init_catalog_db()` vía lifespan handler (idempotente).

---

## 5. Observabilidad

### 5.1 Métricas (`MetricsCollector`)

| Métrica | Captura |
|---|---|
| Precisión | `total_errors / total_requests` |
| Latencia promedio, P95, P99 | Array de 10.000 muestras |
| Frecuencia de errores | Conteo por tipo de excepción |
| Uso de CPU/RAM | `psutil` cada snapshot |
| Cache hit ratio | `hits / (hits + misses)` |
| Carga por endpoint | Distribución en `requests_by_endpoint` |
| Tokens LLM | Acumulador global |

### 5.2 Logs Estructurados

| Archivo | Contenido |
|---|---|
| `chat.log` | Prompts, respuestas, latencia, tokens, estado |
| `api.log` | Solicitudes HTTP, status, duración |
| `audit.log` | Eventos de auditoría |
| `error.log` | Excepciones y errores |
| `access.log` | Traza completa |

### 5.3 Dashboard (Streamlit + Plotly)

Puerto 8501, 5 pestañas:

1. **Visión General** — Tarjetas métricas, consultas/día, distribución por endpoint
2. **Métricas del Agente IA** — Latencia, tokens, cache hit ratio
3. **Errores y Anomalías** — Distribución, cuellos de botella, anomalías estadísticas
4. **Historial de Prompts** — Búsqueda textual en interacciones
5. **Trazabilidad** — Diagrama de flujo con spans

### 5.4 Trazabilidad Distribuida

IDs de correlación (`request_id`, `trace_id`) asignados por `ObservabilityMiddleware` via `ContextVar`, spans anidados para llamadas LLM y ejecución de herramientas.

---

## 6. Seguridad y Uso Responsable

### 6.1 Sanitización de Entrada

| Ataque | Patrones detectados |
|---|---|
| SQL Injection | SELECT.*FROM, DROP TABLE, DELETE FROM, UNION SELECT, --, ;, /* |
| XSS | `<script>`, `javascript:`, `on\w+=`, etiquetas HTML |
| Path Traversal | `../`, `..\\` |
| Command Injection | `; rm`, `| cat`, `` ` `` |

### 6.2 Rate Limiting

| Límite | Ventana | Aplicación |
|---|---|---|
| General | 60 req/60s por usuario+endpoint | Middleware global |
| Chat IA | 20 req/60s por sesión | Endpoint `/api/chat` |

### 6.3 Anti-Spam de Correo

Flag `email_sent` en `session_data` impide reenvío de detalles por consulta.

### 6.4 Anonimización

- IDs de usuario: SHA-256 truncado a 16 caracteres hex
- IPs: Último octeto enmascarado
- Textos: Truncados a 2000 caracteres en logs

---

## 7. Manejo de Markdown en Respuestas

Todas las respuestas del bot (tanto LLM como rule-based) pasan por `_clean_md()`:

```python
def _clean_md(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # bold
    text = re.sub(r'~~(.+?)~~', r'\1', text)        # strikethrough
    text = re.sub(r'_(.+?)_', r'\1', text)           # italic
    return text
```

En correos electrónicos, se usa `_strip_md()` para texto plano y `_md_to_html()` para la versión HTML (convierte `**` → `<strong>`, `~~` → `<s>`, `_` → `<em>`).

---

## 8. Decisiones Técnicas

| Decisión | Alternativa | Motivo |
|---|---|---|
| SQLite en vez de PostgreSQL | PostgreSQL | Mínima complejidad, suficiente para decenas de usuarios concurrentes |
| Sesión en SQLite en vez de Redis | Redis | Evita dependencia externa; funciona con `--workers 4` |
| Rotación de estrategias vía contador | Random | Da variedad sin perder determinismo |
| nginx sin redirect HTTP→HTTPS | Redirect forzoso | Evita problemas CORS al acceder por IP directa con HTTP |
| Puerto 3000 → 3001 en proxy Vite | Puerto 3000 | Proceso stale en 3000 no podía terminarse |

---

## 9. Pendientes y Próximos Pasos

1. Probar builds en EC2: navegación, checkout, builds dinámicos, correo, reset de chat
2. Monitorear logs del backend en EC2 para verificar que SQLite session store funciona sin race conditions
3. Ampliar cobertura de sanitización (NoSQL injection, template injection)
4. Integrar `bandit` (SAST) en pipeline CI/CD
5. Conectar dashboard Streamlit a Redis para datos en tiempo real entre workers

---

## 10. Conclusiones

El sistema PC Factoría IA implementa una tienda virtual completa con asistente conversacional, carrito de compras real, seguimiento de órdenes, recomendaciones inteligentes y un panel de administración con métricas de observabilidad en tiempo real.

La arquitectura elegida (React + FastAPI + SQLite + nginx en Docker Compose) logra un balance óptimo entre funcionalidad y simplicidad, permitiendo despliegue en instancias pequeñas (t2.micro) sin depender de servicios externos más que el proveedor LLM opcional.

La migración de sesiones de in-memory a SQLite garantiza consistencia entre workers de uvicorn, y las cuatro estrategias rotativas de build dan variedad a las recomendaciones de armado sin sacrificar determinismo.

---

## Referencias

- FastAPI. (2025). *Middleware Documentation*. https://fastapi.tiangolo.com/tutorial/middleware/
- React. (2025). *Context and Hooks Documentation*. https://react.dev/reference/react
- SQLite. (2025). *WAL-mode Documentation*. https://www.sqlite.org/wal.html
- nginx. (2025). *ngx_http_headers_module*. https://nginx.org/en/docs/http/ngx_http_headers_module.html
- Streamlit. (2025). *Streamlit Documentation*. https://docs.streamlit.io/
- Plotly. (2025). *Plotly Python Graphing Library*. https://plotly.com/python/
- Mozilla. (2025). *MDN Web Security*. https://developer.mozilla.org/en-US/docs/Web/Security
