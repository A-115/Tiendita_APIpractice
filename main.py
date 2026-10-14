import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class Producto(BaseModel):
    id: Optional[int] = None
    nombre: str
    precio: float

inventario = [
    {"id": 1, "nombre": "Coca-Cola", "precio": 20, "cantidad": 25},
    {"id": 2, "nombre": "Papas", "precio": 15, "cantidad": 40},
    {"id": 3, "nombre": "Café", "precio": 18, "cantidad": 15}
]

base_datos_productos: List[dict] = [
    {"id": 1, "nombre": "Manzana", "precio": 15.5},
    {"id": 2, "nombre": "Leche", "precio": 24.0},
]
# Base de datos asíncrona simulada (simula lectura/escritura en DB o disco) 
async def simular_operacion_db():
    await asyncio.sleep(0.05)  # Simulamos una E/S asíncrona (I/O)
    
@app.get("/")
def home():
    return {"Message": "Hola bienvenido"}

@app.get("/productos")
def getProductos():
    return inventario

@app.post("/productos")
def addProducto(producto: dict):

    nuevo_id = len(inventario) + 1
    nuevo_producto = {
        "id": nuevo_id,    
        "nombre": producto["nombre"],
        "precio": producto["precio"],
        "cantidad": producto["cantidad"]
    }

    inventario.append(nuevo_producto)

    return inventario

@app.delete("/productos/{producto_id}")
def deleteProducto(producto_id: int):
    for producto in inventario:
        if producto["id"] == producto_id:
            inventario.remove(producto)
            return {"Message": "El producto fue eliminado"}
    return {"Message": "No fue encontrado el producto"}



# ---------------------------------------------------------
# 1. Endpoint GET: Obtener todos los productos (async/await)
# ---------------------------------------------------------
@app.get("/productos", response_model=List[dict])
async def obtener_productos():
    # USAMOS AWAIT: Simulamos la consulta asíncrona a la base de datos
    await simular_operacion_db()
    return base_datos_productos


# ---------------------------------------------------------
# 2. Endpoint POST: Crear producto (async SIN await interno)
# ---------------------------------------------------------
@app.post("/productos", status_code=status.HTTP_201_CREATED)
async def crear_producto(producto: Producto):
    # NO USAMOS AWAIT AQUÍ: La generación del ID y la inserción en memoria
    # son operaciones en CPU ultra-rápidas y puramente sincrónicas.
    nuevo_id = len(base_datos_productos) + 1 if base_datos_productos else 1
    nuevo_producto = {"id": nuevo_id, "nombre": producto.nombre, "precio": producto.precio}
    base_datos_productos.append(nuevo_producto)
    return nuevo_producto


# ---------------------------------------------------------
# 3. Endpoint DELETE: Eliminar producto por ID (async con await opcional)
# ---------------------------------------------------------
@app.delete("/productos/{producto_id}")
async def eliminar_producto(producto_id: int):
    # Búsqueda en memoria (operación sincrónica)
    global base_datos_productos
    producto_existente = next((p for p in base_datos_productos if p["id"] == producto_id), None)
    
    if not producto_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado"
        )
    
    # USAMOS AWAIT: Simulamos el borrado persistente en la base de datos
    await simular_operacion_db()
    
    base_datos_productos = [p for p in base_datos_productos if p["id"] != producto_id]
    return {"mensaje": f"Producto con ID {producto_id} eliminado exitosamente"}
