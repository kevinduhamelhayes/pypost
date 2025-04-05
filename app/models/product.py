"""
Modelo para productos en el sistema PyPOS Local.
"""
from datetime import datetime
from app import db


class Product(db.Model):
    """
    Modelo que representa un producto en el sistema.
    
    Attributes:
        id: Clave primaria autoincremental
        name: Nombre del producto (obligatorio)
        description: Descripción detallada del producto (opcional)
        sku: Stock Keeping Unit - código de identificación interno (opcional)
        barcode: Código de barras (opcional)
        purchase_price: Precio de compra/costo del producto
        sale_price: Precio de venta del producto
        current_stock: Cantidad actual disponible en inventario
        is_active: Indica si el producto está activo/disponible
        created_at: Fecha y hora de creación del producto
        updated_at: Fecha y hora de última actualización del producto
    """
    
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sku = db.Column(db.String(100), unique=True, nullable=True)
    barcode = db.Column(db.String(100), unique=True, nullable=True)
    purchase_price = db.Column(db.Numeric(12, 2), default=0.00)
    sale_price = db.Column(db.Numeric(12, 2), nullable=False)
    current_stock = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, description=None, sku=None, barcode=None, purchase_price=0.00, 
                 sale_price=0.00, current_stock=0, is_active=True):
        """
        Inicializa una nueva instancia de Product.
        
        Args:
            name: Nombre del producto
            description: Descripción del producto
            sku: Código interno del producto
            barcode: Código de barras del producto
            purchase_price: Precio de compra/costo del producto
            sale_price: Precio de venta del producto
            current_stock: Cantidad inicial en inventario
            is_active: Estado inicial del producto (activo/inactivo)
        """
        self.name = name
        self.description = description
        self.sku = sku
        self.barcode = barcode
        self.purchase_price = purchase_price
        self.sale_price = sale_price
        self.current_stock = current_stock
        self.is_active = is_active
    
    def __repr__(self):
        """
        Representación en cadena de texto del producto.
        
        Returns:
            Cadena de texto con el ID y nombre del producto.
        """
        return f'<Product {self.id}: {self.name}>'
        
    @property
    def profit_margin(self):
        """
        Calcula el margen de beneficio del producto.
        
        Returns:
            Margen de beneficio como porcentaje (0-100)
        """
        if float(self.purchase_price) == 0:
            return 0 if float(self.sale_price) == 0 else 100
        
        margin = ((float(self.sale_price) - float(self.purchase_price)) / float(self.purchase_price)) * 100
        return round(margin, 2)
    
    @property
    def profit_amount(self):
        """
        Calcula el monto de beneficio por unidad.
        
        Returns:
            Monto de beneficio por unidad vendida
        """
        return round(float(self.sale_price) - float(self.purchase_price), 2)
    
    @property
    def is_in_stock(self):
        """
        Verifica si el producto tiene stock disponible.
        
        Returns:
            True si current_stock > 0, False en caso contrario
        """
        return self.current_stock > 0
        
    def to_dict(self):
        """
        Convierte el producto a un diccionario.
        
        Returns:
            Diccionario con los datos del producto
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sku': self.sku,
            'barcode': self.barcode,
            'purchase_price': float(self.purchase_price),
            'sale_price': float(self.sale_price),
            'current_stock': self.current_stock,
            'is_active': self.is_active,
            'profit_margin': self.profit_margin,
            'profit_amount': self.profit_amount,
            'is_in_stock': self.is_in_stock,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 