const API_URL = "http://127.0.0.1:8000";
let menuCompleto = [];
let carrito = [];

// 1. Cargar el menú desde el backend
async function cargarMenu() {
    try {
        const res = await fetch(`${API_URL}/productos`);
        menuCompleto = await res.json();
        renderizarCatalogo(menuCompleto);
    } catch (error) {
        console.error("Error al cargar el menú:", error);
        document.getElementById("catalogo-contenedor").innerHTML = 
            `<div class="col-12 text-center text-danger">Error al conectar con el servidor.</div>`;
    }
}

// 2. Mostrar productos en pantalla
function renderizarCatalogo(productos) {
    const contenedor = document.getElementById("catalogo-contenedor");
    contenedor.innerHTML = "";

    if (productos.length === 0) {
        contenedor.innerHTML = `<div class="col-12 text-center text-muted">No hay productos disponibles por el momento.</div>`;
        return;
    }

    productos.forEach(p => {
        // Solo mostramos productos que tengan stock disponible
        if (p.cantidad > 0) {
            const card = document.createElement("div");
            card.className = "col-md-6 col-lg-4";
            card.innerHTML = `
                <div class="producto-card p-3 border rounded shadow-sm bg-white h-100 d-flex flex-column justify-content-between">
                    <div>
                        <h6 class="mb-1 fw-bold">${p.nombre}</h6>
                        <span class="badge bg-light text-dark mb-2 border">Disponibles: ${p.cantidad}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <span class="precio text-success fw-bold">$${p.precio.toFixed(2)}</span>
                        <button class="btn btn-sm btn-outline-primary rounded-circle" onclick="agregarAlCarrito(${p.id}, '${p.nombre}', ${p.precio})">
                            <i class="bi bi-plus-lg"></i> +
                        </button>
                    </div>
                </div>
            `;
            contenedor.appendChild(card);
        }
    });
}

// Búsqueda y filtrado en tiempo real
const buscador = document.getElementById("buscador");
if (buscador) {
    buscador.addEventListener("input", (e) => {
        const texto = e.target.value.toLowerCase();
        const filtrados = menuCompleto.filter(p => p.nombre.toLowerCase().includes(texto));
        renderizarCatalogo(filtrados);
    });
}

// 3. Lógica del Carrito de Compras
function agregarAlCarrito(id, nombre, precio) {
    carrito.push({ id, nombre, precio });
    actualizarCarrito();
}

function actualizarCarrito() {
    const lista = document.getElementById("lista-carrito");
    const labelTotal = document.getElementById("total-carrito");
    
    lista.innerHTML = "";
    let total = 0;

    if (carrito.length === 0) {
        lista.innerHTML = `<li class="list-group-item text-muted small text-center">El carrito está vacío</li>`;
    } else {
        carrito.forEach((item, index) => {
            total += item.precio;
            lista.innerHTML += `
                <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                    <span class="small text-truncate" style="max-width: 150px;">${item.nombre}</span>
                    <div class="text-end">
                        <span class="fw-bold me-2">$${item.precio.toFixed(2)}</span>
                        <button class="btn btn-sm text-danger p-0 ms-2" onclick="quitarDelCarrito(${index})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </li>
            `;
        });
    }
    
    if (labelTotal) {
        labelTotal.textContent = `$${total.toFixed(2)}`;
    }
}

function quitarDelCarrito(index) {
    carrito.splice(index, 1);
    actualizarCarrito();
}

// 4. Procesar el pago (Consumir API)
async function procesarPago() {
    if (carrito.length === 0) {
        alert("Tu carrito está vacío. Agrega productos para ordenar.");
        return;
    }

    const btn = document.getElementById("btn-pagar");
    if (btn) {
        btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...`;
        btn.disabled = true;
    }

    try {
        // Enviar una petición POST individual por cada artículo para descontarlo de la base de datos (CSV)
        for (const item of carrito) {
            await fetch(`${API_URL}/productos/${item.id}`, { 
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });
        }
        
        alert("¡Compra procesada con éxito! Tu orden se está preparando.");
        carrito = []; 
        actualizarCarrito();
        
        // Recargar el menú para reflejar el nuevo stock (cantidades actualizadas)
        await cargarMenu(); 
    } catch (error) {
        console.error("Error al procesar el pago", error);
        alert("Hubo un problema de conexión al procesar la orden.");
    } finally {
        if (btn) {
            btn.innerHTML = `<i class="bi bi-credit-card me-2"></i> Pagar Orden`;
            btn.disabled = false;
        }
    }
}

// Inicializar la vista cargando el catálogo
document.addEventListener("DOMContentLoaded", cargarMenu);
