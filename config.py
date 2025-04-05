import os
from dotenv import load_dotenv

# Ruta base del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))
# Cargar variables de entorno desde el archivo .env
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Configuración base de la aplicación."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'

    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))

    # Configuración de la aplicación
    APP_NAME = os.environ.get('APP_NAME', 'PyPOS Local')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    TIMEZONE = os.environ.get('TIMEZONE', 'America/Argentina/Buenos_Aires')
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 10))
    
    # Configuración de archivos
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg').split(','))

    @staticmethod
    def init_app(app):
        """Inicialización de la aplicación."""
        # Crear el directorio de uploads si no existe
        uploads_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir) 