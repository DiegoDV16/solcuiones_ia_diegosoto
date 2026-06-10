import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.catalog_db import (
    query_product_db,
    get_all_skus,
    list_branches,
    query_products_by_region,
    get_branch_by_code,
    get_branch_inventory,
)

router = APIRouter(tags=["products"])


class ProductResponse(BaseModel):
    sku: str
    nombre: str
    descripcion: Optional[str] = None
    precio_lista: int
    descuento_efectivo: float
    categoria: Optional[str] = None
    inventory: list[dict] = []
    total_stock: int = 0


class BranchResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    region: str
    comuna: str
    direccion: Optional[str] = None


@router.get("/products", response_model=list[ProductResponse])
async def list_products(category: Optional[str] = None, search: Optional[str] = None):
    skus = get_all_skus()
    results = []
    for sku in skus:
        _, prod = query_product_db(sku)
        if prod:
            if category and category.lower() not in (prod.get("categoria") or "").lower():
                continue
            if search and search.lower() not in prod["nombre"].lower() and search.lower() not in prod["sku"].lower():
                continue
            results.append(ProductResponse(**prod))
    return results


@router.get("/products/{sku}", response_model=ProductResponse)
async def get_product(sku: str):
    _, prod = query_product_db(sku)
    if not prod:
        raise HTTPException(404, f"Producto {sku} no encontrado")
    return ProductResponse(**prod)


@router.get("/categories")
async def list_categories():
    import sqlite3
    db_path = ROOT / "Scripts" / "catalogo_pc_factory.db"
    with sqlite3.connect(str(db_path)) as conn:
        rows = conn.execute("SELECT id, nombre FROM categories ORDER BY nombre").fetchall()
    return [{"id": r[0], "nombre": r[1]} for r in rows]


@router.get("/branches", response_model=list[BranchResponse])
async def get_branches():
    return [BranchResponse(**b) for b in list_branches()]


@router.get("/branches/{code}/inventory")
async def branch_inventory(code: str):
    branch = get_branch_by_code(code)
    if not branch:
        raise HTTPException(404, f"Sucursal {code} no encontrada")
    items = get_branch_inventory(branch["id"])
    return {"branch": branch, "items": items}


@router.get("/regions/{name}/products")
async def products_by_region(name: str):
    return query_products_by_region(name)
