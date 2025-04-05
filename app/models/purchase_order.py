"""
Modelo para órdenes de compra en el sistema PyPOS Local.
"""
from datetime import datetime
from app import db


class PurchaseOrder(db.Model):
    """
    Modelo que representa una orden de compra a un proveedor.
    
    Attributes:
        id: Clave primaria autoincremental
        order_number: Número de orden de compra (generado automáticamente)
        supplier_id: ID del proveedor
        user_id: ID del usuario que creó la orden
        order_date: Fecha de la orden
        expected_date: Fecha esperada de recepción
        received_date: Fecha real de recepción
        status: Estado de la orden
        subtotal: Subtotal de la orden
        tax_amount: Importe de impuestos
        shipping_cost: Costo de envío
        total_amount: Importe total de la orden
        notes: Notas sobre la orden
        created_at: Fecha y hora de creación del registro
        updated_at: Fecha y hora de última actualización del registro
    """
    
    __tablename__ = 'purchase_orders'
    
    # Estados posibles para una orden de compra
    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_SENT = 'sent'
    STATUS_PARTIAL = 'partially_received'
    STATUS_RECEIVED = 'received'
    STATUS_CANCELLED = 'cancelled'
    
    # Lista de estados válidos
    VALID_STATUSES = [
        STATUS_DRAFT,
        STATUS_PENDING,
        STATUS_APPROVED,
        STATUS_SENT,
        STATUS_PARTIAL,
        STATUS_RECEIVED,
        STATUS_CANCELLED
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expected_date = db.Column(db.DateTime, nullable=True)
    received_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default=STATUS_DRAFT, nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    tax_amount = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    shipping_cost = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Definir relaciones
    supplier = db.relationship('Supplier', backref=db.backref('purchase_orders', lazy=True))
    user = db.relationship('User', backref=db.backref('purchase_orders', lazy=True))
    
    def __init__(self, order_number, supplier_id, user_id, 
                 expected_date=None, notes=None, status=STATUS_DRAFT):
        """
        Inicializa una nueva instancia de PurchaseOrder.
        
        Args:
            order_number: Número de orden de compra
            supplier_id: ID del proveedor
            user_id: ID del usuario que crea la orden
            expected_date: Fecha esperada de recepción
            notes: Notas adicionales
            status: Estado inicial de la orden
        """
        self.order_number = order_number
        self.supplier_id = supplier_id
        self.user_id = user_id
        self.expected_date = expected_date
        self.notes = notes
        self.status = status
    
    def __repr__(self):
        """
        Representación en cadena de texto de la orden de compra.
        
        Returns:
            Cadena de texto con el ID y número de la orden.
        """
        return f'<PurchaseOrder {self.id}: {self.order_number}>'
    
    @staticmethod
    def get_status_display(status_code):
        """
        Obtiene la descripción legible de un código de estado.
        
        Args:
            status_code: Código de estado de la orden
            
        Returns:
            Descripción legible del estado
        """
        status_map = {
            PurchaseOrder.STATUS_DRAFT: 'Borrador',
            PurchaseOrder.STATUS_PENDING: 'Pendiente',
            PurchaseOrder.STATUS_APPROVED: 'Aprobada',
            PurchaseOrder.STATUS_SENT: 'Enviada',
            PurchaseOrder.STATUS_PARTIAL: 'Parcialmente Recibida',
            PurchaseOrder.STATUS_RECEIVED: 'Recibida',
            PurchaseOrder.STATUS_CANCELLED: 'Cancelada'
        }
        return status_map.get(status_code, 'Desconocido')
    
    @property
    def status_display(self):
        """
        Propiedad que devuelve la descripción legible del estado de la orden.
        
        Returns:
            Descripción legible del estado
        """
        return self.get_status_display(self.status)
    
    @property
    def items(self):
        """
        Obtiene los ítems asociados a esta orden de compra.
        
        Returns:
            Lista de ítems de la orden
        """
        return PurchaseOrderItem.query.filter_by(purchase_order_id=self.id).all()
    
    def calculate_totals(self):
        """
        Calcula los totales de la orden basados en sus ítems.
        
        Returns:
            La instancia de orden de compra actualizada
        """
        items = self.items
        self.subtotal = sum(float(item.subtotal) for item in items)
        self.total_amount = self.subtotal + float(self.tax_amount) + float(self.shipping_cost)
        return self
    
    def to_dict(self):
        """
        Convierte la orden de compra a un diccionario.
        
        Returns:
            Diccionario con los datos de la orden
        """
        return {
            'id': self.id,
            'order_number': self.order_number,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'expected_date': self.expected_date.isoformat() if self.expected_date else None,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'status': self.status,
            'status_display': self.status_display,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'shipping_cost': float(self.shipping_cost),
            'total_amount': float(self.total_amount),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class PurchaseOrderItem(db.Model):
    """
    Modelo que representa un ítem en una orden de compra.
    
    Attributes:
        id: Clave primaria autoincremental
        purchase_order_id: ID de la orden de compra
        product_id: ID del producto
        quantity: Cantidad solicitada
        quantity_received: Cantidad recibida
        unit_price: Precio unitario
        subtotal: Subtotal del ítem
        notes: Notas sobre el ítem
        created_at: Fecha y hora de creación del registro
    """
    
    __tablename__ = 'purchase_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    quantity_received = db.Column(db.Integer, default=0, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Definir relaciones
    purchase_order = db.relationship('PurchaseOrder', backref=db.backref('items_relation', lazy=True))
    product = db.relationship('Product', backref=db.backref('purchase_order_items', lazy=True))
    
    def __init__(self, purchase_order_id, product_id, quantity, unit_price, notes=None):
        """
        Inicializa una nueva instancia de PurchaseOrderItem.
        
        Args:
            purchase_order_id: ID de la orden de compra
            product_id: ID del producto
            quantity: Cantidad solicitada
            unit_price: Precio unitario
            notes: Notas adicionales
        """
        self.purchase_order_id = purchase_order_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.subtotal = float(unit_price) * quantity
        self.notes = notes
    
    def __repr__(self):
        """
        Representación en cadena de texto del ítem de orden de compra.
        
        Returns:
            Cadena de texto con el ID y detalles del ítem.
        """
        return f'<PurchaseOrderItem {self.id}: Order {self.purchase_order_id}, Product {self.product_id}>'
    
    @property
    def is_fully_received(self):
        """
        Verifica si el ítem ha sido recibido en su totalidad.
        
        Returns:
            True si quantity_received >= quantity, False en caso contrario
        """
        return self.quantity_received >= self.quantity
    
    def receive(self, quantity_received):
        """
        Registra la recepción de una cantidad del ítem.
        
        Args:
            quantity_received: Cantidad recibida
            
        Returns:
            La instancia del ítem actualizada
        """
        self.quantity_received += quantity_received
        return self
    
    def to_dict(self):
        """
        Convierte el ítem de orden de compra a un diccionario.
        
        Returns:
            Diccionario con los datos del ítem
        """
        return {
            'id': self.id,
            'purchase_order_id': self.purchase_order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'quantity_received': self.quantity_received,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.subtotal),
            'notes': self.notes,
            'is_fully_received': self.is_fully_received,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 