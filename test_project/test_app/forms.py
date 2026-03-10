from django import forms
from .models import Product, JSONProduct

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name_default', 'name_it', 'description_default', 'description_it']

class JSONProductForm(forms.ModelForm):
    class Meta:
        model = JSONProduct
        fields = ['name', 'description']
