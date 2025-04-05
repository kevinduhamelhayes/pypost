"""
Comandos CLI personalizados para la aplicación.
"""
import click
from flask.cli import with_appcontext
from app.utils.seed_data import create_test_data

def register_commands(app):
    """Registra comandos CLI personalizados."""
    
    @app.cli.command('seed-db')
    @with_appcontext
    def seed_db():
        """Crea datos de prueba en la base de datos."""
        if click.confirm('¿Estás seguro? Esto creará datos de prueba en la base de datos.'):
            create_test_data()
            click.echo('Datos de prueba creados exitosamente.') 