import uvicorn
import webbrowser
import time
import threading

def abrir_navegador():
    """Espera un par de segundos a que el servidor levante y abre el navegador."""
    time.sleep(2)
    print("\nAbriendo la cafetería en tu navegador...")
    webbrowser.open("http://127.0.0.1:8000/")

if __name__ == "__main__":
    print("===================================================")
    print("☕ Iniciando el sistema de L'Espresso (Tiendita API)")
    print("===================================================\n")
    
    # Inicia un hilo secundario para abrir el navegador automáticamente
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    # Arranca el servidor Uvicorn programáticamente
    # Nota: El parámetro reload=True requiere que el primer argumento sea un string "archivo:app"
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True
    )