"""
Modelo para ventas en el sistema PyPOS Local.
"""
from datetime import datetime
from app import db

class Sale(db.Model):
    """
    Modelo que representa una venta (cabecera de la transacción).
    
    Attributes:
        id: Clave primaria autoincremental
        sale_datetime: Fecha y hora de la venta
        total_amount: Monto total de la venta
        discount_amount: Monto de descuento aplicado
        tax_amount: Monto de impuestos
        final_amount: Monto final a pagar (total - descuento + impuestos)
        payment_method: Método de pago utilizado
        user_id: ID del usuario (cajero) que realizó la venta
        customer_id: ID del cliente asociado a la venta (opcional)
        session_id: ID de la sesión del cajero
        status: Estado de la venta (completada, pendiente, cancelada)
        notes: Notas adicionales sobre la venta
        created_at: Fecha y hora de creación del registro
        updated_at: Fecha y hora de última actualización del registro
    """
    
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    discount_amount = db.Column(db.Numeric(12, 2), default=0.00)
    tax_amount = db.Column(db.Numeric(12, 2), default=0.00)
    final_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    payment_method = db.Column(db.String(50), default='cash')  # cash, card, transfer
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('cashier_sessions.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='completed')  # completed, pending, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = db.relationship('User', backref='sales')
    # La relación con customer se establecerá cuando se cree el modelo Customer
    items = db.relationship('SaleItem', back_populates='sale', cascade='all, delete-orphan')
    
    def __init__(self, user_id, customer_id=None, payment_method='cash', status='completed', notes=None):
        """
        Inicializa una nueva instancia de Sale.
        
        Args:
            user_id: ID del usuario que realiza la venta
            customer_id: ID del cliente (opcional)
            payment_method: Método de pago
            status: Estado inicial de la venta
            notes: Notas adicionales
        """
        self.user_id = user_id
        self.customer_id = customer_id
        self.payment_method = payment_method
        self.status = status
        self.notes = notes
        self.sale_datetime = datetime.utcnow()
    
    def __repr__(self):
        """
        Representación en cadena de texto de la venta.
        
        Returns:
            Cadena de texto con el ID y fecha de la venta.
        """
        return f'<Sale {self.id}: {self.sale_datetime}>'
    
    def add_item(self, product, quantity=1):
        """
        Añade un producto a la venta.
        
        Args:
            product: Instancia del producto a añadir
            quantity: Cantidad de unidades
            
        Returns:
            Instancia de SaleItem creada
        """
        # Verificar si el producto ya está en la venta
        existing_item = SaleItem.query.filter_by(sale_id=self.id, product_id=product.id).first()
        
        if existing_item:
            # Si ya existe, incrementar la cantidad
            existing_item.quantity += quantity
            existing_item.subtotal = float(existing_item.price_at_sale) * existing_item.quantity
            return existing_item
        
        # Si no existe, crear un nuevo item
        item = SaleItem(
            sale_id=self.id,
            product_id=product.id,
            quantity=quantity,
            price_at_sale=product.sale_price,
            cost_at_sale=product.purchase_price
        )
        db.session.add(item)
        return item
    
    def remove_item(self, product_id):
        """
        Elimina un producto de la venta.
        
        Args:
            product_id: ID del producto a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        item = SaleItem.query.filter_by(sale_id=self.id, product_id=product_id).first()
        if item:
            db.session.delete(item)
            return True
        return False
    
    def update_item_quantity(self, product_id, quantity):
        """
        Actualiza la cantidad de un producto en la venta.
        
        Args:
            product_id: ID del producto a actualizar
            quantity: Nueva cantidad
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        item = SaleItem.query.filter_by(sale_id=self.id, product_id=product_id).first()
        if item:
            if quantity <= 0:
                # Si la cantidad es 0 o negativa, eliminar el item
                return self.remove_item(product_id)
            
            item.quantity = quantity
            item.subtotal = float(item.price_at_sale) * quantity
            return True
        return False
    
    def calculate_totals(self):
        """
        Calcula y actualiza los totales de la venta.
        """
        total = sum(float(item.subtotal) for item in self.items)
        
        self.total_amount = total
        self.final_amount = total - float(self.discount_amount) + float(self.tax_amount)
    
    def complete_sale(self):
        """
        Finaliza la venta, actualizando el inventario.
        
        Returns:
            True si se completó correctamente, False en caso contrario
        """
        try:
            # Calcular totales finales
            self.calculate_totals()
            
            # Actualizar estado
            self.status = 'completed'
            
            # Actualizar inventario
            for item in self.items:
                product = item.product
                if product:
                    product.current_stock -= item.quantity
            
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def cancel_sale(self):
        """
        Cancela la venta, revertiendo cambios en inventario si ya se habían aplicado.
        
        Returns:
            True si se canceló correctamente, False en caso contrario
        """
        try:
            # Si estaba completada, restaurar inventario
            if self.status == 'completed':
                for item in self.items:
                    product = item.product
                    if product:
                        product.current_stock += item.quantity
            
            # Actualizar estado
            self.status = 'cancelled'
            
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def to_dict(self):
        """
        Convierte la venta a un diccionario.
        
        Returns:
            Diccionario con los datos de la venta
        """
        return {
            'id': self.id,
            'sale_datetime': self.sale_datetime.isoformat() if self.sale_datetime else None,
            'total_amount': float(self.total_amount),
            'discount_amount': float(self.discount_amount),
            'tax_amount': float(self.tax_amount),
            'final_amount': float(self.final_amount),
            'payment_method': self.payment_method,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if hasattr(self, 'customer') and self.customer else None,
            'status': self.status,
            'notes': self.notes,
            'items_count': len(self.items),
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SaleItem(db.Model):
    """
    Modelo que representa un ítem (línea) en una venta.
    
    Attributes:
        id: Clave primaria autoincremental
        sale_id: ID de la venta a la que pertenece
        product_id: ID del producto vendido
        quantity: Cantidad de unidades
        price_at_sale: Precio unitario al momento de la venta
        cost_at_sale: Costo unitario al momento de la venta
        subtotal: Monto subtotal (quantity * price_at_sale)
        created_at: Fecha y hora de creación del registro
    """
    
    __tablename__ = 'sale_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_sale = db.Column(db.Numeric(12, 2), nullable=False)
    cost_at_sale = db.Column(db.Numeric(12, 2), default=0.00)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    sale = db.relationship('Sale', back_populates='items')
    product = db.relationship('Product')
    
    def __init__(self, sale_id, product_id, quantity=1, price_at_sale=0.00, cost_at_sale=0.00):
        """
        Inicializa una nueva instancia de SaleItem.
        
        Args:
            sale_id: ID de la venta
            product_id: ID del producto
            quantity: Cantidad de unidades
            price_at_sale: Precio unitario al momento de la venta
            cost_at_sale: Costo unitario al momento de la venta
        """
        self.sale_id = sale_id
        self.product_id = product_id
        self.quantity = quantity
        self.price_at_sale = price_at_sale
        self.cost_at_sale = cost_at_sale
        self.subtotal = float(price_at_sale) * quantity
    
    def __repr__(self):
        """
        Representación en cadena de texto del ítem de venta.
        
        Returns:
            Cadena de texto con el ID de la venta, el ID del producto y la cantidad.
        """
        return f'<SaleItem {self.id}: Sale {self.sale_id}, Product {self.product_id}, Quantity {self.quantity}>'
    
    @property
    def profit(self):
        """
        Calcula el beneficio obtenido por este ítem de venta.
        
        Returns:
            Beneficio total (precio de venta - costo) * cantidad
        """
        return (float(self.price_at_sale) - float(self.cost_at_sale)) * self.quantity
    
    def to_dict(self):
        """
        Convierte el ítem de venta a un diccionario.
        
        Returns:
            Diccionario con los datos del ítem de venta
        """
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'price_at_sale': float(self.price_at_sale),
            'cost_at_sale': float(self.cost_at_sale),
            'subtotal': float(self.subtotal),
            'profit': self.profit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 