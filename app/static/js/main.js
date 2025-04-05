/**
 * PyPOS Local - JavaScript principal
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('PyPOS Local - Aplicación cargada');
    
    // Habilitar todos los tooltips de Bootstrap
    var tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltips.length > 0) {
        tooltips.forEach(function(tooltip) {
            new bootstrap.Tooltip(tooltip);
        });
    }
    
    // Habilitar todos los popovers de Bootstrap
    var popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popovers.length > 0) {
        popovers.forEach(function(popover) {
            new bootstrap.Popover(popover);
        });
    }
    
    // Formatear números como moneda
    function formatCurrency(element) {
        if (!element) return;
        
        const value = parseFloat(element.textContent);
        if (!isNaN(value)) {
            element.textContent = new Intl.NumberFormat('es-AR', {
                style: 'currency',
                currency: 'ARS'
            }).format(value);
        }
    }
    
    // Aplicar formato de moneda a elementos con la clase .currency
    document.querySelectorAll('.currency').forEach(formatCurrency);
    
    // Función para confirmación genérica
    window.confirmAction = function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    };
    
    // Manejador para botones de borrado con confirmación
    document.querySelectorAll('.btn-delete-confirm').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            const item = this.getAttribute('data-item') || 'item';
            
            confirmAction(`¿Estás seguro de que quieres eliminar este ${item}?`, function() {
                window.location.href = url;
            });
        });
    });
    
    // Implementación básica de búsqueda en tablas
    const tableSearch = document.getElementById('table-search');
    if (tableSearch) {
        tableSearch.addEventListener('keyup', function() {
            const searchText = this.value.toLowerCase();
            const table = document.querySelector(this.getAttribute('data-table') || 'table');
            if (!table) return;
            
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchText) ? '' : 'none';
            });
        });
    }
});

/**
 * Función para agregar un producto al carrito de compras
 * @param {number} productId - ID del producto
 * @param {string} productName - Nombre del producto
 * @param {number} price - Precio del producto
 * @param {number} [quantity=1] - Cantidad a agregar
 */
function addToCart(productId, productName, price, quantity = 1) {
    console.log(`Agregando al carrito: ${quantity} x ${productName} ($${price})`);
    // Esta función se implementará cuando se desarrolle la funcionalidad del PDV
    // Por ahora solo registra en consola
}

/**
 * Función para mostrar notificaciones
 * @param {string} message - Mensaje a mostrar
 * @param {string} [type='info'] - Tipo de notificación (info, success, warning, error)
 * @param {number} [duration=3000] - Duración en milisegundos
 */
function showNotification(message, type = 'info', duration = 3000) {
    // Crear el elemento de notificación
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Agregar al contenedor de notificaciones o al body
    const container = document.getElementById('notification-container') || document.body;
    container.appendChild(notification);
    
    // Eliminar después de la duración especificada
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, duration);
} 