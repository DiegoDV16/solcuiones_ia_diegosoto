# Informe de Observabilidad — PC Factoría IA

**Asignatura:** ISY0101 Optativo Ingeniería de Soluciones con IA  
**Evaluación Parcial N°3**  
**Fecha:** Junio 2026  

---

## 1. Implementación de Métricas de Observabilidad (IE1, IE2)

### 1.1 Arquitectura del Módulo de Métricas

El sistema implementa un colector de métricas singleton (`MetricsCollector`) en `backend/monitoring/metrics.py` que captura y expone en tiempo real:

| Métrica | Tipo | Implementación |
|---|---|---|
| **Precisión** | Tasa de error | `total_errors / total_requests` vía `record_ai_interaction(duration, tokens, success)` |
| **Latencia promedio** | Media aritmética | `avg_latency_ms` sobre las últimas 10.000 muestras |
| **Latencia P95 / P99** | Percentiles | Ordenamiento parcial sobre `latencies[]` |
| **Frecuencia de errores** | Conteo por tipo | `error_types: dict[str, int]` en `record_error(error_type)` |
| **Uso de recursos** | CPU %, Memoria % y MB | `psutil.cpu_percent()`, `psutil.virtual_memory().percent` |
| **Consistencia** | Hit ratio de caché | `cache_hits / (cache_hits + cache_misses)` |
| **Carga por endpoint** | Distribución | `requests_by_endpoint: dict[str, int]` |
| **Tokens consumidos** | Acumulador | `total_tokens` por interacción del agente IA |

### 1.2 Instrumentación del Agente IA

El endpoint `/api/chat` (`backend/routers/chat.py:211`) integra métricas en cada etapa del flujo:

```python
# Captura de latencia total (chat.py:247, 284)
start_time = time.perf_counter()
# ...
duration = (time.perf_counter() - start_time) * 1000
metrics.record_ai_interaction(duration, tokens_used, success=True)
metrics.record_request("/api/chat", duration, req.session_id)

# Registro de errores por tipo (chat.py:303-304)
metrics.record_ai_interaction(duration, 0, success=False)
metrics.record_error(type(e).__name__)
```

Se utiliza un decorador `@monitor_endpoint` y un context manager `track_latency()` para instrumentar otros endpoints de forma declarativa.

### 1.3 Exposición de Métricas

El middleware `setup_monitoring()` (`middleware.py:79-94`) registra dos endpoints:

- **`GET /api/metrics`** → snapshot completo del `MetricsCollector.get_snapshot()`
- **`GET /api/health/detailed`** → métricas + uptime + status

---

## 2. Análisis de Registros y Trazabilidad (IE3, IE4)

### 2.1 Sistema de Logs

Se implementaron cinco archivos de log rotativos con formato JSON estructurado (`backend/monitoring/logger.py`):

| Archivo | Propósito | Campos clave |
|---|---|---|
| `chat.log` | Interacciones del agente IA | `user_id` (anonimizado), `prompt`, `response`, `response_time_ms`, `tokens`, `status`, `error` |
| `api.log` | Solicitudes HTTP | `endpoint`, `method`, `http_status`, `duration_ms`, `ip` (anonimizada) |
| `audit.log` | Eventos de auditoría | `action`, `user_id`, `resource`, `outcome` |
| `error.log` | Excepciones y errores | `error_type`, `message`, `endpoint` |
| `access.log` | Traza completa de acceso | `endpoint`, `method`, `user_id`, `duration_ms` |

### 2.2 Motor de Análisis (`LogAnalyzer`)

La clase `LogAnalyzer` en `backend/monitoring/analytics.py` procesa los logs para extraer:

- **Estadísticas de chat**: tasa de éxito/error, latencia media/mediana/máxima/P95, distribución horaria y diaria, top usuarios
- **Análisis de errores**: tipos de error más frecuentes, errores por endpoint
- **Detección de cuellos de botella**: consultas con latencia > 5s (configurable) ordenadas por duración descendente
- **Detección de anomalías estadísticas**: latencias que superan `media + 3σ` y picos de uso horario que exceden el umbral estadístico

```python
# Ejemplo de detección de anomalías (analytics.py:124-167)
def detect_anomalies(self, std_multiplier=3.0):
    mean = statistics.mean(latencies)
    stdev = statistics.stdev(latencies)
    threshold = mean + stdev * std_multiplier
    # Identifica outliers y picos de uso
```

### 2.3 Trazabilidad Distribuida

Se implementó un sistema de trazabilidad propio (`Tracer` y `Span` en `tracing.py`) que asigna un `request_id` único por solicitud y permite anidar spans padre-hijo:

```
Trace: chat_1719000000
├── Span: agent_invoke (12ms, status: ok)
│   ├── Span: llm_call (8ms)
│   └── Span: tool_execution (3ms)
└── Span: response_serialization (1ms)
```

El `ObservabilityMiddleware` asigna `request_id` y `trace_id` al inicio de cada request usando `ContextVar`, garantizando correlación entre logs, métricas y trazas.

---

## 3. Dashboard de Monitoreo (IE5)

### 3.1 Stack Tecnológico

- **Framework:** Streamlit (Python)
- **Visualización:** Plotly (gráficos interactivos)
- **Orquestación:** Servicio Docker bajo perfil `monitoring` (`docker-compose.yml:35-48`)
- **Puerto:** 8501

### 3.2 Estructura del Dashboard (`dashboard_app.py` — 312 líneas)

El dashboard se organiza en 5 pestañas:

| Pestaña | Contenido | Visualizaciones |
|---|---|---|
| **📈 Visión General** | Métricas del sistema en tarjetas (solicitudes, latencia, error, CPU, memoria), consultas por día, distribución por endpoint | 5 tarjetas métricas, gráfico de barras, gráfico de pastel, tabla de logs recientes |
| **🤖 Métricas del Agente IA** | Latencia promedio/P95/P99, tokens totales, cache hit ratio, histograma de latencia, últimas 100 respuestas, distribución de tokens | 6 tarjetas métricas, histograma, scatter plot, histograma de tokens |
| **⚠️ Errores y Anomalías** | Distribución de errores por tipo, tabla de errores recientes, cuellos de botella (>5s), anomalías de latencia y uso | Gráfico de barras, tabla, warning/success indicators |
| **📝 Historial de Prompts** | Búsqueda textual en prompts, slider de cantidad, tarjetas expandibles con prompt/respuesta/latencia/tokens | Campo de búsqueda, slider, expanders anidados |
| **🔄 Trazabilidad** | Diagrama ASCII del flujo de solicitud, muestras de trazas en JSON | Diagrama de flujo, JSON viewer |

### 3.3 Capturas del Dashboard

> *Nota: Las capturas de pantalla deben insertarse aquí. Se recomienda ejecutar el dashboard localmente con `streamlit run dashboard_app.py` y capturar cada pestaña.*

**Figura 1.** *Pestaña Visión General — Tarjetas métricas, consultas por día y distribución por endpoint.*  
**Figura 2.** *Pestaña Métricas del Agente IA — Histograma de latencia, scatter de últimas 100 respuestas, distribución de tokens.*  
**Figura 3.** *Pestaña Errores y Anomalías — Distribución de errores, tabla de errores, detección de cuellos de botella.*  
**Figura 4.** *Pestaña Historial de Prompts — Búsqueda y navegación del historial de interacciones.*  
**Figura 5.** *Pestaña Trazabilidad — Diagrama de flujo y muestras de trazas.*

---

## 4. Seguridad y Uso Responsable (IE6)

### 4.1 Sanitización de Entrada

La clase `Sanitizer` (`security.py:10-58`) detecta y filtra patrones de inyección:

- **SQL Injection:** 10 patrones regex (`SELECT.*FROM`, `DROP TABLE`, `DELETE FROM`, `UNION SELECT`, `--`, `;`, `/*`)
- **XSS:** 4 patrones (`<script>`, `javascript:`, `on\w+=`, etiquetas HTML genéricas)

### 4.2 Anonimización

`Anonymizer` (`security.py:61-87`) protege datos personales:

- **Hash de IDs de usuario:** SHA-256 truncado a 16 caracteres hex
- **Anonimización de IP:** Enmascara el último octeto (IPv4) o la interfaz (IPv6)
- **Truncamiento de texto:** Limita prompts/respuestas a 2000 caracteres

### 4.3 Rate Limiting

`RateLimiter` (`security.py:90-125`) implementa ventana deslizante por clave:

| Límite | Configuración | Aplicación |
|---|---|---|
| General | 60 req/60s por usuario+endpoint | Middleware global (middleware.py:31) |
| Chat IA | 20 req/60s por sesión | Endpoint `/api/chat` (chat.py:228-239) |

### 4.4 Registro de Auditoría

Cada operación exitosa genera un evento de auditoría en `audit.log` con `action`, `user_id` (anonimizado), `resource` y `outcome`, permitiendo trazabilidad forense completa.

---

## 5. Propuesta de Mejoras (IE7)

### 5.1 Optimización de Latencia

**Hallazgo:** El percentil P95 de latencia indica que el 5% de las solicitudes más lentas pueden exceder los 3s en el agente LLM, principalmente por llamadas a la API de Azure OpenAI.

**Recomendaciones:**
1. **Caché aumentada:** Actualmente TTL=300s con max_size=500. Incrementar a TTL=600s y max_size=2000 para consultas frecuentes (productos, stock, sucursales).
2. **Compresión de respuestas:** Habilitar compresión gzip en nginx para reducir payload de respuestas del agente.
3. **Timeout ajustable:** Implementar timeout dinámico basado en el percentil P95 histórico.

### 5.2 Escalabilidad

**Hallazgo:** El `MetricsCollector` mantiene hasta 10.000 muestras de latencia en memoria. Con 4 workers de uvicorn, cada worker tiene su propia instancia singleton.

**Recomendaciones:**
1. **Backend de métricas compartido:** Migrar a Redis para consolidar métricas entre workers (evitar duplicación).
2. **Persistencia de logs:** Implementar rotación con compresión en logs mayores a 100MB.
3. **Dashboard en tiempo real:** Conectar Streamlit directamente a Redis en vez de consultar `/api/metrics` mediante polling HTTP.

### 5.3 Detección de Anomalías

**Hallazgo:** El detector de anomalías usa desviación estándar (`media + 3σ`), sensible a outliers extremos.

**Recomendaciones:**
1. **MAD (Median Absolute Deviation):** Métrica robusta frente a outliers para umbrales de latencia.
2. **Alertas automáticas:** Integrar notificaciones por correo cuando se detecten >5 anomalías/hora.
3. **Ventana temporal deslizante:** Analizar ventanas de 15 minutos en vez de todo el histórico para detectar degradación temprana.

### 5.4 Seguridad

**Hallazgo:** Las reglas de sanitización detectan patrones SQL/XSS conocidos pero no cubren NoSQL injection u otras variantes.

**Recomendaciones:**
1. **Ampliar cobertura de sanitización:** Agregar detección de path traversal, command injection, template injection.
2. **Pruebas de penetración automatizadas:** Integrar `bandit` (SAST) en el pipeline CI/CD.
3. **HTTPS por defecto:** En desarrollo local, forzar HTTPS con el certificado autofirmado ya implementado en Docker.

---

## 6. Conclusiones

El sistema de observabilidad implementado cubre los cuatro pilares fundamentales:

1. **Métricas** — 8 categorías (precisión, latencia promedio/P95/P99, errores, recursos, consistencia, carga, tokens) capturadas en tiempo real
2. **Logs** — 5 archivos JSON estructurados con anonimización y rotación
3. **Trazabilidad** — IDs de correlación, spans anidados y exportación JSON
4. **Dashboard** — Streamlit con 5 pestañas, gráficos Plotly interactivos y detección de anomalías

La integración con el agente de IA (TechAssist) permite monitorear cada interacción desde la sanitización inicial hasta la respuesta al usuario, pasando por rate limiting, caché, llamada LLM y registro de auditoría.

---

## Referencias

- Burnham, K. P., & Anderson, D. R. (2002). *Model Selection and Multimodel Inference: A Practical Information-Theoretic Approach* (2nd ed.). Springer.
- FastAPI. (2025). *Middleware Documentation*. https://fastapi.tiangolo.com/tutorial/middleware/
- Google. (2024). *Site Reliability Engineering: Measuring and Managing Reliability*. https://sre.google/books/
- OpenTelemetry Authors. (2025). *OpenTelemetry Documentation*. https://opentelemetry.io/docs/
- Plotly Technologies. (2025). *Plotly Python Graphing Library*. https://plotly.com/python/
- Streamlit Inc. (2025). *Streamlit Documentation*. https://docs.streamlit.io/
- Zalando. (2024). *RESTful API Guidelines*. https://opensource.zalando.com/restful-api-guidelines/
