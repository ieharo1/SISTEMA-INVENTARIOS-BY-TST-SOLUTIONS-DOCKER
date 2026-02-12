from rest_framework import serializers
from apps.products.models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'full_path']
        read_only_fields = ['id', 'full_path']

class ProductSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    total_stock = serializers.IntegerField(read_only=True)
    margin = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'category', 'category_detail',
            'cost_price', 'sale_price', 'margin', 'image', 'is_active',
            'total_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']