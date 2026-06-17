import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.catalog_db import init_catalog_db
from backend.routers import products, orders, chat, recommendations

from backend.monitoring.middleware import setup_monitoring
from backend.monitoring.logger import audit_log


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_catalog_db()
    audit_log("system_startup", None, "application", "Sistema iniciado correctamente")
    yield
    audit_log("system_shutdown", None, "application", "Sistema detenido")


app = FastAPI(title="PC Factoría API", version="1.0.0", lifespan=lifespan)

allow_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = setup_monitoring(app)

app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
