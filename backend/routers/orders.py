import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.catalog_db import (
    simulate_order,
    create_order_by_branch_code,
    get_order_details,
)

router = APIRouter(tags=["orders"])


class OrderItem(BaseModel):
    sku: str
    cantidad: int


class SimulateRequest(BaseModel):
    branch_code: str
    items: list[OrderItem]
    cliente_nombre: Optional[str] = None


class CreateRequest(BaseModel):
    branch_code: str
    items: list[OrderItem]
    cliente_nombre: Optional[str] = None


@router.post("/orders/simulate")
async def simulate(req: SimulateRequest):
    try:
        result = simulate_order(
            req.branch_code,
            [(i.sku, i.cantidad) for i in req.items],
            req.cliente_nombre,
        )
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/orders")
async def create_order(req: CreateRequest):
    try:
        order_id = create_order_by_branch_code(
            req.branch_code,
            [(i.sku, i.cantidad) for i in req.items],
            req.cliente_nombre,
        )
        details = get_order_details(order_id)
        return details
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    try:
        return get_order_details(order_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/orders/{order_id}/track")
async def track_order(order_id: int):
    try:
        details = get_order_details(order_id)
        order = details["order"]
        statuses = [
            {"estado": "confirmada", "fecha": order["fecha"], "descripcion": "Orden recibida y confirmada"},
            {"estado": "preparacion", "fecha": order["fecha"], "descripcion": "Productos en preparación"},
            {"estado": "listo", "fecha": order["fecha"], "descripcion": "Listo para retiro en sucursal"},
        ]
        recommendations = []
        try:
            from backend.routers.recommendations import get_recommendations
            for item in details.get("items", []):
                recs = await get_recommendations(item["sku"], limit=2)
                recommendations.extend(recs.get("recommendations", []))
        except Exception:
            pass
        return {
            "order": order,
            "items": details["items"],
            "tracking": statuses,
            "recommendations": recommendations[:4],
        }
    except ValueError as e:
        raise HTTPException(404, str(e))
