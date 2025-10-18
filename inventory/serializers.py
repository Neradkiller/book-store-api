from rest_framework import serializers
from .models import Book
import re

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'cost_usd', 
            'selling_price_local', 'stock_quantity', 'category',
            'supplier_country', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_cost_usd(self, value):
        if value <= 0:
            raise serializers.ValidationError("El costo debe ser mayor a 0")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad en stock no puede ser negativa")
        return value

    def validate_isbn(self, value):
        isbn_clean = re.sub(r'[-\s]', '', value)
        
        if len(isbn_clean) not in [10, 13]:
            raise serializers.ValidationError("ISBN debe tener 10 o 13 dígitos")
        
        if len(isbn_clean) == 10:
            pattern = r'^\d{9}[\dX]$'
        else:
            pattern = r'^\d{13}$'
        
        if not re.match(pattern, isbn_clean):
            raise serializers.ValidationError("Formato de ISBN inválido")
        
        return value

    def create(self, validated_data):
        isbn = validated_data.get('isbn')
        if Book.objects.filter(isbn=isbn).exists():
            raise serializers.ValidationError({"isbn": "Ya existe un libro con este ISBN"})
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        isbn = validated_data.get('isbn', instance.isbn)
        if Book.objects.filter(isbn=isbn).exclude(id=instance.id).exists():
            raise serializers.ValidationError({"isbn": "Ya existe un libro con este ISBN"})
        
        return super().update(instance, validated_data)