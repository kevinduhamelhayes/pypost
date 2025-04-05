"""
Inicialización del paquete de rutas.
Este paquete contiene los blueprints que definen las rutas de la aplicación.
"""

# Importar los blueprints directamente
from .home_routes import bp as main
from .auth_routes import bp as auth
from .product_routes import bp as products
from .category_routes import bp as categories
from .pos_routes import bp as pos
from .cashier_routes import bp as cashier
from .customer_routes import bp as customers
from .inventory_routes import bp as inventory
from .supplier_routes import bp as suppliers
from .purchase_order_routes import bp as purchase_orders
from .reports import bp as reports

# Exportar los blueprints
__all__ = [
    'main', 'auth', 'products', 'categories', 'pos', 'cashier',
    'customers', 'inventory', 'suppliers', 'purchase_orders', 'reports'
] 