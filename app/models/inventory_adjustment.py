"""
Modelo para ajustes de inventario en el sistema PyPOS Local.
"""
from datetime import datetime
from app import db


class InventoryAdjustment(db.Model):
    """
    Modelo que representa un ajuste de inventario en el sistema.
    
    Attributes:
        id: Clave primaria autoincremental
        product_id: ID del producto al que se realiza el ajuste
        user_id: ID del usuario que realiza el ajuste
        adjustment_datetime: Fecha y hora del ajuste
        quantity_change: Cantidad ajustada (positiva para entradas, negativa para salidas)
        previous_stock: Stock del producto antes del ajuste
        current_stock: Stock del producto después del ajuste
        reason: Motivo del ajuste (e.g., 'Conteo físico', 'Merma', 'Stock inicial')
        reference: Referencia a documento relacionado (e.g., número de factura, orden)
        notes: Notas adicionales sobre el ajuste
        created_at: Fecha y hora de creación del registro
    """
    
    __tablename__ = 'inventory_adjustments'
    
    # Razones predefinidas para ajustes de inventario
    REASON_INITIAL_STOCK = 'initial_stock'
    REASON_PHYSICAL_COUNT = 'physical_count'
    REASON_DAMAGE = 'damage'
    REASON_EXPIRATION = 'expiration'
    REASON_SUPPLIER_RETURN = 'supplier_return'
    REASON_PURCHASE = 'purchase'
    REASON_MANUAL_ADJUSTMENT = 'manual_adjustment'
    REASON_SYSTEM_ADJUSTMENT = 'system_adjustment'
    
    # Lista de razones válidas
    VALID_REASONS = [
        REASON_INITIAL_STOCK,
        REASON_PHYSICAL_COUNT,
        REASON_DAMAGE,
        REASON_EXPIRATION,
        REASON_SUPPLIER_RETURN,
        REASON_PURCHASE,
        REASON_MANUAL_ADJUSTMENT,
        REASON_SYSTEM_ADJUSTMENT
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    adjustment_datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)
    previous_stock = db.Column(db.Integer, nullable=False)
    current_stock = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(50), nullable=False)
    reference = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Definir relaciones
    product = db.relationship('Product', backref=db.backref('inventory_adjustments', lazy=True))
    user = db.relationship('User', backref=db.backref('inventory_adjustments', lazy=True))
    
    def __init__(self, product_id, user_id, quantity_change, previous_stock, reason, 
                 reference=None, notes=None):
        """
        Inicializa una nueva instancia de InventoryAdjustment.
        
        Args:
            product_id: ID del producto
            user_id: ID del usuario que realiza el ajuste
            quantity_change: Cantidad ajustada (+ para entradas, - para salidas)
            previous_stock: Stock antes del ajuste
            reason: Motivo del ajuste
            reference: Referencia opcional (ej. número de factura)
            notes: Notas adicionales
        """
        self.product_id = product_id
        self.user_id = user_id
        self.quantity_change = quantity_change
        self.previous_stock = previous_stock
        self.current_stock = previous_stock + quantity_change
        self.reason = reason
        self.reference = reference
        self.notes = notes
    
    def __repr__(self):
        """
        Representación en cadena de texto del ajuste de inventario.
        
        Returns:
            Cadena de texto con el ID y detalles del ajuste.
        """
        return f'<InventoryAdjustment {self.id}: Product {self.product_id}, Change {self.quantity_change}>'
    
    @staticmethod
    def get_reason_display(reason_code):
        """
        Obtiene la descripción legible de un código de razón.
        
        Args:
            reason_code: Código de razón para el ajuste
            
        Returns:
            Descripción legible de la razón
        """
        reason_map = {
            InventoryAdjustment.REASON_INITIAL_STOCK: 'Stock Inicial',
            InventoryAdjustment.REASON_PHYSICAL_COUNT: 'Conteo Físico',
            InventoryAdjustment.REASON_DAMAGE: 'Producto Dañado',
            InventoryAdjustment.REASON_EXPIRATION: 'Producto Vencido',
            InventoryAdjustment.REASON_SUPPLIER_RETURN: 'Devolución a Proveedor',
            InventoryAdjustment.REASON_PURCHASE: 'Compra',
            InventoryAdjustment.REASON_MANUAL_ADJUSTMENT: 'Ajuste Manual',
            InventoryAdjustment.REASON_SYSTEM_ADJUSTMENT: 'Ajuste del Sistema'
        }
        return reason_map.get(reason_code, 'Desconocido')
    
    @property
    def reason_display(self):
        """
        Propiedad que devuelve la descripción legible de la razón del ajuste.
        
        Returns:
            Descripción legible de la razón
        """
        return self.get_reason_display(self.reason)
    
    def to_dict(self):
        """
        Convierte el ajuste de inventario a un diccionario.
        
        Returns:
            Diccionario con los datos del ajuste
        """
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else None,
            'adjustment_datetime': self.adjustment_datetime.isoformat() if self.adjustment_datetime else None,
            'quantity_change': self.quantity_change,
            'previous_stock': self.previous_stock,
            'current_stock': self.current_stock,
            'reason': self.reason,
            'reason_display': self.reason_display,
            'reference': self.reference,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 