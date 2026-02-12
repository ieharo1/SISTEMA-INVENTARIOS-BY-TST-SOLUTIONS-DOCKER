from rest_framework import serializers
from apps.warehouses.models import Warehouse

class WarehouseSerializer(serializers.ModelSerializer):
    total_products = serializers.IntegerField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'code', 'name', 'location', 'description',
            'is_active', 'total_products', 'total_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']