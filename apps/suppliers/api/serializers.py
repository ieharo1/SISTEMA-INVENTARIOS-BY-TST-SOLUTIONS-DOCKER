from rest_framework import serializers
from apps.suppliers.models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'identification', 'name', 'contact_name',
            'phone', 'email', 'address', 'city', 'country',
            'website', 'notes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']