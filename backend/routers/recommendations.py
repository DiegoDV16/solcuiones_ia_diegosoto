import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.catalog_db import query_product_db, get_all_skus

router = APIRouter(tags=["recommendations"])

CATEGORY_COMPLEMENTS = {
    "procesadores": ["placas", "ram", "refrigeracion"],
    "video": ["fuentes", "monitores", "gabinetes"],
    "ram": ["procesadores", "placas"],
    "almacenamiento": ["placas", "gabinetes"],
    "placas": ["procesadores", "ram", "almacenamiento"],
    "fuentes": ["gabinetes", "video"],
    "gabinetes": ["fuentes", "refrigeracion", "almacenamiento"],
    "refrigeracion": ["procesadores", "gabinetes"],
    "perifericos": ["monitores", "accesorios"],
    "monitores": ["video", "perifericos"],
}


@router.get("/recommendations/{sku}")
async def get_recommendations(sku: str, limit: int = 4):
    _, product = query_product_db(sku)
    if not product:
        raise HTTPException(404, f"Producto {sku} no encontrado")

    cat = (product.get("categoria") or "").lower()
    complements = CATEGORY_COMPLEMENTS.get(cat, [])

    all_skus = get_all_skus()
    results = []
    seen_cats = set()

    for s in all_skus:
        if s == sku:
            continue
        _, p = query_product_db(s)
        if not p or p.get("total_stock", 0) == 0:
            continue
        p_cat = (p.get("categoria") or "").lower()
        if p_cat in complements and p_cat not in seen_cats:
            results.append({
                "sku": p["sku"],
                "nombre": p["nombre"],
                "precio_lista": p["precio_lista"],
                "descuento_efectivo": p["descuento_efectivo"],
                "categoria": p["categoria"],
                "total_stock": p["total_stock"],
                "reason": f"Complemento ideal para {product.get('nombre', 'tu producto')}",
            })
            seen_cats.add(p_cat)
        if len(results) >= limit:
            break

    if len(results) < limit:
        for s in all_skus:
            if s == sku or any(r["sku"] == s for r in results):
                continue
            _, p = query_product_db(s)
            if not p or p.get("total_stock", 0) == 0:
                continue
            results.append({
                "sku": p["sku"],
                "nombre": p["nombre"],
                "precio_lista": p["precio_lista"],
                "descuento_efectivo": p["descuento_efectivo"],
                "categoria": p["categoria"],
                "total_stock": p["total_stock"],
                "reason": "Producto popular en PC Factoría",
            })
            if len(results) >= limit:
                break

    return {
        "source_sku": sku,
        "source_name": product.get("nombre", ""),
        "recommendations": results,
    }


@router.get("/recommendations/bundle/{budget}")
async def get_bundle_recommendations(budget: int):
    all_skus = get_all_skus()
    categorized = {}

    for s in all_skus:
        _, p = query_product_db(s)
        if not p or p.get("total_stock", 0) == 0:
            continue
        cat = (p.get("categoria") or "").lower()
        effective = p["precio_lista"] - int(p["precio_lista"] * p["descuento_efectivo"])
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append({**p, "precio_efectivo": effective})

    selected = []
    total = 0
    priority = ["procesadores", "placas", "ram", "video", "almacenamiento", "fuentes", "gabinete", "refrigeracion"]

    for cat in priority:
        items = categorized.get(cat, [])
        items.sort(key=lambda x: x["precio_efectivo"])
        for item in items:
            if total + item["precio_efectivo"] <= budget:
                selected.append(item)
                total += item["precio_efectivo"]
                break

    return {
        "budget": budget,
        "total": total,
        "remaining": budget - total,
        "items": selected,
    }
