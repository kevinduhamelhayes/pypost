"""
Blueprint para las rutas principales de la aplicación.
"""
from flask import Blueprint, render_template, current_app

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('/')
def index():
    """
    Ruta principal que muestra la página de inicio.
    
    Returns:
        La plantilla de inicio renderizada
    """
    app_name = current_app.config.get('APP_NAME', 'PyPOS Local')
    return render_template('index.html', app_name=app_name)

@bp.route('/dashboard')
def dashboard():
    """
    Ruta para el panel de control principal.
    
    Returns:
        La plantilla del dashboard renderizada
    """
    return render_template('dashboard.html') 