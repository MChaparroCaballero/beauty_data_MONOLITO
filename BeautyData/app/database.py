from dotenv import load_dotenv, find_dotenv
import os
import mysql.connector
from typing import List, Dict, Any, cast
from mysql.connector.cursor import MySQLCursorDict  # opción C si la prefieres

# Carga .env desde la raíz
load_dotenv(find_dotenv())

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),        # <— corregidos nombres
        user=os.getenv("DB_USER", "beauty_data"),
        password=os.getenv("DB_PASSWORD", "beauty_data"),
        database=os.getenv("DB_NAME", "beauty_data"),
        port=int(os.getenv("DB_PORT", "3307")),
        charset="utf8mb4"
    )

def fetch_all_productos() -> List[Dict[str, Any]]:
    """
    Ejecuta SELECT * FROM productos y devuelve una lista de dicts.
    """
    conn = None
    try:
        conn = get_connection()
        # Opción C (anotación explícita del cursor):
        cur: MySQLCursorDict
        cur = conn.cursor(dictionary=True)  # type: ignore[assignment]
        try:
            cur.execute(
                "SELECT COD, NOMBRE, Categoria, Descripción, Precio_de_compra, Precio_de_venta, Stock, Proveedor, Estado FROM productos;"
            )
            # Opción A: cast para contentar al type checker
            rows = cast(List[Dict[str, Any]], cur.fetchall())
            return rows

            # Opción B alternativa (sin cast):
            # return [dict(row) for row in cur.fetchall()]
        finally:
            cur.close()
    finally:
        if conn:
            conn.close()


def insert_producto(
    nombre: str, 
    categoria: str, 
    descripcion: str, 
    precio_compra: float, 
    precio_venta: float, 
    stock: int, 
    proveedor: str, 
    estado: str = 'Activo'
) -> int:
    """
    Inserta un nuevo producto en la base de datos.
    Retorna el COD del producto insertado.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO productos (NOMBRE, Categoria, Descripción, Precio_de_compra, Precio_de_venta, Stock, Proveedor, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (nombre, categoria, descripcion, precio_compra, precio_venta, stock, proveedor, estado)
            )
            conn.commit()
            return cur.lastrowid or 0
        finally:
            cur.close()
    finally:
        if conn:
            conn.close()


def delete_producto(producto_cod: int) -> bool:
    """
    Elimina un producto de la base de datos por su COD.
    Retorna True si se eliminó correctamente, False si no se encontró.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "DELETE FROM productos WHERE COD = %s",
                (producto_cod,)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
    finally:
        if conn:
            conn.close()


def fetch_producto_by_cod(producto_cod: int) -> Dict[str, Any] | None:
    """
    Obtiene un producto por su COD.
    Retorna un dict con los datos del producto o None si no existe.
    """
    conn = None
    try:
        conn = get_connection()
        cur: MySQLCursorDict
        cur = conn.cursor(dictionary=True)  # type: ignore[assignment]
        try:
            cur.execute(
                "SELECT COD, NOMBRE, Categoria, Descripción, Precio_de_compra, Precio_de_venta, Stock, Proveedor, Estado FROM productos WHERE COD = %s",
                (producto_cod,)
            )
            result = cur.fetchone()
            return dict(result) if result else None
        finally:
            cur.close()
    finally:
        if conn:
            conn.close()


def update_producto(
    producto_cod: int,
    nombre: str,
    categoria: str,
    descripcion: str,
    precio_compra: float,
    precio_venta: float,
    stock: int,
    proveedor: str,
    estado: str
) -> bool:
    """
    Actualiza los datos de un producto existente.
    Retorna True si se actualizó correctamente, False si no se encontró.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE productos 
                SET NOMBRE = %s, Categoria = %s, Descripción = %s, Precio_de_compra = %s, Precio_de_venta = %s, Stock = %s, Proveedor = %s, Estado = %s
                WHERE COD = %s
                """,
                (nombre, categoria, descripcion, precio_compra, precio_venta, stock, proveedor, estado, producto_cod)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
    finally:
        if conn:
            conn.close()
