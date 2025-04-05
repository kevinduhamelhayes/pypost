# PyPOS Local - Sistema de Punto de Venta

## Descripción
PyPOS Local es un sistema de Punto de Venta (PDV) de código abierto diseñado para funcionar localmente en tiendas y pequeños negocios. Está desarrollado con Python/Flask y PostgreSQL.

## Características
- Gestión de productos e inventario
- Control de stock y alertas
- Gestión de usuarios y permisos
- Gestión de clientes
- Sistema de ventas (próximamente)
- Informes y estadísticas

## Requisitos
- Docker y Docker Compose
- Git

## Instalación

1. Clonar el repositorio:
```bash
git clone <URL_DEL_REPOSITORIO>
cd pypos-local
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. Construir e iniciar los contenedores:
```bash
docker-compose up --build -d
```

4. Aplicar migraciones:
```bash
docker-compose exec web flask db upgrade
```

5. Crear datos de prueba (opcional):
```bash
docker-compose exec web flask seed-db
```

## Usuarios de Prueba
- Admin: usuario: admin, contraseña: admin123
- Cajero: usuario: cajero, contraseña: cajero123
- Gerente: usuario: gerente, contraseña: gerente123

## Uso
1. Acceder a la aplicación en http://localhost:5000
2. Iniciar sesión con las credenciales de prueba
3. Explorar las diferentes secciones del sistema

## Desarrollo
- El código sigue la estructura de blueprints de Flask
- Los modelos están en app/models/
- Las rutas están en app/routes/
- Las plantillas están en app/templates/

## Contribuir
Las contribuciones son bienvenidas. Por favor:
1. Haz fork del repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Envía un pull request

## Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles. 