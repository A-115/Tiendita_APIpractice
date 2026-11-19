const API_URL = "http://127.0.0.1:8000";

// Elementos del DOM
const formProducto = document.getElementById("formProducto");
const tablaProductos = document.getElementById("tablaProductos");
const totalProductos = document.getElementById("totalProductos");

// Variables globales para destruir las gráficas previas (Requisito de Chart.js)
let graficaBarrasInstancia = null;
let graficaPastelInstancia = null;

// 1. Cargar el Catálogo (CRUD)
async function cargarProductos() {
    try {
        const respuesta = await fetch(`${API_URL}/productos`);
        const productos = await respuesta.json();

        tablaProductos.innerHTML = "";
        totalProductos.textContent = `${productos.length} productos`;

        if (productos.length === 0) {
            tablaProductos.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">Inventario vacío.</td></tr>`;
            return;
        }

        productos.forEach(p => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td class="fw-bold text-secondary">#${p.id}</td>
                <td>${p.nombre}</td>
                <td class="text-success fw-bold">$${p.precio.toFixed(2)}</td>
                <td>
                    <span class="badge ${p.cantidad < 5 ? 'bg-danger' : 'bg-success'}">
                        ${p.cantidad}
                    </span>
                </td>
                <td class="text-end">
                    <button class="btn btn-outline-primary btn-sm me-1" onclick="comprarProducto(${p.id})">
                        <i class="bi bi-cart-plus"></i> Servir
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="eliminarProducto(${p.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
            tablaProductos.appendChild(fila);
        });
    } catch (error) {
        console.error("Error al cargar productos:", error);
    }
}

// 2. Cargar KPIs y Gráficas (Dashboard Analítico)
async function cargarDashboard() {
    try {
        // --- Cargar KPIs ---
        const resKpis = await fetch(`${API_URL}/analiticas/kpis`);
        const kpis = await resKpis.json();
        
        document.getElementById("kpi-favorito").textContent = kpis.favorito;
        document.getElementById("kpi-ingresos").textContent = `$${kpis.ingresos.toFixed(2)}`;
        document.getElementById("kpi-ordenes").textContent = kpis.ordenes;

        // --- Cargar Gráficas ---
        const resGraficas = await fetch(`${API_URL}/analiticas/graficas`);
        const datosGraficas = await resGraficas.json();

        renderizarGraficas(datosGraficas);
    } catch (error) {
        console.error("Error al cargar analíticas:", error);
    }
}

// 3. Renderizar Chart.js
function renderizarGraficas(datos) {
    // Destruir instancias previas para evitar sobreescritura de canvas
    if (graficaBarrasInstancia) graficaBarrasInstancia.destroy();
    if (graficaPastelInstancia) graficaPastelInstancia.destroy();

    // Colores cálidos estilo Gourmet
    const colores = ['#C5A059', '#8B4513', '#2C1E16', '#EBE3D5', '#A67B5B'];

    // Gráfica de Barras
    const ctxBarras = document.getElementById('graficaBarras').getContext('2d');
    graficaBarrasInstancia = new Chart(ctxBarras, {
        type: 'bar',
        data: {
            labels: datos.barras.labels,
            datasets: [{
                label: 'Ingresos ($)',
                data: datos.barras.data,
                backgroundColor: '#C5A059',
                borderRadius: 4
            }]
        }
    });

    // Gráfica de Pastel (Doughnut)
    const ctxPastel = document.getElementById('graficaPastel').getContext('2d');
    graficaPastelInstancia = new Chart(ctxPastel, {
        type: 'doughnut',
        data: {
            labels: datos.pastel.labels,
            datasets: [{
                data: datos.pastel.data,
                backgroundColor: colores,
                borderWidth: 0
            }]
        }
    });
}

// 4. Operaciones CRUD que refrescan toda la vista
async function agregarProducto(event) {
    event.preventDefault();
    const nuevoContenido = {
        nombre: document.getElementById("nombre").value,
        precio: parseFloat(document.getElementById("precio").value),
        cantidad: parseInt(document.getElementById("cantidad").value)
    };

    try {
        await fetch(`${API_URL}/productos`, {
            method: "POST", 
            headers: {"Content-Type": "application/json"}, 
            body: JSON.stringify(nuevoContenido)
        });
        formProducto.reset();
        await actualizarVistaCompleta();
    } catch (error) {
        console.error("Error al guardar", error);
    }
}

async function eliminarProducto(id) {
    try {
        await fetch(`${API_URL}/productos/${id}`, { method: "DELETE" });
        await actualizarVistaCompleta();
    } catch (error) {
        console.error("Error al eliminar", error);
    }
}

async function comprarProducto(id) {
    try {
        const respuesta = await fetch(`${API_URL}/productos/${id}`, { method: "POST" });
        if(respuesta.ok) {
            await actualizarVistaCompleta();
        } else {
            alert("Stock agotado para este producto.");
        }
    } catch (error) {
        console.error("Error en la compra", error);
    }
}

// Función maestra para refrescar todo
async function actualizarVistaCompleta() {
    await cargarProductos();
    await cargarDashboard();
}

// Inicializadores
document.addEventListener("DOMContentLoaded", actualizarVistaCompleta);
formProducto.addEventListener("submit", agregarProducto);
