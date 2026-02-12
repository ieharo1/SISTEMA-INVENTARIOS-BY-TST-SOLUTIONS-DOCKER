from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'description', 'category', 'cost_price', 'sale_price', 'image', 'is_active']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_sku(self):
        sku = self.cleaned_data['sku'].upper()
        if self.instance.pk:
            if Product.objects.filter(sku=sku, company=self.instance.company).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este SKU ya existe en su compañía')
        else:
            if Product.objects.filter(sku=sku, company=self.cleaned_data.get('company')).exists():
                raise forms.ValidationError('Este SKU ya existe en su compañía')
        return sku
    
    def clean(self):
        cleaned_data = super().clean()
        cost_price = cleaned_data.get('cost_price')
        sale_price = cleaned_data.get('sale_price')
        
        if cost_price and sale_price and sale_price < cost_price:
            raise forms.ValidationError('El precio de venta no puede ser menor al precio de costo')
        
        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance.pk:
            if Category.objects.filter(name=name, company=self.instance.company).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe una categoría con este nombre en su compañía')
        return name