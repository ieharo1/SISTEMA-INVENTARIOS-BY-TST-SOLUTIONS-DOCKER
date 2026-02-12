from django import forms
from .models import Warehouse

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['code', 'name', 'location', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_code(self):
        code = self.cleaned_data['code'].upper()
        if self.instance.pk:
            if Warehouse.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este código ya está en uso')
        else:
            if Warehouse.objects.filter(code=code).exists():
                raise forms.ValidationError('Este código ya está en uso')
        return code
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance.pk:
            if Warehouse.objects.filter(name=name, company=self.instance.company).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe una bodega con este nombre en su compañía')
        return name