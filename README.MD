# Sistema de Punto de Venta Local (PyPOS Local)

## Descripción

PyPOS Local es un sistema de Punto de Venta (PDV) de código abierto diseñado para funcionar localmente en tiendas y pequeños negocios. Está inspirado en la funcionalidad y modularidad de sistemas como Odoo, pero enfocado en una implementación más sencilla y autocontenida. Utiliza Python (con Flask) para el backend, PostgreSQL como base de datos y está diseñado para ser fácilmente desplegado usando Docker.

El desarrollo se realiza en un entorno Ubuntu, utilizando Cursor Cloud como IDE asistido por IA.

## Características Principales (Planificadas)

* **Gestión de Productos:**
    * Creación, edición, eliminación de productos.
    * Categorías de productos.
    * Gestión de precios y costos.
    * Soporte para variantes de productos (talla, color, etc.).
    * Códigos de barras / SKU.
* **Gestión de Inventario:**
    * Seguimiento de stock en tiempo real.
    * Ajustes de inventario (entrada/salida manual).
    * Notificaciones de bajo stock (opcional).
* **Proceso de Venta (PDV):**
    * Interfaz rápida para añadir productos al carrito (búsqueda, código de barras).
    * Cálculo de totales, impuestos y descuentos.
    * Múltiples métodos de pago.
    * Generación de tickets/recibos (impresión/digital).
    * Gestión de sesiones de caja (apertura/cierre).
* **Gestión de Clientes:**
    * Base de datos de clientes.
    * Historial de compras por cliente.
* **Gestión de Usuarios y Permisos:**
    * Roles de usuario (cajero, gerente, administrador).
    * Autenticación segura.
* **Informes:**
    * Informes de ventas (diarios, semanales, mensuales).
    * Informes por producto, categoría, cajero.
    * Informes de inventario.
* **Configuración:**
    * Configuración de la tienda (nombre, dirección, impuestos).
    * Configuración de periféricos (impresora de tickets - *requiere investigación adicional*).
* **Dockerizable:** Fácil de configurar y ejecutar en cualquier sistema compatible con Docker.

## Pila Tecnológica

* **Backend:** Python 3.x, Flask
* **Base de Datos:** PostgreSQL (>= 13)
* **ORM:** SQLAlchemy
* **Migraciones DB:** Alembic
* **Frontend:** HTML, CSS, JavaScript (inicialmente simple, podría evolucionar a un framework como Vue.js o React)
* **Contenedorización:** Docker, Docker Compose
* **Entorno de Desarrollo:** Ubuntu, Cursor Cloud
* **Servidor WSGI:** Gunicorn (para producción dentro de Docker)

## Prerrequisitos (Entorno Local - Ubuntu)

* Git ([https://git-scm.com/](https://git-scm.com/))
* Docker ([https://docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/))
* Docker Compose ([https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/))
* Cursor Cloud (o tu IDE preferido) ([https://cursor.sh/](https://cursor.sh/))
* Navegador Web moderno

*(Nota: Python y PostgreSQL se ejecutarán dentro de contenedores Docker, por lo que no es estrictamente necesario instalarlos directamente en el host, aunque tener Python/pip en el host puede ser útil).*

## Configuración y Puesta en Marcha (Usando Docker)

1.  **Clonar el Repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO_CUANDO_EXISTA>
    cd nombre-del-directorio-del-proyecto
    ```

2.  **Configurar Variables de Entorno:**
    * Copia el archivo de ejemplo `.env.example` a `.env`.
    * Edita el archivo `.env` y ajusta las variables según sea necesario (credenciales de la base de datos, claves secretas, etc.). **Asegúrate de usar contraseñas seguras.**

    *Ejemplo `.env.example`:*
    ```dotenv
    # PostgreSQL Settings
    POSTGRES_DB=pydv_local_db
    POSTGRES_USER=pydv_user
    POSTGRES_PASSWORD=tu_contraseña_segura_aqui
    POSTGRES_HOST=db # Nombre del servicio en docker-compose.yml
    POSTGRES_PORT=5432

    # Flask Settings
    SECRET_KEY=una_clave_secreta_muy_larga_y_aleatoria
    FLASK_ENV=development # Cambiar a 'production' para despliegue
    FLASK_APP=run.py # O el nombre de tu archivo de entrada principal
    ```

3.  **Construir e Iniciar los Contenedores:**
    * Este comando construirá las imágenes (si no existen o si el Dockerfile cambió) e iniciará los servicios definidos en `docker-compose.yml` (la aplicación Flask y la base de datos PostgreSQL) en segundo plano (`-d`).
    ```bash
    docker-compose up --build -d
    ```

4.  **Aplicar Migraciones de Base de Datos (Primera vez y cada vez que haya cambios en modelos):**
    * Asegúrate de que el contenedor de la aplicación (`backend` o como lo llames en `docker-compose.yml`) esté en ejecución.
    ```bash
    docker-compose exec backend flask db upgrade
    ```
    *(Nota: El comando exacto podría variar dependiendo de cómo integres Flask-Migrate/Alembic. Podría ser `docker-compose exec backend alembic upgrade head`)*

5.  **Acceder a la Aplicación:**
    * Abre tu navegador web y ve a `http://localhost:5000` (o el puerto que hayas configurado en `docker-compose.yml`).

## Uso de Docker Compose

* **Iniciar servicios:** `docker-compose up -d`
* **Detener servicios:** `docker-compose down`
* **Ver logs:** `docker-compose logs -f` (o `docker-compose logs -f backend` para ver solo los de la app)
* **Ejecutar comandos dentro de un contenedor:** `docker-compose exec <nombre_servicio> <comando>` (ej. `docker-compose exec backend bash`)
* **Reconstruir imágenes:** `docker-compose build` (o `docker-compose up --build`)

## Estructura del Proyecto (Sugerida)
pypos-local/
├── app/                      # Directorio principal de la aplicación Flask
│   ├── init.py           # Inicializa la aplicación Flask y extensiones
│   ├── models/               # Modelos de SQLAlchemy (productos, ventas, etc.)
│   │   ├── init.py
│   │   └── product.py
│   │   └── sale.py
│   │   └── ...
│   ├── routes/               # Blueprints de Flask para organizar rutas
│   │   ├── init.py
│   │   └── pos_routes.py
│   │   └── product_routes.py
│   │   └── ...
│   ├── services/             # Lógica de negocio (opcional, para mantener rutas limpias)
│   │   └── ...
│   ├── static/               # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── css/
│   │   └── js/
│   ├── templates/            # Plantillas HTML (Jinja2)
│   │   ├── base.html
│   │   └── pos.html
│   │   └── ...
│   └── utils/                # Funciones de utilidad
│       └── ...
├── migrations/               # Archivos de migración de Alembic
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/                    # Pruebas unitarias e de integración
│   └── ...
├── .env                      # Variables de entorno (NO versionar)
├── .env.example              # Ejemplo de variables de entorno (Versionar)
├── .gitignore                # Archivos y directorios a ignorar por Git
├── docker-compose.yml        # Definición de servicios Docker (app, db)
├── Dockerfile                # Instrucciones para construir la imagen Docker de la app
├── requirements.txt          # Dependencias de Python
├── run.py                    # Punto de entrada para ejecutar la aplicación Flask (o manage.py)
└── README.md                 # Este archivo


## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue las guías estándar de contribución (fork, branch, pull request).

## Licencia

[Especificar Licencia, e.g., MIT, GPL]

---

## Plan de Desarrollo Incremental

Aquí tienes un enfoque paso a paso para construir el sistema:

**Fase 0: Configuración Inicial y "Hola Mundo" Dockerizado**

1.  **Inicializar Proyecto:** Crea la estructura de directorios básica. Inicializa Git (`git init`).
2.  **Configurar Docker:**
    * Crea un `Dockerfile` básico para la aplicación Python/Flask. Empieza con una imagen oficial de Python. Instala dependencias desde `requirements.txt`.
    * Crea `docker-compose.yml` con dos servicios: `backend` (tu app Flask) y `db` (usando la imagen oficial de `postgres`). Configura volúmenes para persistencia de la base de datos y para el código fuente (para desarrollo en vivo). Define la red y las variables de entorno.
    * Crea un archivo `requirements.txt` inicial (solo `Flask`, `psycopg2-binary`, `python-dotenv`).
    * Crea un `run.py` (o `app.py`) súper simple con una ruta `/` que devuelva "Hola Mundo desde Flask y Docker!".
3.  **Probar:** Ejecuta `docker-compose up --build`. Verifica que puedas acceder a "Hola Mundo" en tu navegador y que el contenedor de PostgreSQL se inicie correctamente.
4.  **Configurar `.gitignore` y `.env.example`.**

**Fase 1: Conexión a Base de Datos y Migraciones**

1.  **Añadir Dependencias:** Agrega `SQLAlchemy`, `Flask-SQLAlchemy`, `Alembic`, `Flask-Migrate` a `requirements.txt`. Reconstruye la imagen (`docker-compose build backend`).
2.  **Configurar Flask-SQLAlchemy:** En `app/__init__.py`, inicializa la extensión SQLAlchemy y configura la URI de la base de datos leyéndola desde las variables de entorno (`DATABASE_URL` o las variables `POSTGRES_*`).
3.  **Configurar Flask-Migrate/Alembic:** Inicializa Alembic (`docker-compose exec backend flask db init`). Esto creará el directorio `migrations`. Asegúrate de que `env.py` detecte tus modelos.
4.  **Crear Primer Modelo:** Define un modelo simple en `app/models/product.py` (ej., `Product` con `id`, `name`, `price`).
5.  **Generar Migración:** Ejecuta `docker-compose exec backend flask db migrate -m "Initial product model"`.
6.  **Aplicar Migración:** Ejecuta `docker-compose exec backend flask db upgrade`. Verifica en la base de datos (puedes usar `docker-compose exec db psql -U <user> -d <db>` o una herramienta como DBeaver/pgAdmin conectándote al puerto expuesto) que la tabla se haya creado.

**Fase 2: CRUD Básico de Productos (API/Backend)**

1.  **Crear Rutas:** En `app/routes/product_routes.py`, crea un Blueprint de Flask.
2.  **Implementar Endpoints:**
    * `POST /api/products`: Crear un nuevo producto (recibe JSON, lo guarda en DB).
    * `GET /api/products`: Listar todos los productos.
    * `GET /api/products/<int:product_id>`: Obtener un producto específico.
    * `PUT /api/products/<int:product_id>`: Actualizar un producto.
    * `DELETE /api/products/<int:product_id>`: Eliminar un producto.
3.  **Registrar Blueprint:** Registra el blueprint en `app/__init__.py`.
4.  **Probar API:** Usa herramientas como `curl` o Postman/Insomnia para probar los endpoints interactuando directamente con tu backend en `http://localhost:5000/api/products`.

**Fase 3: Interfaz Frontend Básica (Listar y Añadir Productos)**

1.  **Crear Plantillas:** En `app/templates/`, crea `base.html` (estructura común) y `products.html`.
2.  **Ruta HTML:** Crea una ruta Flask (ej. `/products`) que renderice `products.html`.
3.  **Mostrar Productos:** En la ruta `/products`, obtén los productos de la base de datos y pásalos a la plantilla. Usa Jinja2 en `products.html` para iterar y mostrar la lista de productos en una tabla HTML.
4.  **Formulario Básico:** Añade un formulario HTML simple en `products.html` para ingresar el nombre y precio de un nuevo producto.
5.  **Ruta para Añadir:** Crea una ruta Flask (ej. `POST /products/add`) que reciba los datos del formulario, cree el producto usando el modelo SQLAlchemy, y redirija de nuevo a la página `/products`.
6.  **JavaScript Básico (Opcional):** Podrías empezar a usar JavaScript simple (o una librería como htmx) para hacer la adición de productos más dinámica (sin recargar toda la página), llamando al endpoint API `POST /api/products` que creaste antes.

**Fase 4: Lógica del PDV - Carrito de Compras**

1.  **Interfaz PDV:** Crea una nueva plantilla `pos.html` y una ruta `/pos`.
2.  **Selección de Productos:** Muestra una lista/cuadrícula de productos (quizás con búsqueda). Al hacer clic en un producto, añádelo a un "carrito".
3.  **Gestión del Carrito (Frontend):** Usa JavaScript para mantener el estado del carrito en el navegador (productos, cantidades, precios). Muestra el carrito y el total actualizándose dinámicamente.
4.  **Modelo de Venta:** Crea los modelos SQLAlchemy `Sale` (venta) y `SaleItem` (línea de venta). Una venta tendrá un total, fecha, etc. Un item de venta tendrá referencia al producto, cantidad, precio en el momento de la venta.
5.  **Endpoint "Finalizar Venta":** Crea una ruta API (ej. `POST /api/sales`) que reciba los datos del carrito (lista de productos y cantidades) desde el frontend (JavaScript).
6.  **Lógica Backend Venta:**
    * Crea un nuevo registro `Sale`.
    * Para cada ítem en el carrito recibido, crea un registro `SaleItem` asociado a la venta.
    * **Importante:** Actualiza el stock del producto (necesitarás añadir un campo `stock` al modelo `Product` y crear la migración correspondiente). Implementa esto dentro de una transacción de base de datos para asegurar la atomicidad (o la venta se realiza y el stock se descuenta, o nada ocurre).
    * Devuelve una confirmación al frontend.

**Fases Siguientes (Iteración y Mejora):**

* **Fase 5: Gestión de Inventario:** Añadir rutas/interfaces para ver stock, hacer ajustes manuales. Mejorar modelo `Product` (costo, stock mínimo).
* **Fase 6: Usuarios y Autenticación:** Añadir modelo `User` (con hash de contraseña). Implementar login/logout (usando `Flask-Login` o similar). Proteger rutas. Definir roles básicos.
* **Fase 7: Mejoras Interfaz PDV:** Búsqueda de productos más eficiente, soporte para código de barras (requiere JS y posiblemente acceso a hardware), manejo de descuentos, impuestos.
* **Fase 8: Informes:** Crear rutas y plantillas para mostrar informes básicos de ventas y stock, filtrando por fechas, productos, etc.
* **Fase 9: Clientes:** Modelo `Customer`, asociar ventas a clientes.
* **Fase 10: Sesiones de Caja:** Lógica para abrir/cerrar caja, registrar efectivo inicial/final.
* **Fase 11: Refinamiento y Pruebas:** Añadir más pruebas unitarias y de integración. Mejorar la interfaz de usuario (quizás adoptar un framework JS como Vue/React). Optimizar consultas a la base de datos. Revisar seguridad.
* **Fase 12: Configuración y Periféricos:** Interfaz para configurar datos de la tienda, impuestos. Investigar la integración con impresoras de tickets (puede ser complejo, a menudo se usan bibliotecas específicas o se generan archivos que la impresora pueda entender).

**Notas Importantes:**

* **Cursor Cloud:** Úsalo en cada paso para ayudarte a generar código, refactorizar, explicar conceptos y depurar.
* **Commits Frecuentes:** Haz `git commit` después de completar cada pequeño paso funcional.
* **Pruebas:** Aunque no se detallan aquí, intenta escribir pruebas (usando `pytest`, por ejemplo) a medida que desarrollas funcionalidades críticas, especialmente la lógica de negocio y las interacciones con la base de datos.
* **Framework Frontend:** Empezar con HTML/CSS/JS simple es bueno para entender los fundamentos. Si la interfaz se vuelve compleja, considera adoptar un framework como Vue.js, React o Svelte para gestionarla mejor.
* **Seguridad:** Presta atención a la seguridad desde el principio (validación de entradas, protección CSRF, almacenamiento seguro de contraseñas, configuración adecuada de CORS si la API y el frontend se sirven por separado).

Este plan te da una hoja de ruta clara. ¡Empieza por la Fase 0 y avanza paso a paso! ¡Mucha suerte con tu proyecto!





dame el modelo sugerido de bases de datos



Mostrar cuando piensa
¡Claro! Aquí tienes un modelo de base de datos relacional sugerido para PostgreSQL, pensado para las funcionalidades de un PDV como el que planeas. Se enfoca en las entidades principales y sus relaciones.

Usaremos convenciones comunes: nombres de tabla en plural y minúsculas, claves primarias id (autoincrementales), y claves foráneas nombretabla_id. Usaremos TIMESTAMP WITH TIME ZONE para fechas y horas para evitar problemas de zona horaria.

SQL

-- Eliminar tablas si existen para permitir la recreación (¡CUIDADO EN PRODUCCIÓN!)
-- DROP TABLE IF EXISTS payments CASCADE;
-- DROP TABLE IF EXISTS sale_items CASCADE;
-- DROP TABLE IF EXISTS inventory_adjustments CASCADE;
-- DROP TABLE IF EXISTS sales CASCADE;
-- DROP TABLE IF EXISTS cashier_sessions CASCADE;
-- DROP TABLE IF EXISTS products CASCADE;
-- DROP TABLE IF EXISTS categories CASCADE;
-- DROP TABLE IF EXISTS customers CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- Tabla para Usuarios del sistema (Cajeros, Gerentes, Administradores)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL, -- ¡NUNCA guardar contraseñas en texto plano!
    full_name VARCHAR(120),
    email VARCHAR(120) UNIQUE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('cashier', 'manager', 'admin')), -- Roles definidos
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Clientes
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(120) UNIQUE,
    phone VARCHAR(50),
    address TEXT,
    -- Podrías añadir más campos: DNI/CUIT, fecha de nacimiento, puntos de fidelidad, etc.
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Categorías de Productos
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL, -- Para subcategorías (opcional)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Productos
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE, -- Stock Keeping Unit (Código interno)
    barcode VARCHAR(100) UNIQUE, -- Código de barras
    purchase_price NUMERIC(12, 2) DEFAULT 0.00, -- Precio de costo
    sale_price NUMERIC(12, 2) NOT NULL CHECK (sale_price >= 0), -- Precio de venta
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    current_stock INTEGER NOT NULL DEFAULT 0, -- Cantidad actual en inventario
    low_stock_threshold INTEGER, -- Umbral para alertas de bajo stock (opcional)
    is_active BOOLEAN DEFAULT TRUE, -- Para "eliminar" suavemente o desactivar
    -- Podrías añadir: unidad de medida (kg, unidad, litro), impuestos aplicables, imagen, etc.
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_products_name ON products (name); -- Indexar campos usados frecuentemente para búsqueda

-- Tabla para Sesiones de Caja (Apertura/Cierre)
CREATE TABLE cashier_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT, -- Quién abrió/cerró
    start_datetime TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    end_datetime TIMESTAMPTZ,
    starting_cash NUMERIC(12, 2) DEFAULT 0.00, -- Efectivo inicial
    ending_cash_expected NUMERIC(12, 2), -- Calculado basado en ventas en efectivo
    ending_cash_actual NUMERIC(12, 2), -- Contado físicamente
    cash_difference NUMERIC(12, 2), -- Diferencia (calculada)
    status VARCHAR(20) NOT NULL CHECK (status IN ('open', 'closed')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_cashier_sessions_user_id ON cashier_sessions (user_id);
CREATE INDEX idx_cashier_sessions_status ON cashier_sessions (status);

-- Tabla para Ventas (Cabecera de la transacción)
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    sale_datetime TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT, -- Cajero que realizó la venta
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL, -- Cliente asociado (opcional)
    session_id INTEGER REFERENCES cashier_sessions(id) ON DELETE RESTRICT, -- Sesión de caja asociada
    total_amount NUMERIC(12, 2) NOT NULL, -- Suma de subtotales de items
    discount_amount NUMERIC(12, 2) DEFAULT 0.00, -- Descuento general sobre la venta
    tax_amount NUMERIC(12, 2) DEFAULT 0.00, -- Impuestos totales (podría ser más complejo)
    final_amount NUMERIC(12, 2) NOT NULL, -- Monto final a pagar (total - discount + tax)
    status VARCHAR(20) NOT NULL CHECK (status IN ('completed', 'pending', 'cancelled')), -- Estado de la venta
    notes TEXT,
    -- Podría añadirse: número de factura/ticket, tipo de comprobante, etc.
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_sales_sale_datetime ON sales (sale_datetime);
CREATE INDEX idx_sales_user_id ON sales (user_id);
CREATE INDEX idx_sales_customer_id ON sales (customer_id);
CREATE INDEX idx_sales_session_id ON sales (session_id);

-- Tabla para Items de Venta (Detalle de productos en una venta)
-- Tabla de unión entre 'sales' y 'products'
CREATE TABLE sale_items (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE, -- Si se borra la venta, se borran sus items
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT, -- No permitir borrar producto si está en ventas (o manejarlo)
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_at_sale NUMERIC(12, 2) NOT NULL, -- Precio del producto EN EL MOMENTO de la venta (importante por si cambia después)
    cost_at_sale NUMERIC(12, 2),           -- Costo del producto EN EL MOMENTO de la venta (para calcular margen)
    subtotal NUMERIC(12, 2) NOT NULL, -- quantity * price_at_sale
    -- Podría añadirse: descuento específico del item, impuesto específico del item
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    -- UNIQUE(sale_id, product_id) -- Podría ser útil si no permites añadir el mismo producto dos veces en la misma venta (se edita la cantidad)
);
CREATE INDEX idx_sale_items_sale_id ON sale_items (sale_id);
CREATE INDEX idx_sale_items_product_id ON sale_items (product_id);

-- Tabla para Pagos asociados a una Venta
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('cash', 'card', 'transfer', 'other', 'account_credit')), -- Tipos de pago
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
    payment_datetime TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    transaction_ref VARCHAR(100), -- Referencia para tarjeta, transferencia, etc.
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_payments_sale_id ON payments (sale_id);
CREATE INDEX idx_payments_payment_method ON payments (payment_method);

-- Tabla para Ajustes de Inventario (Entradas/Salidas manuales, Mermas, Stock inicial)
CREATE TABLE inventory_adjustments (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT, -- Quién hizo el ajuste
    adjustment_datetime TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    quantity_change INTEGER NOT NULL, -- Positivo para añadir stock, Negativo para quitar
    reason VARCHAR(255), -- Ej: 'Stock Inicial', 'Conteo Físico', 'Daño', 'Devolución Proveedor'
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_inventory_adjustments_product_id ON inventory_adjustments (product_id);
CREATE INDEX idx_inventory_adjustments_user_id ON inventory_adjustments (user_id);


-- Triggers (Ejemplo conceptual para actualizar timestamps - la implementación varía)
-- Podrías usar triggers para actualizar automáticamente los campos `updated_at`
-- CREATE OR REPLACE FUNCTION update_updated_at_column()
-- RETURNS TRIGGER AS $$
-- BEGIN
--    NEW.updated_at = CURRENT_TIMESTAMP;
--    RETURN NEW;
-- END;
-- $$ language 'plpgsql';

-- CREATE TRIGGER update_user_modtime BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
-- CREATE TRIGGER update_customer_modtime BEFORE UPDATE ON customers FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
-- ... y así para las otras tablas ...
Consideraciones Clave:

Inventario (products.current_stock): Este es el campo central para el stock. Debe actualizarse:
Decrementarse cuando se crea un sale_item (idealmente dentro de la misma transacción de la venta).
Incrementarse/Decrementarse cuando se crea un inventory_adjustment.
Esto requiere lógica en tu aplicación Python (backend) para asegurar la consistencia. Podrías usar triggers de base de datos, pero a menudo es más claro manejarlo en la lógica de la aplicación.
Precio y Costo en Venta (sale_items): Es crucial guardar price_at_sale y cost_at_sale en sale_items. Los precios y costos en la tabla products pueden cambiar con el tiempo, pero necesitas saber a qué precio/costo se vendió ese item específico en esa transacción para informes correctos y cálculo de márgenes.
Relaciones ON DELETE: Piensa cuidadosamente qué debe pasar si eliminas un registro al que otros hacen referencia.
ON DELETE RESTRICT: Impide eliminar si hay registros relacionados (más seguro por defecto).
ON DELETE CASCADE: Elimina registros relacionados (útil para sale_items si borras sales, pero peligroso en otros casos).
ON DELETE SET NULL: Pone la clave foránea a NULL (útil si la relación es opcional, como products.category_id).
Índices: Se han añadido índices básicos a las claves foráneas y algunos campos comunes de búsqueda (products.name). Añade más índices según las consultas que realices con más frecuencia para mejorar el rendimiento.
Tipos de Datos: NUMERIC(12, 2) es adecuado para la mayoría de valores monetarios (hasta 9,999,999,999.99). Ajusta la precisión si necesitas manejar valores más grandes.
Simplificaciones: Este modelo es un buen punto de partida. Podrías necesitar más tablas o campos para características avanzadas como:
Impuestos: Una tabla separada taxes y una tabla de unión product_taxes si los impuestos varían por producto.
Descuentos: Tablas para definir tipos de descuento (porcentaje, fijo) y aplicarlos a ventas o productos.
Proveedores: Tabla suppliers y relacionarla con productos o compras.
Compras: Tablas para registrar órdenes de compra a proveedores.
Variantes de Producto: Un esquema más complejo si necesitas manejar productos con atributos (talla, color) como entidades separadas.