"""
Modelo para categorías de productos en el sistema PyPOS Local.
"""
from datetime import datetime
from app import db

class Category(db.Model):
    """
    Modelo que representa una categoría de productos en el sistema.
    
    Attributes:
        id: Clave primaria autoincremental
        name: Nombre de la categoría (obligatorio)
        description: Descripción de la categoría (opcional)
        parent_id: ID de la categoría padre (para categorías jerárquicas)
        is_active: Indica si la categoría está activa
        created_at: Fecha y hora de creación de la categoría
        updated_at: Fecha y hora de última actualización de la categoría
    """
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación para subcategorías
    children = db.relationship('Category', 
                              backref=db.backref('parent', remote_side=[id]),
                              cascade="all, delete-orphan")
    
    # Relación con productos (se añadirá referencia en el modelo Product)
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __init__(self, name, description=None, parent_id=None, is_active=True):
        """
        Inicializa una nueva instancia de Category.
        
        Args:
            name: Nombre de la categoría
            description: Descripción de la categoría
            parent_id: ID de la categoría padre (opcional)
            is_active: Estado inicial de la categoría (activo/inactivo)
        """
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.is_active = is_active
    
    def __repr__(self):
        """
        Representación en cadena de texto de la categoría.
        
        Returns:
            Cadena de texto con el ID y nombre de la categoría.
        """
        return f'<Category {self.id}: {self.name}>'
    
    @property
    def full_path(self):
        """
        Obtiene la ruta completa de la categoría (incluyendo padres).
        
        Returns:
            Cadena de texto con la ruta completa separada por " > "
        """
        if self.parent is None:
            return self.name
        return f"{self.parent.full_path} > {self.name}"
    
    @property
    def is_leaf(self):
        """
        Verifica si la categoría es una hoja (no tiene subcategorías).
        
        Returns:
            True si no tiene subcategorías, False en caso contrario
        """
        return len(self.children) == 0
    
    @property
    def product_count(self):
        """
        Obtiene el número de productos directamente asignados a esta categoría.
        
        Returns:
            Número de productos en la categoría
        """
        return len(self.products)
    
    @property
    def total_product_count(self):
        """
        Obtiene el número total de productos en esta categoría y sus subcategorías.
        
        Returns:
            Número total de productos
        """
        count = self.product_count
        for child in self.children:
            count += child.total_product_count
        return count
    
    def to_dict(self):
        """
        Convierte la categoría a un diccionario.
        
        Returns:
            Diccionario con los datos de la categoría
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'is_active': self.is_active,
            'full_path': self.full_path,
            'is_leaf': self.is_leaf,
            'product_count': self.product_count,
            'children_count': len(self.children),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 