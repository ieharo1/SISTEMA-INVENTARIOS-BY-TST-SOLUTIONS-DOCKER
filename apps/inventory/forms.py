from django import forms
from .models import Inventory

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'warehouse', 'min_stock', 'max_stock', 'location']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select select2'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'max_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }