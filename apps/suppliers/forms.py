from django import forms
from .models import Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'identification', 'name', 'contact_name', 'phone', 'email',
            'address', 'city', 'country', 'website', 'notes', 'is_active'
        ]
        widgets = {
            'identification': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_identification(self):
        identification = self.cleaned_data['identification'].upper()
        if self.instance.pk:
            if Supplier.objects.filter(identification=identification).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Esta identificación fiscal ya está registrada')
        else:
            if Supplier.objects.filter(identification=identification).exists():
                raise forms.ValidationError('Esta identificación fiscal ya está registrada')
        return identification