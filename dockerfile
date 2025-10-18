FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Comando mejorado
CMD ["sh", "-c", "python wait_for_db.py && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]