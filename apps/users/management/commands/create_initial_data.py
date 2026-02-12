from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from apps.users.models import User, Company
from apps.products.models import Product, Category
from apps.warehouses.models import Warehouse
from apps.suppliers.models import Supplier
import uuid

class Command(BaseCommand):
    help = 'Crea datos iniciales para el sistema'
    
    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Creando datos iniciales...')
        
        # Crear grupos y permisos
        self.create_groups_and_permissions()
        
        # Crear compañía por defecto
        company = self.create_default_company()
        
        # Crear superusuario
        self.create_superuser(company)
        
        # Crear datos de ejemplo
        self.create_sample_data(company)
        
        self.stdout.write(self.style.SUCCESS('Datos iniciales creados exitosamente!'))
    
    def create_groups_and_permissions(self):
        """Crear grupos y asignar permisos"""
        groups_permissions = {
            'Admin': ['add', 'change', 'delete', 'view'],
            'Manager': ['add', 'change', 'view'],
            'Operador': ['view'],
        }
        
        models = [
            'user', 'company', 'product', 'category',
            'warehouse', 'supplier', 'inventory', 'movement'
        ]
        
        for group_name, actions in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(f'  Grupo creado: {group_name}')
                
                # Asignar permisos
                for model_name in models:
                    for action in actions:
                        try:
                            perm_name = f'{action}_{model_name}'
                            perm = Permission.objects.get(codename=perm_name)
                            group.permissions.add(perm)
                        except Permission.DoesNotExist:
                            pass
    
    def create_default_company(self):
        """Crear compañía por defecto"""
        company, created = Company.objects.get_or_create(
            rut='76.123.456-7',
            defaults={
                'name': 'Empresa Demo S.A.',
                'address': 'Av. Principal 123',
                'phone': '+56 9 1234 5678',
                'email': 'contacto@empresademo.cl',
            }
        )
        
        if created:
            self.stdout.write(f'  Compañía creada: {company.name}')
        
        return company
    
    def create_superuser(self, company):
        """Crear superusuario"""
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='Sistema',
                company=company
            )
            
            # Asignar grupo Admin
            admin_group = Group.objects.get(name='Admin')
            user.groups.add(admin_group)
            
            self.stdout.write('  Superusuario creado: admin / admin123')
    
    def create_sample_data(self, company):
        """Crear datos de ejemplo"""
        
        # Categorías
        categorias = [
            {'name': 'Electrónica', 'description': 'Productos electrónicos'},
            {'name': 'Computación', 'description': 'Computadores y accesorios', 'parent': 'Electrónica'},
            {'name': 'Audio', 'description': 'Equipos de audio', 'parent': 'Electrónica'},
            {'name': 'Oficina', 'description': 'Artículos de oficina'},
            {'name': 'Muebles', 'description': 'Muebles de oficina', 'parent': 'Oficina'},
        ]
        
        cat_objects = {}
        for cat_data in categorias:
            parent = None
            if 'parent' in cat_data and cat_data['parent'] in cat_objects:
                parent = cat_objects[cat_data['parent']]
            
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'parent': parent,
                    'company': company,
                }
            )
            cat_objects[cat_data['name']] = category
            
            if created:
                self.stdout.write(f'    Categoría creada: {category.name}')
        
        # Bodegas
        bodegas = [
            {'name': 'Bodega Central', 'code': 'B001', 'location': 'Santiago Centro', 'is_active': True},
            {'name': 'Bodega Norte', 'code': 'B002', 'location': 'Antofagasta', 'is_active': True},
            {'name': 'Bodega Sur', 'code': 'B003', 'location': 'Concepción', 'is_active': False},
        ]
        
        for bodega_data in bodegas:
            warehouse, created = Warehouse.objects.get_or_create(
                code=bodega_data['code'],
                defaults={
                    'name': bodega_data['name'],
                    'location': bodega_data['location'],
                    'is_active': bodega_data['is_active'],
                    'company': company,
                }
            )
            if created:
                self.stdout.write(f'    Bodega creada: {warehouse.name}')
        
        # Proveedores
        proveedores = [
            {
                'name': 'Proveedor Tecnología Ltda.',
                'identification': '76.123.456-8',
                'phone': '+56 2 2123 4567',
                'email': 'ventas@tecnologia.cl',
                'address': 'Av. Providencia 1234',
            },
            {
                'name': 'Oficinas Globales S.A.',
                'identification': '77.234.567-9',
                'phone': '+56 2 2234 5678',
                'email': 'contacto@oficinaglobal.cl',
                'address': 'Av. Apoquindo 5678',
            },
        ]
        
        for prov_data in proveedores:
            supplier, created = Supplier.objects.get_or_create(
                identification=prov_data['identification'],
                defaults={
                    'name': prov_data['name'],
                    'phone': prov_data['phone'],
                    'email': prov_data['email'],
                    'address': prov_data['address'],
                    'company': company,
                }
            )
            if created:
                self.stdout.write(f'    Proveedor creado: {supplier.name}')
        
        # Productos
        productos = [
            {
                'name': 'Notebook Pro',
                'description': 'Notebook de alta gama',
                'category': cat_objects.get('Computación'),
                'cost_price': 650000,
                'sale_price': 799990,
                'sku': 'NB001',
            },
            {
                'name': 'Monitor 24"',
                'description': 'Monitor Full HD',
                'category': cat_objects.get('Computación'),
                'cost_price': 120000,
                'sale_price': 159990,
                'sku': 'MN001',
            },
            {
                'name': 'Parlantes Bluetooth',
                'description': 'Parlantes inalámbricos',
                'category': cat_objects.get('Audio'),
                'cost_price': 35000,
                'sale_price': 49990,
                'sku': 'AU001',
            },
            {
                'name': 'Silla Ejecutiva',
                'description': 'Silla ergonómica',
                'category': cat_objects.get('Muebles'),
                'cost_price': 85000,
                'sale_price': 129990,
                'sku': 'MB001',
            },
        ]
        
        for prod_data in productos:
            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'description': prod_data['description'],
                    'category': prod_data['category'],
                    'cost_price': prod_data['cost_price'],
                    'sale_price': prod_data['sale_price'],
                    'company': company,
                }
            )
            if created:
                self.stdout.write(f'    Producto creado: {product.name}')