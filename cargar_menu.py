import csv
import requests
import time

# URL de tu API local
API_URL = "http://localhost:8000/productos"

def cargar_productos_desde_csv(ruta_csv):
    """
    Lee un archivo CSV y realiza peticiones POST a la API para registrar cada producto.
    """
    productos_agregados = 0
    errores = 0

    try:
        with open(ruta_csv, mode='r', encoding='utf-8') as archivo:
            lector_csv = csv.DictReader(archivo)
            
            print("Iniciando la carga de productos al servidor...")
            for fila in lector_csv:
                # Preparamos el payload en el formato que espera tu Pydantic BaseModel
                # Nota: Tu API actual solo espera 'nombre' y 'precio', ignorará el ID y la cantidad por ahora.
                payload = {
                    "nombre": fila["nombre"],
                    "precio": float(fila["precio"])
                }
                
                # Realizar la petición POST
                respuesta = requests.post(API_URL, json=payload)
                
                if respuesta.status_code == 201:
                    productos_agregados += 1
                    print(f"[{productos_agregados}] Agregado exitosamente: {fila['nombre']}")
                elif respuesta.status_code == 429:
                    # Manejo del Rate Limiting (Too Many Requests)
                    print(f"⚠️ Rate limit alcanzado al intentar agregar {fila['nombre']}. Esperando 1 segundo...")
                    time.sleep(1) # Pausa para respetar el límite de 5 peticiones por segundo
                    
                    # Reintentar la misma petición después de la pausa
                    retry = requests.post(API_URL, json=payload)
                    if retry.status_code == 201:
                        productos_agregados += 1
                        print(f"[{productos_agregados}] Agregado exitosamente tras reintento: {fila['nombre']}")
                    else:
                        errores += 1
                        print(f" Error al reintentar {fila['nombre']}: Código {retry.status_code}")
                else:
                    errores += 1
                    print(f" Error al agregar {fila['nombre']}: Código {respuesta.status_code}")
                    
                # Pequeña pausa para no saturar el Rate Limiting (máximo 5 pet/seg)
                time.sleep(0.25)
                
        print("\n--- Resumen de la carga ---")
        print(f"Total productos agregados: {productos_agregados}")
        print(f"Total errores: {errores}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_csv}'. Asegúrate de que esté en la misma ruta.")
    except KeyError as e:
         print(f"Error en el formato del CSV: Falta la columna {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    # Asegúrate de que el nombre coincida con tu archivo CSV real
    cargar_productos_desde_csv("productos.csv")