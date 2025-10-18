# Bookstore Inventory API

API REST para sistema de gestión de inventario de librerías con validación de precios en tiempo real, desarrollada con Django REST Framework.

## 📋 Características

- ✅ Gestión completa de inventario de libros (CRUD)
- ✅ Cálculo automático de precios con tasas de cambio en tiempo real
- ✅ Validación de ISBN y reglas de negocio
- ✅ Filtros y búsquedas avanzadas
- ✅ Base de datos MySQL
- ✅ Dockerizado para fácil despliegue
- ✅ API RESTful documentada

## 🚀 Requisitos Previos

### Opción 1: Con Docker (Recomendado)
- Docker 20.10+
- Docker Compose 2.0+

### Opción 2: Sin Docker
- Python 3.11+
- MySQL 8.0+
- pip (gestor de paquetes de Python)

## 📦 Instalación y Ejecución

### Método 1: Usando Docker (Recomendado)

```
git clone <repository-url>
cd bookstore-inventory-api
docker-compose up --build
```

La aplicación estará disponible en: `http://localhost:8000`

### Método 2: Instalación Manual

```
git clone <repository-url>
cd bookstore-inventory-api

python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt

export DB_HOST=localhost
export DB_NAME=book-store
export DB_USER=book-user
export DB_PASSWORD=book-password
export DEBUG=True

python manage.py migrate
python manage.py runserver
```

## 🗄️ Configuración de Base de Datos

```
CREATE DATABASE `book-store`;
CREATE USER 'book-user'@'localhost' IDENTIFIED BY 'book-password';
GRANT ALL PRIVILEGES ON `book-store`.* TO 'book-user'@'localhost';
FLUSH PRIVILEGES;
```

## 📚 Endpoints de la API

### Base URL: `http://localhost:8000/api`

### 1. Listar Todos los Libros
**GET** `/books/`

```
curl -X GET "http://localhost:8000/api/books/"
```

**Respuesta:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "El Quijote",
      "author": "Miguel de Cervantes",
      "isbn": "978-84-376-0494-7",
      "cost_usd": "15.99",
      "selling_price_local": null,
      "stock_quantity": 25,
      "category": "Literatura Clásica",
      "supplier_country": "ES",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

**Para el paginado:**

```
curl -X GET "http://localhost:8000/api/books/?page=n"
```

Si la pagina no esta disponible arrojara un error

### 2. Crear Libro
**POST** `/books/`

```
curl -X POST "http://localhost:8000/api/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cien años de soledad",
    "author": "Gabriel García Márquez",
    "isbn": "978-84-9759-275-5",
    "cost_usd": 18.50,
    "stock_quantity": 15,
    "category": "Realismo Mágico",
    "supplier_country": "CO"
  }'
```

**Campos requeridos:**
- `title` (string): Título del libro
- `author` (string): Autor del libro
- `isbn` (string): ISBN válido (10 o 13 dígitos)
- `cost_usd` (decimal): Costo en USD (> 0)
- `stock_quantity` (integer): Cantidad en stock (≥ 0)
- `category` (string): Categoría del libro
- `supplier_country` (string): Código de país del proveedor (2 caracteres)

### 3. Obtener Libro por ID
**GET** `/books/{id}/`

```
curl -X GET "http://localhost:8000/api/books/1/"
```

**Respuesta:**
```json
{
  "id": 1,
  "title": "El Quijote",
  "author": "Miguel de Cervantes",
  "isbn": "978-84-376-0494-7",
  "cost_usd": "15.99",
  "selling_price_local": null,
  "stock_quantity": 25,
  "category": "Literatura Clásica",
  "supplier_country": "ES",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### 4. Actualizar Libro
**PUT** `/books/{id}/`

```
curl -X PUT "http://localhost:8000/api/books/1/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Don Quijote de la Mancha",
    "author": "Miguel de Cervantes",
    "isbn": "978-84-376-0494-7",
    "cost_usd": "16.50",
    "stock_quantity": 30,
    "category": "Literatura Clásica",
    "supplier_country": "ES"
  }'
```

**Respuesta:**
```json
{
  "id": 1,
  "title": "Don Quijote de la Mancha",
  "author": "Miguel de Cervantes",
  "isbn": "978-84-376-0494-7",
  "cost_usd": "16.50",
  "selling_price_local": null,
  "stock_quantity": 30,
  "category": "Literatura Clásica",
  "supplier_country": "ES",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T11:30:00Z"
}
```

### 5. Eliminar Libro
**DELETE** `/books/{id}/`

```
curl -X DELETE "http://localhost:8000/api/books/1/"
```

**Respuesta:** `204 No Content`

### 6. Calcular Precio de Venta
**POST** `/books/{id}/calculate_price/`

```
curl -X POST "http://localhost:8000/api/books/1/calculate_price/"
```

**Respuesta:**
```json
{
  "book_id": 1,
  "cost_usd": 15.99,
  "exchange_rate": 0.85,
  "cost_local": 13.59,
  "margin_percentage": 40,
  "selling_price_local": 19.03,
  "currency": "VES",
  "calculation_timestamp": "2025-01-15T10:30:00Z"
}
```

### 7. Buscar por Categoría
**GET** `/books/?category={categoria}`

```
curl -X GET "http://localhost:8000/api/books/?category=Literatura%20Clásica"
```

**Respuesta:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "El Quijote",
      "author": "Miguel de Cervantes",
      "isbn": "978-84-376-0494-7",
      "cost_usd": "15.99",
      "selling_price_local": null,
      "stock_quantity": 25,
      "category": "Literatura Clásica",
      "supplier_country": "ES",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### 8. Libros con Stock Bajo
**GET** `/books/?threshold={cantidad}`

```
curl -X GET "http://localhost:8000/api/books/?threshold=10"
```

**Respuesta:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 3,
      "title": "El amor en los tiempos del cólera",
      "author": "Gabriel García Márquez",
      "isbn": "978-84-339-3132-2",
      "cost_usd": "14.75",
      "selling_price_local": null,
      "stock_quantity": 5,
      "category": "Realismo Mágico",
      "supplier_country": "CO",
      "created_at": "2025-01-15T12:00:00Z",
      "updated_at": "2025-01-15T12:00:00Z"
    }
  ]
}
```

### 9. Búsqueda General
**GET** `/books/?search={termino}`

```
curl -X GET "http://localhost:8000/api/books/?search=Cervantes"
```

**Respuesta:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "El Quijote",
      "author": "Miguel de Cervantes",
      "isbn": "978-84-376-0494-7",
      "cost_usd": "15.99",
      "selling_price_local": null,
      "stock_quantity": 25,
      "category": "Literatura Clásica",
      "supplier_country": "ES",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

## 🔍 Filtros y Parámetros de Búsqueda

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `category` | Filtrar por categoría | `?category=Ficción` |
| `threshold` | Stock menor que el valor | `?threshold=10` |
| `search` | Búsqueda en título, autor, categoría | `?search=García` |
| `page` | Paginación | `?page=2` |

## ⚠️ Validaciones y Reglas de Negocio

- **ISBN:** Debe ser único y tener formato válido (10 o 13 dígitos)
- **Costo USD:** Debe ser mayor a 0
- **Stock:** No puede ser negativo
- **País proveedor:** Código de 2 caracteres (ISO)
- **Precio de venta:** Se calcula automáticamente con margen del 40%

## 🐛 Manejo de Errores

La API retorna códigos HTTP estándar:

- `200 OK` - Operación exitosa
- `201 Created` - Recurso creado exitosamente
- `400 Bad Request` - Datos de entrada inválidos
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

**Ejemplo de error de validación:**
```json
{
  "isbn": ["Ya existe un libro con este ISBN"]
}
```

## 🛠️ Comandos Útiles

### Con Docker
```
docker-compose logs -f web
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose down
docker-compose down -v
```

### Sin Docker
```
python manage.py createsuperuser
python manage.py test
python manage.py showmigrations
```

## 📊 Estructura del Proyecto

```
bookstore-inventory-api/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── wait_for_db.py
├── manage.py
├── bookstore/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── inventory/
    ├── models.py
    ├── views.py
    ├── serializers.py
    ├── urls.py
    └── tests.py
```

## 🔄 Flujo de Cálculo de Precios

1. **Obtiene** el `cost_usd` del libro
2. **Consulta** la tasa de cambio actual USD→VES via API externa
3. **Aplica** margen de ganancia del 40%
4. **Actualiza** `selling_price_local` en la base de datos
5. **Retorna** el cálculo detallado

**API de tasas de cambio:** `https://api.exchangerate-api.com/v4/latest/USD`

## 🧪 Ejemplos de Prueba Completa

```
#!/bin/bash

BASE_URL="http://localhost:8000/api"

echo "=== Prueba completa de la API Bookstore ==="

echo "1. Creando libro..."
curl -X POST $BASE_URL/books/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "isbn": "978-84-9759-327-1",
    "cost_usd": 12.99,
    "stock_quantity": 8,
    "category": "Ciencia Ficción",
    "supplier_country": "US"
  }'

echo "2. Calculando precio..."
curl -X POST "$BASE_URL/books/1/calculate_price/"

echo "3. Libros con stock bajo:"
curl -X GET "$BASE_URL/books/?threshold=10"

echo "4. Buscando por categoría:"
curl -X GET "$BASE_URL/books/?category=Ciencia%20Ficción"

echo "5. Listando todos los libros:"
curl -X GET "$BASE_URL/books/"
```

## Ejecucion de pruebas

```
# Ejecutar todas las pruebas
docker-compose exec web python manage.py test

# Ejecutar pruebas específicas
docker-compose exec web python manage.py test inventory.tests.BookModelTest
docker-compose exec web python manage.py test inventory.tests.BookAPITest
```

## 📞 Soporte

Si encuentras problemas:

1. Verifica que todos los contenedores estén ejecutándose: `docker-compose ps`
2. Revisa los logs: `docker-compose logs web`
3. Verifica la conexión a la base de datos
4. Asegúrate de que las migraciones se ejecutaron correctamente

## 📄 Licencia

Este proyecto es para fines de demostración técnica.

---