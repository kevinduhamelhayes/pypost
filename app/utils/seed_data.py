"""
Script para generar datos de prueba en la aplicación.
"""
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import db
from app.models import (
    User, Category, Product, Customer, 
    InventoryAdjustment, InventoryAlert
)

def create_test_data():
    """Crea datos de prueba para la aplicación."""
    
    # Crear usuarios de prueba
    users = [
        User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            full_name='Administrador',
            email='admin@pypos.local',
            role='admin'
        ),
        User(
            username='cajero',
            password_hash=generate_password_hash('cajero123'),
            full_name='Cajero Demo',
            email='cajero@pypos.local',
            role='cashier'
        ),
        User(
            username='gerente',
            password_hash=generate_password_hash('gerente123'),
            full_name='Gerente Demo',
            email='gerente@pypos.local',
            role='manager'
        )
    ]
    
    for user in users:
        db.session.add(user)
    
    # Crear categorías de prueba
    categories = [
        Category(name='Bebidas', description='Refrescos, jugos y bebidas'),
        Category(name='Snacks', description='Botanas y aperitivos'),
        Category(name='Abarrotes', description='Productos básicos y despensa'),
        Category(name='Limpieza', description='Productos de limpieza'),
        Category(name='Electrónicos', description='Accesorios electrónicos')
    ]
    
    for category in categories:
        db.session.add(category)
    
    # Hacer commit para tener IDs de categorías
    db.session.commit()
    
    # Crear productos de prueba
    products = [
        # Bebidas
        Product(
            name='Coca Cola 600ml',
            description='Refresco Coca Cola botella 600ml',
            sku='BEB001',
            barcode='7501055300006',
            purchase_price=8.50,
            sale_price=15.00,
            category_id=categories[0].id,
            current_stock=50,
            low_stock_threshold=10
        ),
        Product(
            name='Agua Natural 1L',
            description='Agua purificada 1 litro',
            sku='BEB002',
            barcode='7501055300013',
            purchase_price=5.00,
            sale_price=10.00,
            category_id=categories[0].id,
            current_stock=100,
            low_stock_threshold=20
        ),
        # Snacks
        Product(
            name='Sabritas Clásicas 45g',
            description='Papas fritas sabor original',
            sku='SNK001',
            barcode='7501055300020',
            purchase_price=7.50,
            sale_price=13.00,
            category_id=categories[1].id,
            current_stock=5,  # Stock bajo para pruebas
            low_stock_threshold=10
        ),
        # Abarrotes
        Product(
            name='Arroz 1kg',
            description='Arroz blanco 1kg',
            sku='ABR001',
            barcode='7501055300037',
            purchase_price=15.00,
            sale_price=25.00,
            category_id=categories[2].id,
            current_stock=0,  # Sin stock para pruebas
            low_stock_threshold=5
        ),
        # Limpieza
        Product(
            name='Jabón en Polvo 1kg',
            description='Detergente en polvo multiusos',
            sku='LIM001',
            barcode='7501055300044',
            purchase_price=20.00,
            sale_price=35.00,
            category_id=categories[3].id,
            current_stock=15,
            low_stock_threshold=8
        ),
        # Electrónicos
        Product(
            name='Cable USB 1m',
            description='Cable USB tipo C',
            sku='ELE001',
            barcode='7501055300051',
            purchase_price=25.00,
            sale_price=50.00,
            category_id=categories[4].id,
            current_stock=20,
            low_stock_threshold=5
        )
    ]
    
    for product in products:
        db.session.add(product)
    
    # Crear clientes de prueba
    customers = [
        Customer(
            first_name='Juan',
            last_name='Pérez',
            email='juan.perez@email.com',
            phone='5551234567'
        ),
        Customer(
            first_name='María',
            last_name='García',
            email='maria.garcia@email.com',
            phone='5559876543'
        )
    ]
    
    for customer in customers:
        db.session.add(customer)
    
    # Hacer commit para tener IDs
    db.session.commit()
    
    # Crear algunos ajustes de inventario
    adjustments = [
        InventoryAdjustment(
            product_id=products[0].id,  # Coca Cola
            user_id=users[0].id,  # Admin
            quantity_change=50,
            previous_stock=0,
            reason='initial_stock',
            notes='Stock inicial del producto'
        ),
        InventoryAdjustment(
            product_id=products[2].id,  # Sabritas
            user_id=users[0].id,
            quantity_change=-5,
            previous_stock=10,
            reason='damage',
            notes='Productos dañados en almacén'
        )
    ]
    
    for adjustment in adjustments:
        db.session.add(adjustment)
    
    # Crear algunas alertas de inventario
    alerts = [
        InventoryAlert(
            product_id=products[2].id,  # Sabritas (stock bajo)
            alert_type='low_stock',
            threshold=10,
            current_value=5
        ),
        InventoryAlert(
            product_id=products[3].id,  # Arroz (sin stock)
            alert_type='stock_out',
            threshold=0,
            current_value=0
        )
    ]
    
    for alert in alerts:
        db.session.add(alert)
    
    # Commit final
    db.session.commit()
    
    print("Datos de prueba creados exitosamente!")
    print("\nUsuarios creados:")
    print("Admin - usuario: admin, contraseña: admin123")
    print("Cajero - usuario: cajero, contraseña: cajero123")
    print("Gerente - usuario: gerente, contraseña: gerente123") 