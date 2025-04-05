# PyPOS Local

Sistema de Punto de Venta Local desarrollado con Flask y PostgreSQL, ideal para pequeños negocios.

## Características

- Gestión completa de productos (CRUD)
- Interfaz de usuario moderna y responsiva
- Base de datos PostgreSQL robusta
- Implementado como contenedores Docker para facilitar su despliegue
- Documentación completa y código limpio

## Requisitos previos

- Docker y Docker Compose
- Git (para clonar el repositorio)

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/pypos-local.git
   cd pypos-local
   ```

2. Crear archivo de variables de entorno:
   ```bash
   cp .env.example .env
   ```
   Editar `.env` con tus propias configuraciones.

3. Levantar los contenedores con Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Ejecutar migraciones de la base de datos:
   ```bash
   docker-compose exec backend flask db upgrade
   ```

5. Acceder a la aplicación:
   - Abrir el navegador y visitar `http://localhost:5000`

## Estructura del proyecto

```
pypos-local/
├── app/                      # Directorio principal de la aplicación Flask
│   ├── __init__.py           # Inicializa la aplicación Flask y extensiones
│   ├── models/               # Modelos de SQLAlchemy
│   │   ├── __init__.py
│   │   └── product.py        # Modelo de productos
│   ├── routes/               # Rutas de la aplicación
│   │   ├── __init__.py
│   │   ├── home_routes.py    # Rutas de la página principal
│   │   └── product_routes.py # Rutas para productos
│   ├── static/               # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   └── templates/            # Plantillas HTML (Jinja2)
│       ├── base.html
│       ├── index.html
│       ├── dashboard.html
│       └── products/
│           ├── index.html
│           ├── new.html
│           ├── edit.html
│           └── show.html
├── migrations/               # Migraciones de la base de datos
├── .env.example              # Plantilla para variables de entorno
├── .gitignore                # Ignora archivos en Git
├── docker-compose.yml        # Configuración de Docker Compose
├── Dockerfile                # Configuración para construir la imagen Docker
├── requirements.txt          # Dependencias de Python
└── run.py                    # Punto de entrada para ejecutar la aplicación
```

## Uso

### Panel de control

El panel de control ofrece un resumen del negocio con estadísticas y acceso rápido a las funciones más utilizadas.

### Gestión de productos

- **Listar productos**: Navega a la sección "Productos" para ver todos los productos registrados.
- **Crear producto**: Usa el botón "Nuevo Producto" para añadir un producto al inventario.
- **Ver detalles**: Haz clic en el icono de "ojo" junto a un producto para ver su información detallada.
- **Editar producto**: Usa el icono de "lápiz" para modificar la información de un producto.
- **Eliminar producto**: El icono de "papelera" permite eliminar productos (se solicitará confirmación).

## Desarrollo

Si deseas trabajar en el proyecto sin Docker:

1. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno para desarrollo local.

4. Ejecutar la aplicación:
   ```bash
   flask run
   ```

## Contribuciones

Las contribuciones son bienvenidas. Por favor, crea un fork del repositorio y envía un pull request para proponer mejoras.

## Licencia

Este proyecto está licenciado bajo la licencia MIT - ver el archivo LICENSE para más detalles. 