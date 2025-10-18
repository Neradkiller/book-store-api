from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import re

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=17, unique=True)
    cost_usd = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    selling_price_local = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    stock_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    category = models.CharField(max_length=100)
    supplier_country = models.CharField(max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.is_valid_isbn():
            raise ValidationError({'isbn': 'ISBN debe tener 10 o 13 dígitos válidos'})

    def is_valid_isbn(self):
        isbn_clean = re.sub(r'[-\s]', '', self.isbn)
        
        if len(isbn_clean) not in [10, 13]:
            return False
        
        if len(isbn_clean) == 10:
            pattern = r'^\d{9}[\dX]$'
        else:
            pattern = r'^\d{13}$'
        
        return bool(re.match(pattern, isbn_clean))

    def __str__(self):
        return f"{self.title} - {self.author}"

    class Meta:
        db_table = 'books'
        ordering = ['id'] 