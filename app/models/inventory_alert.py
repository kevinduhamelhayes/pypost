"""
Modelo para alertas de inventario en el sistema PyPOS Local.
"""
from datetime import datetime
from app import db


class InventoryAlert(db.Model):
    """
    Modelo que representa una alerta de inventario en el sistema.
    
    Attributes:
        id: Clave primaria autoincremental
        product_id: ID del producto asociado a la alerta
        alert_type: Tipo de alerta (e.g., 'low_stock', 'expiration')
        alert_datetime: Fecha y hora de creación de la alerta
        resolved_datetime: Fecha y hora de resolución de la alerta
        is_resolved: Indica si la alerta ha sido resuelta
        resolved_by: ID del usuario que resolvió la alerta
        notes: Notas sobre la resolución de la alerta
        threshold: Umbral que activó la alerta (aplicable a alertas de stock)
        current_value: Valor actual que activó la alerta
        created_at: Fecha y hora de creación del registro
        updated_at: Fecha y hora de última actualización del registro
    """
    
    __tablename__ = 'inventory_alerts'
    
    # Tipos de alerta predefinidos
    ALERT_TYPE_LOW_STOCK = 'low_stock'
    ALERT_TYPE_EXPIRATION = 'expiration'
    ALERT_TYPE_STOCK_OUT = 'stock_out'
    ALERT_TYPE_OVERSTOCK = 'overstock'
    ALERT_TYPE_PRICE_BELOW_COST = 'price_below_cost'
    ALERT_TYPE_CUSTOM = 'custom'
    
    # Lista de tipos de alertas válidos
    VALID_ALERT_TYPES = [
        ALERT_TYPE_LOW_STOCK,
        ALERT_TYPE_EXPIRATION,
        ALERT_TYPE_STOCK_OUT,
        ALERT_TYPE_OVERSTOCK,
        ALERT_TYPE_PRICE_BELOW_COST,
        ALERT_TYPE_CUSTOM
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    alert_type = db.Column(db.String(30), nullable=False)
    alert_datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resolved_datetime = db.Column(db.DateTime, nullable=True)
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    threshold = db.Column(db.Integer, nullable=True)
    current_value = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Definir relaciones
    product = db.relationship('Product', backref=db.backref('inventory_alerts', lazy=True))
    resolver = db.relationship('User', backref=db.backref('resolved_alerts', lazy=True))
    
    def __init__(self, product_id, alert_type, threshold=None, current_value=None, notes=None):
        """
        Inicializa una nueva instancia de InventoryAlert.
        
        Args:
            product_id: ID del producto
            alert_type: Tipo de alerta
            threshold: Umbral que activó la alerta (opcional)
            current_value: Valor actual que activó la alerta (opcional)
            notes: Notas adicionales (opcional)
        """
        self.product_id = product_id
        self.alert_type = alert_type
        self.threshold = threshold
        self.current_value = current_value
        self.notes = notes
    
    def __repr__(self):
        """
        Representación en cadena de texto de la alerta de inventario.
        
        Returns:
            Cadena de texto con el ID y detalles de la alerta.
        """
        return f'<InventoryAlert {self.id}: Product {self.product_id}, Type {self.alert_type}>'
    
    @staticmethod
    def get_alert_type_display(alert_type):
        """
        Obtiene la descripción legible de un tipo de alerta.
        
        Args:
            alert_type: Tipo de alerta
            
        Returns:
            Descripción legible del tipo de alerta
        """
        alert_type_map = {
            InventoryAlert.ALERT_TYPE_LOW_STOCK: 'Stock Bajo',
            InventoryAlert.ALERT_TYPE_EXPIRATION: 'Próximo a Vencer',
            InventoryAlert.ALERT_TYPE_STOCK_OUT: 'Sin Stock',
            InventoryAlert.ALERT_TYPE_OVERSTOCK: 'Exceso de Stock',
            InventoryAlert.ALERT_TYPE_PRICE_BELOW_COST: 'Precio por Debajo del Costo',
            InventoryAlert.ALERT_TYPE_CUSTOM: 'Personalizada'
        }
        return alert_type_map.get(alert_type, 'Desconocida')
    
    @property
    def alert_type_display(self):
        """
        Propiedad que devuelve la descripción legible del tipo de alerta.
        
        Returns:
            Descripción legible del tipo de alerta
        """
        return self.get_alert_type_display(self.alert_type)
    
    def resolve(self, user_id, resolution_notes=None):
        """
        Marca la alerta como resuelta.
        
        Args:
            user_id: ID del usuario que resuelve la alerta
            resolution_notes: Notas sobre la resolución
            
        Returns:
            La instancia de alerta actualizada
        """
        self.is_resolved = True
        self.resolved_datetime = datetime.utcnow()
        self.resolved_by = user_id
        if resolution_notes:
            self.notes = resolution_notes if not self.notes else f"{self.notes}\n\nResolución: {resolution_notes}"
        return self
    
    def to_dict(self):
        """
        Convierte la alerta de inventario a un diccionario.
        
        Returns:
            Diccionario con los datos de la alerta
        """
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'alert_type': self.alert_type,
            'alert_type_display': self.alert_type_display,
            'alert_datetime': self.alert_datetime.isoformat() if self.alert_datetime else None,
            'resolved_datetime': self.resolved_datetime.isoformat() if self.resolved_datetime else None,
            'is_resolved': self.is_resolved,
            'resolved_by': self.resolved_by,
            'resolver_name': self.resolver.username if self.resolver else None,
            'notes': self.notes,
            'threshold': self.threshold,
            'current_value': self.current_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 