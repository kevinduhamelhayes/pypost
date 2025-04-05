"""
Inicialización del módulo de modelos.
"""
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem
from app.models.cashier_session import CashierSession
from app.models.inventory_adjustment import InventoryAdjustment
from app.models.inventory_alert import InventoryAlert
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem 