from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Classe Font Awesome (ex: fa-laptop)")
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    supplier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_currency = models.CharField(max_length=3, default='USD', choices=[
        ('USD', 'USD'), ('EUR', 'EUR'), ('CFA', 'CFA')
    ])
    description = models.TextField()
    quantity_available = models.PositiveIntegerField()
    country_of_origin = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.supplier.username}"
    
    def get_absolute_url(self):
        return reverse('product-detail', args=[str(self.id)])

class Request(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='requests')
    desired_quantity = models.PositiveIntegerField()
    desired_country = models.CharField(max_length=100)
    description = models.TextField()
    max_budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    budget_currency = models.CharField(max_length=3, default='USD', choices=[
        ('USD', 'USD'), ('EUR', 'EUR'), ('CFA', 'CFA')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.product_name} - {self.buyer.username}"
    
    def get_absolute_url(self):
        return reverse('request-detail', args=[str(self.id)])

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product', 'request']