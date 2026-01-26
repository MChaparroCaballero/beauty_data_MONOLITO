from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, field_validator, ValidationError
from typing import Optional, List
import re

# Importamos las funciones que consultan/insertan/eliminan en MySQL
from app.database import (
    fetch_all_productos, 
    insert_producto, 
    delete_producto,
    fetch_producto_by_cod,
    update_producto
)


# Modelo base con validaciones comunes
class ProductoBase(BaseModel):
    nombre: str
    categoria: str
    descripcion: str
    precio_compra: float
    precio_venta: float
    stock: int
    proveedor: str
    estado: str = 'Activo'
    


    
    @field_validator('nombre', 'categoria', 'descripcion', 'proveedor')
    @classmethod
    def validar_strings(cls, v: str) -> str:
        """Valida que los campos de texto tengan formato correcto."""
        if not v or not v.strip():
            raise ValueError('El campo no puede estar vacío')
        
        v = v.strip()
        
        if len(v) > 200:
            raise ValueError('No puede exceder 200 caracteres')
        
        return v
    
    @field_validator('precio_compra', 'precio_venta')
    @classmethod
    def validar_precios(cls, v: float) -> float:
        """Valida que los precios sean positivos."""
        if v < 0:
            raise ValueError('El precio no puede ser negativo')
        return v
    
    @field_validator('stock')
    @classmethod
    def validar_stock(cls, v: int) -> int:
        """Valida que el stock sea no negativo."""
        if v < 0:
            raise ValueError('El stock no puede ser negativo')
        return v
    
    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: str) -> str:
        """Valida que el estado sea válido."""
        if v not in ['Activo', 'Agotado', 'Inactivo']:
            raise ValueError('Estado debe ser Activo, Agotado o Inactivo')
        return v


# Modelo para lectura de BD (sin validaciones estrictas, acepta datos históricos)
class ProductoDB(BaseModel):
    COD: int
    NOMBRE: str
    Categoria: str
    Descripción: str
    Precio_de_compra: float
    Precio_de_venta: float
    Stock: int
    Proveedor: str
    Estado: str


# Modelo para crear producto (sin COD)
class ProductoCreate(ProductoBase):
    pass


# Modelo para actualizar producto (sin COD)
class ProductoUpdate(ProductoBase):
    pass


# Modelo completo de Producto (con COD y validaciones)
class Producto(ProductoBase):
    COD: int


app = FastAPI(title="SumaAPI")

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Motor de plantillas
templates = Jinja2Templates(directory="app/templates")


def map_rows_to_productos(rows: List[dict]) -> List[ProductoDB]:
    """
    Convierte las filas del SELECT * FROM productos (dict) 
    en objetos ProductoDB (sin validaciones estrictas para datos existentes).
    """
    return [
        ProductoDB(
            COD=row["COD"],
            NOMBRE=row["NOMBRE"],
            Categoria=row["Categoria"],
            Descripción=row["Descripción"],
            Precio_de_compra=row["Precio_de_compra"],
            Precio_de_venta=row["Precio_de_venta"],
            Stock=row["Stock"],
            Proveedor=row["Proveedor"],
            Estado=row["Estado"],
        )
        for row in rows
    ]


# --- GET principal ---
@app.get("/", response_class=HTMLResponse)
def get_index(request: Request):
    # 1️⃣ Obtenemos los datos desde MySQL
    rows = fetch_all_productos()

    # 2️⃣ Convertimos cada fila a Producto (valida estructura)
    productos = map_rows_to_productos(rows)

    # 3️⃣ Enviamos a la plantilla
    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "productos": productos
        }
    )


# --- GET formulario nuevo cliente ---
@app.get("/productos/nuevo", response_class=HTMLResponse)
def get_nuevo_producto(request: Request):
    return templates.TemplateResponse(
        "pages/nuevo_producto.html",
        {
            "request": request,
            "mensaje": None
        }
    )


# --- POST guardar nuevo producto ---
@app.post("/productos/nuevo")
def post_nuevo_producto(
    request: Request,
    nombre: str = Form(...),
    categoria: str = Form(...),
    descripcion: str = Form(...),
    precio_compra: float = Form(...),
    precio_venta: float = Form(...),
    stock: int = Form(...),
    proveedor: str = Form(...),
    estado: str = Form('Activo')
):
    try:
        # Validamos los datos usando Pydantic
        producto_data = ProductoCreate(
            nombre=nombre,
            categoria=categoria,
            descripcion=descripcion,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            stock=stock,
            proveedor=proveedor,
            estado=estado
        )
        
        # Insertamos el producto en la base de datos
        insert_producto(
            producto_data.nombre,
            producto_data.categoria,
            producto_data.descripcion,
            producto_data.precio_compra,
            producto_data.precio_venta,
            producto_data.stock,
            producto_data.proveedor,
            producto_data.estado
        )
        
        # Redirigimos al inicio para ver el listado actualizado
        return RedirectResponse(url="/", status_code=303)
        
    except ValidationError as e:
        # Extraemos los errores de validación
        errores = []
        for error in e.errors():
            campo = str(error['loc'][0]) if error['loc'] else 'campo'
            mensaje = error['msg']
            errores.append(f"{campo.capitalize()}: {mensaje}")
        
        # Mostramos el formulario con los errores
        return templates.TemplateResponse(
            "pages/nuevo_producto.html",
            {
                "request": request,
                "mensaje": None,
                "errores": errores,
                "nombre": nombre,
                "categoria": categoria,
                "descripcion": descripcion,
                "precio_compra": precio_compra,
                "precio_venta": precio_venta,
                "stock": stock,
                "proveedor": proveedor,
                "estado": estado
            },
            status_code=422
        )


# --- DELETE eliminar producto ---
@app.delete("/productos/{producto_cod}")
def delete_producto_endpoint(producto_cod: int):
    """
    Endpoint para eliminar un producto por su COD.
    """
    eliminado = delete_producto(producto_cod)
    
    if not eliminado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return JSONResponse(
        content={"mensaje": "Producto eliminado exitosamente"},
        status_code=200
    )


# --- GET formulario editar producto ---
@app.get("/productos/editar/{producto_cod}", response_class=HTMLResponse)
def get_editar_producto(request: Request, producto_cod: int):
    """
    Endpoint para mostrar el formulario de edición con datos precargados.
    """
    # Obtenemos los datos del producto
    producto_data = fetch_producto_by_cod(producto_cod)
    
    if not producto_data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Convertimos a modelo ProductoDB para mostrar en formulario (sin validaciones)
    producto = ProductoDB(**producto_data)
    
    return templates.TemplateResponse(
        "pages/editar_producto.html",
        {
            "request": request,
            "producto": producto
        }
    )


# --- POST actualizar producto ---
@app.post("/productos/editar/{producto_cod}")
def post_editar_producto(
    request: Request,
    producto_cod: int,
    nombre: str = Form(...),
    categoria: str = Form(...),
    descripcion: str = Form(...),
    precio_compra: float = Form(...),
    precio_venta: float = Form(...),
    stock: int = Form(...),
    proveedor: str = Form(...),
    estado: str = Form(...)
):
    """
    Endpoint para actualizar los datos de un producto.
    """
    try:
        # Validamos los datos usando Pydantic
        producto_data = ProductoUpdate(
            nombre=nombre,
            categoria=categoria,
            descripcion=descripcion,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            stock=stock,
            proveedor=proveedor,
            estado=estado
        )
        
        # Actualizamos el producto en la base de datos
        actualizado = update_producto(
            producto_cod,
            producto_data.nombre,
            producto_data.categoria,
            producto_data.descripcion,
            producto_data.precio_compra,
            producto_data.precio_venta,
            producto_data.stock,
            producto_data.proveedor,
            producto_data.estado
        )
        
        if not actualizado:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Redirigimos al inicio para ver el listado actualizado
        return RedirectResponse(url="/", status_code=303)
        
    except ValidationError as e:
        # Extraemos los errores de validación
        errores = []
        for error in e.errors():
            campo = str(error['loc'][0]) if error['loc'] else 'campo'
            mensaje = error['msg']
            errores.append(f"{campo.capitalize()}: {mensaje}")
        
        # Creamos un objeto producto temporal para mostrar en el formulario
        producto_temp = ProductoDB(
            COD=producto_cod,
            NOMBRE=nombre,
            Categoria=categoria,
            Descripción=descripcion,
            Precio_de_compra=precio_compra,
            Precio_de_venta=precio_venta,
            Stock=stock,
            Proveedor=proveedor,
            Estado=estado
        )
        
        # Mostramos el formulario con los errores
        return templates.TemplateResponse(
            "pages/editar_producto.html",
            {
                "request": request,
                "producto": producto_temp,
                "errores": errores
            },
            status_code=422
        )