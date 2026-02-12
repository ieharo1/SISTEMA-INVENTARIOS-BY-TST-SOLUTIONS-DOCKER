from django import forms
from .models import Movement

class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ['movement_type', 'product', 'quantity', 'warehouse_from', 'warehouse_to', 'unit_cost', 'reference', 'notes']
        widgets = {
            'movement_type': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select select2'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'warehouse_from': forms.Select(attrs={'class': 'form-select'}),
            'warehouse_to': forms.Select(attrs={'class': 'form-select'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        warehouse_from = cleaned_data.get('warehouse_from')
        warehouse_to = cleaned_data.get('warehouse_to')
        
        if movement_type == 'TRANSFER':
            if not warehouse_from or not warehouse_to:
                raise forms.ValidationError('Para transferencias necesita bodega origen y destino')
            if warehouse_from == warehouse_to:
                raise forms.ValidationError('La bodega origen y destino deben ser diferentes')
        
        return cleaned_data