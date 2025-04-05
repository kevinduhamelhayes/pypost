FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Puerto en el que se ejecuta la aplicación
EXPOSE 5000

# Entrypoint usando gunicorn para producción
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"] 