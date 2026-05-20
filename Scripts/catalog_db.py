import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "catalogo_pc_factory.db"
SQL_PATH = BASE_DIR / "catalog_db.sql"


def _table_exists(cursor, name: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ? LIMIT 1",
        (name,),
    )
    return cursor.fetchone() is not None


def init_catalog_db(recreate: bool = False) -> None:
    """Inicializa la base de datos desde el archivo SQL si no existe o se fuerza recreación."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists() and not recreate:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA foreign_keys = OFF;")
            cur = conn.cursor()
            if _table_exists(cur, "branches"):
                return
            if _table_exists(cur, "products") and not _table_exists(cur, "products_legacy"):
                cur.execute("ALTER TABLE products RENAME TO products_legacy;")
            cur.executescript(
                """
                DROP TABLE IF EXISTS order_items;
                DROP TABLE IF EXISTS orders;
                DROP TABLE IF EXISTS inventory;
                DROP TABLE IF EXISTS branches;
                DROP TABLE IF EXISTS categories;
                DROP TABLE IF EXISTS comunas;
                DROP TABLE IF EXISTS regions;
                """
            )
            conn.commit()
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = OFF;")
        cur = conn.cursor()

        cur.executescript(
            """
            DROP TABLE IF EXISTS order_items;
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS inventory;
            DROP TABLE IF EXISTS branches;
            DROP TABLE IF EXISTS categories;
            DROP TABLE IF EXISTS comunas;
            DROP TABLE IF EXISTS regions;
            """
        )

        if DB_PATH.exists() and recreate:
            if _table_exists(cur, "products"):
                cur.execute("DROP TABLE products;")
            cur.execute("DROP TABLE IF EXISTS products_legacy;")

        with SQL_PATH.open("r", encoding="utf-8") as f:
            conn.executescript(f.read())
        cur.execute("DROP TABLE IF EXISTS products_legacy;")
        cur.execute("DROP TABLE IF EXISTS __lock_test;")
        conn.commit()


def query_product_db(query: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Busca un producto por SKU exacto o por coincidencia en el nombre y devuelve inventario por sucursal."""
    texto = query.strip()
    if not texto:
        return None, None

    normalized = texto.upper()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        producto = cur.execute(
            """
            SELECT p.sku, p.nombre, p.descripcion, p.precio_lista, p.descuento_efectivo,
                   c.nombre AS categoria
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE UPPER(p.sku) = ? OR UPPER(p.nombre) LIKE ?
            ORDER BY p.sku
            LIMIT 1
            """,
            (normalized, f"%{normalized}%"),
        ).fetchone()

        if not producto:
            return None, None

        product = dict(producto)
        inventory_rows = cur.execute(
            """
            SELECT b.codigo AS branch_codigo,
                   b.nombre AS branch_nombre,
                   b.direccion,
                   r.nombre AS region,
                   m.nombre AS comuna,
                   i.cantidad
            FROM inventory i
            JOIN branches b ON i.branch_id = b.id
            JOIN regions r ON b.region_id = r.id
            JOIN comunas m ON b.comuna_id = m.id
            WHERE i.sku = ?
            ORDER BY r.nombre, m.nombre, b.nombre
            """,
            (product['sku'],),
        ).fetchall()

        product['inventory'] = [dict(row) for row in inventory_rows]
        product['total_stock'] = sum(row['cantidad'] for row in product['inventory'])
        return product['sku'], product


def _normalize_text(text: str) -> str:
    return text.strip().upper()


def get_all_skus() -> List[str]:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        rows = cur.execute("SELECT sku FROM products ORDER BY sku").fetchall()
        return [row[0] for row in rows]


def list_regions() -> List[str]:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        rows = cur.execute("SELECT nombre FROM regions ORDER BY nombre").fetchall()
        return [row[0] for row in rows]


def list_branches() -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = cur.execute(
            """
            SELECT b.id, b.codigo, b.nombre, r.nombre AS region, m.nombre AS comuna, b.direccion
            FROM branches b
            JOIN regions r ON b.region_id = r.id
            JOIN comunas m ON b.comuna_id = m.id
            ORDER BY r.nombre, m.nombre, b.nombre
            """
        ).fetchall()
        return [dict(row) for row in rows]


def get_branch_by_code(code: str) -> Optional[Dict[str, Any]]:
    if not code:
        return None
    normalized = _normalize_text(code)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        row = cur.execute(
            """
            SELECT b.id, b.codigo, b.nombre, r.nombre AS region, m.nombre AS comuna, b.direccion
            FROM branches b
            JOIN regions r ON b.region_id = r.id
            JOIN comunas m ON b.comuna_id = m.id
            WHERE UPPER(b.codigo) = ?
            LIMIT 1
            """,
            (normalized,),
        ).fetchone()
        return dict(row) if row else None


def query_products_by_region(region_or_comuna: str) -> List[Dict[str, Any]]:
    normalized = _normalize_text(region_or_comuna)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = cur.execute(
            """
            SELECT b.codigo AS branch_codigo,
                   b.nombre AS branch_nombre,
                   r.nombre AS region,
                   m.nombre AS comuna,
                   p.sku,
                   p.nombre AS producto,
                   c.nombre AS categoria,
                   i.cantidad
            FROM inventory i
            JOIN branches b ON i.branch_id = b.id
            JOIN regions r ON b.region_id = r.id
            JOIN comunas m ON b.comuna_id = m.id
            JOIN products p ON i.sku = p.sku
            JOIN categories c ON p.category_id = c.id
            WHERE UPPER(r.nombre) = ? OR UPPER(m.nombre) = ?
            ORDER BY p.nombre, b.codigo
            """,
            (normalized, normalized),
        ).fetchall()
        return [dict(row) for row in rows]


def query_shipping_to_region(region_or_comuna: str) -> List[Dict[str, Any]]:
    normalized = _normalize_text(region_or_comuna)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = cur.execute(
            """
            SELECT b.codigo AS branch_codigo,
                   b.nombre AS branch_nombre,
                   r.nombre AS region,
                   m.nombre AS comuna,
                   SUM(i.cantidad) AS stock_total,
                   COUNT(DISTINCT i.sku) AS productos_disponibles
            FROM inventory i
            JOIN branches b ON i.branch_id = b.id
            JOIN regions r ON b.region_id = r.id
            JOIN comunas m ON b.comuna_id = m.id
            WHERE UPPER(r.nombre) = ? OR UPPER(m.nombre) = ?
            GROUP BY b.id, b.codigo, b.nombre, r.nombre, m.nombre
            ORDER BY r.nombre, m.nombre, b.nombre
            """,
            (normalized, normalized),
        ).fetchall()
        return [dict(row) for row in rows]


def simulate_order(branch_code: str, items: List[Tuple[str, int]], cliente_nombre: Optional[str] = None) -> Dict[str, Any]:
    branch = get_branch_by_code(branch_code)
    if not branch:
        raise ValueError(f"No encontré la sucursal con código '{branch_code}'.")
    if not items:
        raise ValueError("Debes indicar al menos un artículo y su cantidad.")

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        detalle = []
        total = 0
        for sku, cantidad in items:
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a cero.")

            producto = cur.execute(
                "SELECT nombre, precio_lista, descuento_efectivo FROM products WHERE sku = ?",
                (sku,),
            ).fetchone()
            if not producto:
                raise ValueError(f"Producto no encontrado: {sku}")

            inventario = cur.execute(
                "SELECT cantidad FROM inventory WHERE branch_id = ? AND sku = ?",
                (branch['id'], sku),
            ).fetchone()
            cantidad_disponible = inventario['cantidad'] if inventario else 0
            if cantidad_disponible < cantidad:
                raise ValueError(
                    f"Stock insuficiente para {sku} en {branch['codigo']}: disponible {cantidad_disponible}, pediste {cantidad}."
                )

            precio_unitario = producto['precio_lista']
            descuento = producto['descuento_efectivo']
            subtotal = int(precio_unitario * cantidad * (1 - descuento))
            total += subtotal
            detalle.append(
                {
                    'sku': sku,
                    'nombre': producto['nombre'],
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'descuento': descuento,
                    'subtotal': subtotal,
                    'disponible': cantidad_disponible,
                }
            )

        return {
            'branch': branch,
            'cliente_nombre': cliente_nombre,
            'items': detalle,
            'total': total,
        }


def create_order(branch_id: int, items: List[Tuple[str, int]], cliente_nombre: Optional[str] = None) -> int:
    if not items:
        raise ValueError("Debes indicar al menos un artículo y su cantidad.")

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")

        total = 0
        for sku, cantidad in items:
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a cero.")

            producto = cur.execute(
                "SELECT precio_lista, descuento_efectivo FROM products WHERE sku = ?",
                (sku,),
            ).fetchone()
            if not producto:
                raise ValueError(f"Producto no encontrado: {sku}")

            inventario = cur.execute(
                "SELECT cantidad FROM inventory WHERE branch_id = ? AND sku = ?",
                (branch_id, sku),
            ).fetchone()
            cantidad_disponible = inventario['cantidad'] if inventario else 0
            if cantidad_disponible < cantidad:
                raise ValueError(
                    f"Stock insuficiente para {sku} en la sucursal {branch_id}: disponible {cantidad_disponible}, pediste {cantidad}."
                )

            subtotal = int(producto['precio_lista'] * cantidad * (1 - producto['descuento_efectivo']))
            total += subtotal

        cur.execute(
            "INSERT INTO orders (branch_id, cliente_nombre, total) VALUES (?, ?, ?)",
            (branch_id, cliente_nombre, total),
        )
        order_id = cur.lastrowid

        for sku, cantidad in items:
            producto = cur.execute(
                "SELECT precio_lista, descuento_efectivo FROM products WHERE sku = ?",
                (sku,),
            ).fetchone()
            cur.execute(
                "INSERT INTO order_items (order_id, sku, cantidad, precio_unitario, descuento) VALUES (?, ?, ?, ?, ?)",
                (order_id, sku, cantidad, producto['precio_lista'], producto['descuento_efectivo']),
            )
            cur.execute(
                "UPDATE inventory SET cantidad = cantidad - ? WHERE branch_id = ? AND sku = ?",
                (cantidad, branch_id, sku),
            )

        conn.commit()
        return order_id


def get_order_details(order_id: int) -> Dict[str, Any]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        order = cur.execute(
            "SELECT o.id, o.fecha, o.cliente_nombre, o.total, b.codigo AS branch_codigo, b.nombre AS branch_nombre, r.nombre AS region, m.nombre AS comuna, b.direccion "
            "FROM orders o "
            "JOIN branches b ON o.branch_id = b.id "
            "JOIN regions r ON b.region_id = r.id "
            "JOIN comunas m ON b.comuna_id = m.id "
            "WHERE o.id = ?",
            (order_id,),
        ).fetchone()
        if not order:
            raise ValueError(f"Orden no encontrada: {order_id}")

        items = cur.execute(
            "SELECT oi.sku, oi.cantidad, oi.precio_unitario, oi.descuento, p.nombre AS producto "
            "FROM order_items oi "
            "JOIN products p ON oi.sku = p.sku "
            "WHERE oi.order_id = ?",
            (order_id,),
        ).fetchall()

        return {
            'order': dict(order),
            'items': [dict(item) for item in items],
        }


def create_order_by_branch_code(branch_code: str, items: List[Tuple[str, int]], cliente_nombre: Optional[str] = None) -> int:
    branch = get_branch_by_code(branch_code)
    if not branch:
        raise ValueError(f"No encontré la sucursal con código '{branch_code}'.")
    return create_order(branch['id'], items, cliente_nombre)


def get_branch_inventory(branch_id: int) -> List[Dict[str, Any]]:
    """Devuelve el inventario de una sucursal con stock por producto."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = cur.execute(
            """
            SELECT p.sku, p.nombre, p.precio_lista, p.descuento_efectivo,
                   c.nombre AS categoria, i.cantidad
            FROM inventory i
            JOIN products p ON i.sku = p.sku
            JOIN categories c ON p.category_id = c.id
            WHERE i.branch_id = ?
            ORDER BY p.nombre
            """,
            (branch_id,),
        ).fetchall()
        return [dict(row) for row in rows]
