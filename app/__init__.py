"""
Inicialización de la aplicación Flask y configuración de extensiones.
Este módulo crea y configura la aplicación Flask, registra los blueprints y
configura las extensiones necesarias.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Inicialización de extensiones
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    """
    Función factory para crear y configurar la aplicación Flask.
    
    Args:
        test_config: Configuración opcional para pruebas
        
    Returns:
        La aplicación Flask configurada
    """
    # Crear instancia de Flask
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuración por defecto
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=f"postgresql://{os.environ.get('POSTGRES_USER', 'pypos_user')}:"
                               f"{os.environ.get('POSTGRES_PASSWORD', 'password')}@"
                               f"{os.environ.get('POSTGRES_HOST', 'localhost')}:"
                               f"{os.environ.get('POSTGRES_PORT', '5432')}/"
                               f"{os.environ.get('POSTGRES_DB', 'pypos_local_db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        APP_NAME=os.environ.get('APP_NAME', 'PyPOS Local')
    )
    
    # Sobrescribir configuración si se provee configuración de prueba
    if test_config is not None:
        app.config.update(test_config)
    
    # Asegurar que existe el directorio de instancia
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Registrar blueprints
    from app.routes import home_routes, product_routes
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(product_routes.bp)
    
    # Ruta de bienvenida para verificar que la app está funcionando
    @app.route('/hello')
    def hello():
        return {'message': 'Bienvenido a PyPOS Local API!'}
    
    return app 