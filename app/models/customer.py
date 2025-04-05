"""
Modelo para clientes en el sistema PyPOS Local.
"""
from datetime import datetime
from app import db

class Customer(db.Model):
    """
    Modelo que representa un cliente en el sistema.
    
    Attributes:
        id: Clave primaria autoincremental
        first_name: Nombre del cliente
        last_name: Apellido del cliente
        email: Correo electrónico (opcional, único)
        phone: Número de teléfono (opcional)
        address: Dirección física (opcional)
        tax_id: Identificación fiscal (opcional, ej. RFC, CUIT, DNI)
        notes: Notas adicionales sobre el cliente
        is_active: Indica si el cliente está activo
        created_at: Fecha y hora de creación del registro
        updated_at: Fecha y hora de última actualización del registro
    """
    
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    sales = db.relationship('Sale', backref='customer', lazy=True)
    
    def __init__(self, first_name, last_name, email=None, phone=None, address=None, tax_id=None, notes=None, is_active=True):
        """
        Inicializa una nueva instancia de Customer.
        
        Args:
            first_name: Nombre del cliente
            last_name: Apellido del cliente
            email: Correo electrónico (opcional)
            phone: Número de teléfono (opcional)
            address: Dirección física (opcional)
            tax_id: Identificación fiscal (opcional)
            notes: Notas adicionales sobre el cliente
            is_active: Estado inicial del cliente (activo/inactivo)
        """
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.tax_id = tax_id
        self.notes = notes
        self.is_active = is_active
    
    def __repr__(self):
        """
        Representación en cadena de texto del cliente.
        
        Returns:
            Cadena de texto con el ID y nombre completo del cliente.
        """
        return f'<Customer {self.id}: {self.full_name}>'
    
    @property
    def full_name(self):
        """
        Obtiene el nombre completo del cliente.
        
        Returns:
            Nombre completo (nombre + apellido)
        """
        return f"{self.first_name} {self.last_name}"
    
    @property
    def total_purchases(self):
        """
        Obtiene el monto total de compras del cliente.
        
        Returns:
            Suma de todos los montos de ventas asociadas al cliente
        """
        from app.models.sale import Sale
        sales = Sale.query.filter_by(customer_id=self.id, status='completed').all()
        return sum(float(sale.final_amount) for sale in sales)
    
    @property
    def purchase_count(self):
        """
        Obtiene el número de compras realizadas por el cliente.
        
        Returns:
            Cantidad de ventas completadas asociadas al cliente
        """
        return len([sale for sale in self.sales if sale.status == 'completed'])
    
    @property
    def last_purchase_date(self):
        """
        Obtiene la fecha de la última compra del cliente.
        
        Returns:
            Fecha de la última venta completada, o None si no hay ventas
        """
        from app.models.sale import Sale
        last_sale = Sale.query.filter_by(customer_id=self.id, status='completed').order_by(Sale.sale_datetime.desc()).first()
        return last_sale.sale_datetime if last_sale else None
    
    def to_dict(self):
        """
        Convierte el cliente a un diccionario.
        
        Returns:
            Diccionario con los datos del cliente
        """
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'tax_id': self.tax_id,
            'notes': self.notes,
            'is_active': self.is_active,
            'purchase_count': self.purchase_count,
            'total_purchases': self.total_purchases,
            'last_purchase_date': self.last_purchase_date.isoformat() if self.last_purchase_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 