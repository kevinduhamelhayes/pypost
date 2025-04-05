"""
Modelo para usuarios del sistema PyPOS Local.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    """
    Modelo que representa un usuario del sistema.
    
    Attributes:
        id: Clave primaria autoincremental
        username: Nombre de usuario único (obligatorio)
        email: Email único del usuario (obligatorio)
        password_hash: Hash de la contraseña (no se almacena la contraseña en texto plano)
        full_name: Nombre completo del usuario
        role: Rol del usuario (admin, manager, cashier)
        is_active: Indica si el usuario está activo
        last_login: Fecha y hora del último inicio de sesión
        created_at: Fecha y hora de creación del usuario
        updated_at: Fecha y hora de última actualización del usuario
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), nullable=False, default='cashier')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, username, email, password, full_name=None, role='cashier', is_active=True):
        """
        Inicializa una nueva instancia de User.
        
        Args:
            username: Nombre de usuario único
            email: Email único del usuario
            password: Contraseña (será hasheada antes de almacenarse)
            full_name: Nombre completo del usuario
            role: Rol del usuario (admin, manager, cashier)
            is_active: Estado inicial del usuario (activo/inactivo)
        """
        self.username = username
        self.email = email
        self.set_password(password)
        self.full_name = full_name
        self.role = role
        self.is_active = is_active
    
    def __repr__(self):
        """
        Representación en cadena de texto del usuario.
        
        Returns:
            Cadena de texto con el ID y nombre de usuario.
        """
        return f'<User {self.id}: {self.username}>'
    
    def set_password(self, password):
        """
        Establece una nueva contraseña para el usuario.
        
        Args:
            password: Nueva contraseña en texto plano (será hasheada)
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verifica si la contraseña proporcionada es correcta.
        
        Args:
            password: Contraseña en texto plano a verificar
            
        Returns:
            True si la contraseña es correcta, False en caso contrario
        """
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """
        Actualiza la fecha y hora del último inicio de sesión.
        """
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @property
    def is_admin(self):
        """
        Verifica si el usuario tiene rol de administrador.
        
        Returns:
            True si el usuario es administrador, False en caso contrario
        """
        return self.role == 'admin'
    
    @property
    def is_manager(self):
        """
        Verifica si el usuario tiene rol de gerente.
        
        Returns:
            True si el usuario es gerente, False en caso contrario
        """
        return self.role == 'manager'
    
    def to_dict(self):
        """
        Convierte el usuario a un diccionario.
        
        Returns:
            Diccionario con los datos del usuario (sin la contraseña)
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 