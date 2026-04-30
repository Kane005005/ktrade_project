from django import forms
from .models import Product, Request, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'estimated_price', 'price_currency', 
                 'description', 'quantity_available', 'country_of_origin', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['product_name', 'category', 'desired_quantity', 'desired_country',
                 'description', 'max_budget', 'budget_currency']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SearchForm(forms.Form):
    q = forms.CharField(required=False, label='Rechercher')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="Toutes les catégories")
    country = forms.CharField(required=False, label='Pays')
    min_price = forms.DecimalField(required=False, decimal_places=2)
    max_price = forms.DecimalField(required=False, decimal_places=2)
    user_type = forms.ChoiceField(required=False, choices=[
        ('', 'Tous'), ('fournisseur', 'Fournisseurs'), ('vendeur', 'Acheteurs')
    ])