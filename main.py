import os
import pandas as pd
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(title="API Cafetería Gourmet")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

ARCHIVO_PRODUCTOS = "productos.csv"
ARCHIVO_VENTAS = "ventas.csv"

class Producto(BaseModel):
    nombre: str
    precio: float
    cantidad: int = 10 # Cantidad inicial por defecto

#  Inicialización de persistencia
def inicializar_csv():
    """Verifica si existen los CSV. Si no, los crea con datos por defecto."""
    if not os.path.exists(ARCHIVO_PRODUCTOS):
        datos_iniciales = {
            "id": [1],
            "nombre": ["Espresso de Origen"],
            "precio": [45.0],
            "cantidad": [50]
        }
        df = pd.DataFrame(datos_iniciales)
        df.to_csv(ARCHIVO_PRODUCTOS, index=False)
        print(f"Archivo {ARCHIVO_PRODUCTOS} creado con éxito.")
        
        if not os.path.exists(ARCHIVO_VENTAS):
            df_ventas = pd.DataFrame(columns=["fecha", "producto_id", "nombre", "precio", "cantidad", "monto_total"])
            df_ventas.to_csv(ARCHIVO_VENTAS, index=False)
            
        print(f"Archivo {ARCHIVO_VENTAS} creado con éxito.")
        
inicializar_csv()


###    Endpoints de la API

# Página principal de bienvenida (Portada)
@app.get("/")
def pagina_principal():
    return FileResponse("index.html")

@app.get("/app.js")
def archivo_javascript_dashboard():
    return FileResponse("app.js")

@app.get("/kiosco.js")
def archivo_javascript_cliente():
    return FileResponse("kiosco.js")

# Página del Dashboard
@app.get("/dashboard")
def pagina_dashboard():
    return FileResponse("dashboard-cafe.html")
@app.get("/dashboard")
def pagina_dashboard_admin():
    return FileResponse("dashboard-cafe.html")
# Endpoints CRUD interactuando con CSV
@app.get("/productos")
def obtener_productos():
    df = pd.read_csv(ARCHIVO_PRODUCTOS)
    return df.to_dict(orient="records")

@app.post("/productos", status_code=status.HTTP_201_CREATED)
def crear_producto(producto: Producto):
    df = pd.read_csv(ARCHIVO_PRODUCTOS)
    
    nuevo_id = int(df["id"].max() + 1) if not df.empty else 1
    nuevo_registro = {
        "id": nuevo_id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "cantidad": producto.cantidad
    }
    
    # Agregamos la fila y sobreescribimos el archivo
    df.loc[len(df)] = nuevo_registro
    df.to_csv(ARCHIVO_PRODUCTOS, index=False)
    
    return nuevo_registro

@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    df = pd.read_csv(ARCHIVO_PRODUCTOS)
    
    if producto_id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Filtramos conservando solo los que no coinciden con el ID
    df = df[df["id"] != producto_id]
    df.to_csv(ARCHIVO_PRODUCTOS, index=False)
    
    return {"mensaje": f"Producto {producto_id} eliminado exitosamente"}

@app.post("/productos/{producto_id}")
def comprar_producto(producto_id: int):
    df = pd.read_csv(ARCHIVO_PRODUCTOS)
    
    if producto_id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Producto no existe")
    
    # Obtenemos el índice numérico de la fila donde está el producto
    indice = df.index[df["id"] == producto_id].tolist()[0]
    
    if df.at[indice, "cantidad"] > 0:
        # Descuenta 1 unidad y guarda el archivo de productos
        df.at[indice, "cantidad"] -= 1
        df.to_csv(ARCHIVO_PRODUCTOS, index=False)
        
        # Extraemos los datos para el ticket
        producto_nombre = df.at[indice, "nombre"]
        producto_precio = float(df.at[indice, "precio"])
        
        # Registramos la transacción en ventas.csv
        df_ventas = pd.read_csv(ARCHIVO_VENTAS)
        nueva_venta = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "producto_id": producto_id,
            "nombre": producto_nombre,
            "precio": producto_precio,
            "cantidad": 1,
            "monto_total": producto_precio
        }
        df_ventas.loc[len(df_ventas)] = nueva_venta
        df_ventas.to_csv(ARCHIVO_VENTAS, index=False)
        
        return {"mensaje": "Compra registrada con éxito"}
    else:
        raise HTTPException(status_code=400, detail="Stock agotado")
    
    
# Analitica de ventas 

@app.get("/analiticas/kpis")
def obtener_kpis():
    df_ventas = pd.read_csv(ARCHIVO_VENTAS)
    if df_ventas.empty:
        return {"favorito": "Sin ventas", "ingresos": 0.0, "ordenes": 0}

    ingresos_totales = float(df_ventas["monto_total"].sum())
    ordenes_totales = int(len(df_ventas))
    
    ventas_por_producto = df_ventas.groupby("nombre")["cantidad"].sum()
    favorito = ventas_por_producto.idxmax() if not ventas_por_producto.empty else "Sin ventas"

    return {"favorito": favorito, "ingresos": ingresos_totales, "ordenes": ordenes_totales}

@app.get("/analiticas/graficas")
def obtener_datos_graficas():
    if not os.path.exists(ARCHIVO_VENTAS):
        return {"barras": {"labels": [], "data": []}, "pastel": {"labels": [], "data": []}}

    df_ventas = pd.read_csv(ARCHIVO_VENTAS)
    if df_ventas.empty:
        return {"barras": {"labels": [], "data": []}, "pastel": {"labels": [], "data": []}}

    # Agrupación para gráfica de barras: Ingresos por especialidad
    ingresos_prod = df_ventas.groupby("nombre")["monto_total"].sum().reset_index()
    
    # Agrupación para gráfica de pastel: Cantidad de ventas por producto
    cantidad_prod = df_ventas.groupby("nombre")["cantidad"].sum().reset_index()

    return {
        "barras": {
            "labels": ingresos_prod["nombre"].tolist(),
            "data": ingresos_prod["monto_total"].tolist()
        },
        "pastel": {
            "labels": cantidad_prod["nombre"].tolist(),
            "data": cantidad_prod["cantidad"].tolist()
        }
    }