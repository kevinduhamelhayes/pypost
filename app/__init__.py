"""
Inicialización de la aplicación Flask y configuración de extensiones.
Este módulo crea y configura la aplicación Flask, registra los blueprints y
configura las extensiones necesarias.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
from config import Config

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Inicialización de extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    """
    Función factory para crear y configurar la aplicación Flask.
    
    Args:
        config_class: Clase de configuración para la aplicación
        
    Returns:
        La aplicación Flask configurada
    """
    # Crear instancia de Flask
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuración por defecto
    app.config.from_object(config_class)
    
    # Asegurar que existe el directorio de instancia
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Ruta para redirigir si se requiere login
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from app.routes import auth, main, products, inventory, customers, pos, reports
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(customers.bp)
    app.register_blueprint(pos.bp)
    app.register_blueprint(reports.bp)
    
    # Ruta de bienvenida para verificar que la app está funcionando
    @app.route('/hello')
    def hello():
        return {'message': 'Bienvenido a PyPOS Local API!'}
    
    return app 