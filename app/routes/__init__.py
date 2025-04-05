"""
Inicialización del paquete de rutas.
Este paquete contiene los blueprints que definen las rutas de la aplicación.
"""

# Importar módulos de rutas para asegurar que estén disponibles
from app.routes import (
    home_routes,
    product_routes,
    auth_routes,
    category_routes,
    pos_routes,
    cashier_routes,
    customer_routes
) 