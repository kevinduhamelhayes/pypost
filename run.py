"""
PyPOS Local - Sistema de Punto de Venta Local
Este es el punto de entrada principal para la aplicación Flask.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True) 