from locust import HttpUser, task, between
import random

class UsuarioTienditaCompleto(HttpUser):
    # Intervalo de descanso aleatorio entre peticiones por usuario[cite: 8]
    wait_time = between(0.2, 0.8)

    @task(1)
    def comprarProducto(self):
        # Selecciona un ID aleatorio o apunta al producto crítico (ID 3: Café)
        producto_id = random.randint(1, 3)
        
        # catch_response=True evita que el código 400 (sin stock) se registre como fallo en Locust[cite: 8]
        with self.client.post(f"/productos/{producto_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400:
                # El 400 es un comportamiento de negocio esperado al agotarse el stock
                response.success()

    @task(3)
    def getProductos(self):
        # Simula la consulta del catálogo de productos (lectura)[cite: 6, 8]
        self.client.get("/productos")