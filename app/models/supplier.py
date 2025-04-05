"""
Modelo para proveedores en el sistema PyPOS Local.
"""
from datetime import datetime
from app import db


class Supplier(db.Model):
    """
    Modelo que representa un proveedor en el sistema.
    
    Attributes:
        id: Clave primaria autoincremental
        name: Nombre del proveedor
        contact_person: Nombre de la persona de contacto
        email: Correo electrónico del proveedor
        phone: Teléfono del proveedor
        address: Dirección del proveedor
        tax_id: Identificación fiscal del proveedor (e.g., RUC, CUIT)
        notes: Notas sobre el proveedor
        is_active: Indica si el proveedor está activo
        payment_terms: Términos de pago acordados
        lead_time: Tiempo promedio de entrega (en días)
        created_at: Fecha y hora de creación del registro
        updated_at: Fecha y hora de última actualización del registro
    """
    
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    payment_terms = db.Column(db.String(100), nullable=True)
    lead_time = db.Column(db.Integer, nullable=True)  # Días promedio de entrega
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones (se implementarán cuando se cree modelo ProductSupplier)
    # products = db.relationship('ProductSupplier', back_populates='supplier')
    
    def __init__(self, name, contact_person=None, email=None, phone=None, address=None, 
                 tax_id=None, notes=None, payment_terms=None, lead_time=None, is_active=True):
        """
        Inicializa una nueva instancia de Supplier.
        
        Args:
            name: Nombre del proveedor
            contact_person: Nombre de la persona de contacto
            email: Correo electrónico
            phone: Teléfono
            address: Dirección
            tax_id: ID fiscal
            notes: Notas adicionales
            payment_terms: Términos de pago
            lead_time: Tiempo de entrega en días
            is_active: Estado del proveedor
        """
        self.name = name
        self.contact_person = contact_person
        self.email = email
        self.phone = phone
        self.address = address
        self.tax_id = tax_id
        self.notes = notes
        self.payment_terms = payment_terms
        self.lead_time = lead_time
        self.is_active = is_active
    
    def __repr__(self):
        """
        Representación en cadena de texto del proveedor.
        
        Returns:
            Cadena de texto con el ID y nombre del proveedor.
        """
        return f'<Supplier {self.id}: {self.name}>'
    
    def to_dict(self):
        """
        Convierte el proveedor a un diccionario.
        
        Returns:
            Diccionario con los datos del proveedor
        """
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'tax_id': self.tax_id,
            'notes': self.notes,
            'is_active': self.is_active,
            'payment_terms': self.payment_terms,
            'lead_time': self.lead_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 