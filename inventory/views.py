from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
import requests
from django.utils import timezone
from django.db.models import Q

from .models import Book
from .serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title', 'author', 'category', 'isbn']
    filterset_fields = ['category', 'supplier_country']

    def get_queryset(self):
        queryset = Book.objects.all()
        threshold = self.request.query_params.get('threshold')
        if threshold and threshold.isdigit():
            queryset = queryset.filter(stock_quantity__lt=int(threshold))
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__icontains=category)
            
        return queryset

    @action(detail=True, methods=['post'], url_path='calculate-price')
    def calculate_price(self, request, pk=None):
        try:
            book = self.get_object()
        except Book.DoesNotExist:
            return Response(
                {"error": "Libro no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            exchange_rate = self.get_exchange_rate()
     
            cost_local = float(book.cost_usd) * exchange_rate
            selling_price_local = cost_local * 1.4 
            
            book.selling_price_local = selling_price_local
            book.save()

            calculation_data = {
                "book_id": book.id,
                "cost_usd": float(book.cost_usd),
                "exchange_rate": exchange_rate,
                "cost_local": round(cost_local, 2),
                "margin_percentage": 40,
                "selling_price_local": round(selling_price_local, 2),
                "currency": "VES",
                "calculation_timestamp": timezone.now().isoformat()
            }

            return Response(calculation_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Capturar cualquier error durante el cálculo
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating price for book {pk}: {str(e)}")
            return Response(
                {"error": "Error interno al calcular el precio"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_exchange_rate(self):
        try:
            response = requests.get(
                'https://api.exchangerate-api.com/v4/latest/USD', 
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data['rates']['VES']
        except (requests.RequestException, KeyError, ValueError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error fetching exchange rate: {e}. Using default rate 0.85")
            return 0.85