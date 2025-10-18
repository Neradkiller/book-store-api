import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock
import requests
from .models import Book
from .serializers import BookSerializer

class BookModelTest(TestCase):
    """Pruebas para el modelo Book"""
    
    def setUp(self):
        """Configuración inicial para todas las pruebas"""
        self.book_data = {
            'title': 'El Quijote',
            'author': 'Miguel de Cervantes',
            'isbn': '978-84-376-0494-7',
            'cost_usd': Decimal('15.99'),  
            'stock_quantity': 25,
            'category': 'Literatura Clásica',
            'supplier_country': 'ES'
        }
    
    def test_create_book_success(self):
        """Prueba: Crear un libro exitosamente"""
        book = Book.objects.create(**self.book_data)
        self.assertEqual(book.title, 'El Quijote')
        self.assertEqual(book.author, 'Miguel de Cervantes')
        self.assertEqual(book.isbn, '978-84-376-0494-7')
        self.assertEqual(book.cost_usd, Decimal('15.99')) 
        self.assertEqual(book.stock_quantity, 25)
        self.assertEqual(book.category, 'Literatura Clásica')
        self.assertEqual(book.supplier_country, 'ES')
    
    def test_isbn_validation_valid(self):
        """Prueba: Validación de ISBN válido"""
        book1 = Book(**self.book_data)
        book1.full_clean()  
        book2_data = {**self.book_data, 'isbn': '8420636432', 'cost_usd': Decimal('14.50')}
        book2 = Book(**book2_data)
        book2.full_clean() 
    
    def test_isbn_validation_invalid(self):
        """Prueba: Validación de ISBN inválido"""
        book_data = {**self.book_data, 'isbn': '123', 'cost_usd': Decimal('12.50')}
        book = Book(**book_data)
        with self.assertRaises(ValidationError):
            book.full_clean()
        
        book_data = {**self.book_data, 'isbn': '978-84-376-0494-A', 'cost_usd': Decimal('12.50')}
        book = Book(**book_data)
        with self.assertRaises(ValidationError):
            book.full_clean()
    
    def test_cost_usd_validation(self):
        """Prueba: Validación de costo USD mayor a 0"""
        book_data = {**self.book_data, 'cost_usd': Decimal('0.00')}
        book = Book(**book_data)
        with self.assertRaises(ValidationError):
            book.full_clean()
        
        book_data = {**self.book_data, 'cost_usd': Decimal('-10.00')}
        book = Book(**book_data)
        with self.assertRaises(ValidationError):
            book.full_clean()
    
    def test_stock_quantity_validation(self):
        """Prueba: Validación de stock no negativo"""
        book_data = {**self.book_data, 'stock_quantity': -5, 'cost_usd': Decimal('12.50')}
        book = Book(**book_data)
        with self.assertRaises(ValidationError):
            book.full_clean()
    
    def test_unique_isbn(self):
        """Prueba: ISBN debe ser único"""
        Book.objects.create(**self.book_data)
        duplicate_book = Book(**self.book_data)
        with self.assertRaises(ValidationError):
            duplicate_book.full_clean()


class BookSerializerTest(TestCase):
    """Pruebas para el serializer BookSerializer"""
    
    def setUp(self):
        self.valid_data = {
            'title': 'Cien años de soledad',
            'author': 'Gabriel García Márquez',
            'isbn': '978-84-9759-275-5',
            'cost_usd': '18.50', 
            'stock_quantity': 15,
            'category': 'Realismo Mágico',
            'supplier_country': 'CO'
        }
    
    def test_valid_serializer(self):
        """Prueba: Serializer con datos válidos"""
        serializer = BookSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_isbn_serializer(self):
        """Prueba: Serializer con ISBN inválido"""
        invalid_data = {**self.valid_data, 'isbn': '123'}
        serializer = BookSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('isbn', serializer.errors)
    
    def test_duplicate_isbn_serializer(self):
        """Prueba: Serializer con ISBN duplicado"""
        Book.objects.create(
            title='Cien años de soledad',
            author='Gabriel García Márquez',
            isbn='978-84-9759-275-5',
            cost_usd=Decimal('18.50'),
            stock_quantity=15,
            category='Realismo Mágico',
            supplier_country='CO'
        )
        
        serializer = BookSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('isbn', serializer.errors)


class BookAPITest(APITestCase):
    """Pruebas para los endpoints de la API"""
    
    def setUp(self):
        """Configuración inicial para pruebas de API"""
        self.client = APIClient()
        self.book_data = {
            'title': 'El Quijote',
            'author': 'Miguel de Cervantes',
            'isbn': '978-84-376-0494-7',
            'cost_usd': '15.99',  
            'stock_quantity': 25,
            'category': 'Literatura Clásica',
            'supplier_country': 'ES'
        }
        self.book = Book.objects.create(
            title='El Quijote',
            author='Miguel de Cervantes',
            isbn='978-84-376-0494-7',
            cost_usd=Decimal('15.99'),
            stock_quantity=25,
            category='Literatura Clásica',
            supplier_country='ES'
        )
        self.list_url = reverse('book-list')
        self.detail_url = reverse('book-detail', kwargs={'pk': self.book.pk})
        self.calculate_price_url = reverse('book-calculate-price', kwargs={'pk': self.book.pk})
    
    def test_get_books_list(self):
        """Prueba: Obtener lista de libros"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_book_success(self):
        """Prueba: Crear libro exitosamente via API"""
        new_book_data = {
            'title': '1984',
            'author': 'George Orwell',
            'isbn': '978-84-9759-327-1',
            'cost_usd': '12.99',
            'stock_quantity': 10,
            'category': 'Ciencia Ficción',
            'supplier_country': 'US'
        }
        response = self.client.post(self.list_url, new_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
    
    def test_create_book_duplicate_isbn(self):
        """Prueba: Intentar crear libro con ISBN duplicado"""
        response = self.client.post(self.list_url, self.book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('isbn', response.data)
    
    def test_get_book_detail(self):
        """Prueba: Obtener detalle de un libro"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book.title)
        self.assertEqual(response.data['isbn'], self.book.isbn)
    
    def test_update_book(self):
        """Prueba: Actualizar libro existente"""
        update_data = {
            'title': 'Don Quijote de la Mancha',
            'author': 'Miguel de Cervantes',
            'isbn': '978-84-376-0494-7',
            'cost_usd': '16.50',
            'stock_quantity': 30,
            'category': 'Literatura Clásica',
            'supplier_country': 'ES'
        }
        response = self.client.put(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Don Quijote de la Mancha')
        self.assertEqual(self.book.cost_usd, Decimal('16.50'))
    
    def test_delete_book(self):
        """Prueba: Eliminar libro"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
    
    def test_filter_by_category(self):
        """Prueba: Filtrar libros por categoría"""
        Book.objects.create(
            title='Rayuela',
            author='Julio Cortázar',
            isbn='978-84-376-0123-6',
            cost_usd=Decimal('14.50'),
            stock_quantity=8,
            category='Literatura Contemporánea',
            supplier_country='AR'
        )
        
        response = self.client.get(self.list_url, {'category': 'Literatura Clásica'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['category'], 'Literatura Clásica')
    
    def test_low_stock_filter(self):
        """Prueba: Filtrar libros con stock bajo"""
        Book.objects.create(
            title='Libro con stock bajo',
            author='Autor',
            isbn='978-84-376-0123-7',
            cost_usd=Decimal('10.00'),
            stock_quantity=5,
            category='Ficción',
            supplier_country='MX'
        )
        
        response = self.client.get(self.list_url, {'threshold': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['stock_quantity'], 5)
    
    def test_search_books(self):
        """Prueba: Buscar libros"""
        response = self.client.get(self.list_url, {'search': 'Cervantes'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['author'], 'Miguel de Cervantes')
    
    @patch('inventory.views.requests.get')
    def test_calculate_price_success(self, mock_get):
        """Prueba: Calcular precio exitosamente"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'rates': {'VES': 0.85}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        response = self.client.post(self.calculate_price_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book_id'], self.book.pk)
        self.assertEqual(response.data['cost_usd'], 15.99)
        self.assertEqual(response.data['exchange_rate'], 0.85)
        self.assertEqual(response.data['margin_percentage'], 40)
        self.assertEqual(response.data['currency'], 'VES')
        self.book.refresh_from_db()
        self.assertEqual(float(self.book.selling_price_local), 19.03)
    
    @patch('inventory.views.requests.get')
    def test_calculate_price_api_fallback(self, mock_get):
        """Prueba: Calcular precio con fallback cuando la API externa falla"""
        mock_get.side_effect = requests.RequestException('API no disponible')
        
        response = self.client.post(self.calculate_price_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['exchange_rate'], 0.85)
    
    def test_calculate_price_nonexistent_book(self):
        """Prueba: Intentar calcular precio para libro inexistente"""
        invalid_url = reverse('book-calculate-price', kwargs={'pk': 999})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PaginationTest(APITestCase):
    """Pruebas para la paginación"""
    
    def setUp(self):
        for i in range(25):  
            Book.objects.create(
                title=f'Libro {i}',
                author=f'Autor {i}',
                isbn=f'978-84-376-{i:04d}-{i}',
                cost_usd=Decimal(str(10.00 + i)),  
                stock_quantity=i,
                category='Ficción',
                supplier_country='ES'
            )
    
    def test_pagination_default(self):
        """Prueba: Paginación por defecto (5 items por página)"""
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(len(response.data['results']), 5)  
        self.assertIsNotNone(response.data['next'])
    
    def test_pagination_custom_page(self):
        """Prueba: Navegación entre páginas"""
        response = self.client.get(reverse('book-list'), {'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  
        self.assertIsNotNone(response.data['previous'])