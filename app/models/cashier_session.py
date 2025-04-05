"""
Modelo para sesiones de caja en el sistema PyPOS Local.
"""
from datetime import datetime
from app import db

class CashierSession(db.Model):
    """
    Modelo que representa una sesión de caja (apertura/cierre).
    
    Attributes:
        id: Clave primaria autoincremental
        user_id: ID del usuario que abrió/cerró la caja
        start_datetime: Fecha y hora de apertura de caja
        end_datetime: Fecha y hora de cierre de caja (NULL si está abierta)
        starting_cash: Monto inicial en caja
        ending_cash_expected: Monto final esperado (calculado)
        ending_cash_actual: Monto final real (contado físicamente)
        cash_difference: Diferencia entre monto esperado y real
        status: Estado de la sesión (open, closed)
        notes: Notas adicionales sobre la sesión
        created_at: Fecha y hora de creación del registro
        updated_at: Fecha y hora de última actualización del registro
    """
    
    __tablename__ = 'cashier_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=True)
    starting_cash = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    ending_cash_expected = db.Column(db.Numeric(12, 2), nullable=True)
    ending_cash_actual = db.Column(db.Numeric(12, 2), nullable=True)
    cash_difference = db.Column(db.Numeric(12, 2), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='open')  # open, closed
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = db.relationship('User', backref='cashier_sessions')
    sales = db.relationship('Sale', backref='cashier_session', lazy=True)
    
    def __init__(self, user_id, starting_cash=0.00, notes=None):
        """
        Inicializa una nueva instancia de CashierSession.
        
        Args:
            user_id: ID del usuario que abre la caja
            starting_cash: Monto inicial en caja
            notes: Notas adicionales
        """
        self.user_id = user_id
        self.starting_cash = starting_cash
        self.notes = notes
        self.start_datetime = datetime.utcnow()
        self.status = 'open'
    
    def __repr__(self):
        """
        Representación en cadena de texto de la sesión de caja.
        
        Returns:
            Cadena de texto con el ID, usuario y estado de la sesión.
        """
        return f'<CashierSession {self.id}: User {self.user_id}, Status {self.status}>'
    
    def close(self, ending_cash_actual, notes=None):
        """
        Cierra la sesión de caja.
        
        Args:
            ending_cash_actual: Monto final real en caja
            notes: Notas adicionales sobre el cierre
            
        Returns:
            True si se cerró correctamente, False en caso contrario
        """
        if self.status == 'closed':
            return False
        
        try:
            # Calcular el monto esperado en caja
            cash_sales_amount = 0
            for sale in self.sales:
                if sale.status == 'completed' and sale.payment_method == 'cash':
                    cash_sales_amount += float(sale.final_amount)
            
            self.ending_cash_expected = float(self.starting_cash) + cash_sales_amount
            self.ending_cash_actual = ending_cash_actual
            self.cash_difference = float(self.ending_cash_actual) - float(self.ending_cash_expected)
            self.end_datetime = datetime.utcnow()
            self.status = 'closed'
            
            if notes:
                self.notes = (self.notes or '') + f"\nCierre: {notes}"
            
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @property
    def is_open(self):
        """
        Verifica si la sesión está abierta.
        
        Returns:
            True si está abierta, False en caso contrario
        """
        return self.status == 'open'
    
    @property
    def duration(self):
        """
        Calcula la duración de la sesión.
        
        Returns:
            Duración en segundos, o None si la sesión está abierta
        """
        if not self.end_datetime:
            return None
        
        return (self.end_datetime - self.start_datetime).total_seconds()
    
    @property
    def total_sales(self):
        """
        Calcula el total de ventas en la sesión.
        
        Returns:
            Monto total de ventas completadas
        """
        return sum(float(sale.final_amount) for sale in self.sales if sale.status == 'completed')
    
    @property
    def sales_count(self):
        """
        Cuenta el número de ventas en la sesión.
        
        Returns:
            Cantidad de ventas completadas
        """
        return len([sale for sale in self.sales if sale.status == 'completed'])
    
    @classmethod
    def get_current_session(cls, user_id=None):
        """
        Obtiene la sesión de caja actualmente abierta.
        
        Args:
            user_id: ID del usuario (opcional)
            
        Returns:
            Instancia de CashierSession abierta, o None si no hay sesión abierta
        """
        query = cls.query.filter_by(status='open')
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(cls.start_datetime.desc()).first()
    
    def to_dict(self):
        """
        Convierte la sesión de caja a un diccionario.
        
        Returns:
            Diccionario con los datos de la sesión
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else None,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'starting_cash': float(self.starting_cash),
            'ending_cash_expected': float(self.ending_cash_expected) if self.ending_cash_expected else None,
            'ending_cash_actual': float(self.ending_cash_actual) if self.ending_cash_actual else None,
            'cash_difference': float(self.cash_difference) if self.cash_difference else None,
            'status': self.status,
            'notes': self.notes,
            'is_open': self.is_open,
            'duration': self.duration,
            'total_sales': self.total_sales,
            'sales_count': self.sales_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 