from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Movement, Kardex
from apps.inventory.models import Inventory
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class MovementService:
    """Servicio para manejar movimientos de inventario con transacciones atómicas"""
    
    @staticmethod
    @transaction.atomic
    def create_entry(product, warehouse, quantity, unit_cost, created_by, reference='', notes=''):
        """
        Crear movimiento de entrada
        """
        # Bloquear inventario para actualización
        inventory, created = Inventory.objects.select_for_update().get_or_create(
            company=product.company,
            product=product,
            warehouse=warehouse,
            defaults={
                'quantity': 0,
                'min_stock': 0,
                'company': product.company
            }
        )
        
        # Validar cantidad
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
        # Crear movimiento
        movement = Movement.objects.create(
            company=product.company,
            movement_type='IN',
            product=product,
            quantity=quantity,
            warehouse_to=warehouse,
            unit_cost=unit_cost,
            total_cost=unit_cost * quantity,
            reference=reference,
            notes=notes,
            created_by=created_by,
            status='COMPLETED',
            processed_at=timezone.now()
        )
        
        # Actualizar inventario
        old_quantity = inventory.quantity
        inventory.quantity = F('quantity') + quantity
        inventory.last_movement = timezone.now()
        inventory.save()
        inventory.refresh_from_db()
        
        # Crear registro Kardex
        Kardex.objects.create(
            company=product.company,
            movement=movement,
            product=product,
            warehouse=warehouse,
            movement_type='IN',
            input_quantity=quantity,
            output_quantity=0,
            balance_quantity=inventory.quantity,
            input_value=unit_cost * quantity,
            output_value=0,
            balance_value=inventory.quantity * unit_cost,  # Costo promedio simplificado
            unit_cost=unit_cost,
            reference=reference,
            notes=notes,
            created_by=created_by
        )
        
        logger.info(f'Entrada creada: {movement.id} - {product.sku} - {quantity}')
        
        return movement
    
    @staticmethod
    @transaction.atomic
    def create_output(product, warehouse, quantity, unit_cost, created_by, reference='', notes=''):
        """
        Crear movimiento de salida
        """
        # Bloquear inventario para actualización
        try:
            inventory = Inventory.objects.select_for_update().get(
                company=product.company,
                product=product,
                warehouse=warehouse
            )
        except Inventory.DoesNotExist:
            raise ValueError(f"No hay inventario del producto {product.sku} en {warehouse.name}")
        
        # Validar stock suficiente
        if inventory.quantity < quantity:
            raise ValueError(f"Stock insuficiente. Disponible: {inventory.quantity}, Solicitado: {quantity}")
        
        # Crear movimiento
        movement = Movement.objects.create(
            company=product.company,
            movement_type='OUT',
            product=product,
            quantity=quantity,
            warehouse_from=warehouse,
            unit_cost=unit_cost,
            total_cost=unit_cost * quantity,
            reference=reference,
            notes=notes,
            created_by=created_by,
            status='COMPLETED',
            processed_at=timezone.now()
        )
        
        # Actualizar inventario
        old_quantity = inventory.quantity
        inventory.quantity = F('quantity') - quantity
        inventory.last_movement = timezone.now()
        inventory.save()
        inventory.refresh_from_db()
        
        # Crear registro Kardex
        Kardex.objects.create(
            company=product.company,
            movement=movement,
            product=product,
            warehouse=warehouse,
            movement_type='OUT',
            input_quantity=0,
            output_quantity=quantity,
            balance_quantity=inventory.quantity,
            input_value=0,
            output_value=unit_cost * quantity,
            balance_value=inventory.quantity * unit_cost,
            unit_cost=unit_cost,
            reference=reference,
            notes=notes,
            created_by=created_by
        )
        
        logger.info(f'Salida creada: {movement.id} - {product.sku} - {quantity}')
        
        return movement
    
    @staticmethod
    @transaction.atomic
    def create_transfer(product, warehouse_from, warehouse_to, quantity, created_by, reference='', notes=''):
        """
        Crear transferencia entre bodegas
        """
        # Validar que no sean la misma bodega
        if warehouse_from.id == warehouse_to.id:
            raise ValueError("La bodega origen y destino deben ser diferentes")
        
        # Bloquear inventario origen
        try:
            inventory_from = Inventory.objects.select_for_update().get(
                company=product.company,
                product=product,
                warehouse=warehouse_from
            )
        except Inventory.DoesNotExist:
            raise ValueError(f"No hay inventario del producto {product.sku} en {warehouse_from.name}")
        
        # Validar stock suficiente
        if inventory_from.quantity < quantity:
            raise ValueError(f"Stock insuficiente en origen. Disponible: {inventory_from.quantity}, Solicitado: {quantity}")
        
        # Bloquear o crear inventario destino
        inventory_to, created = Inventory.objects.select_for_update().get_or_create(
            company=product.company,
            product=product,
            warehouse=warehouse_to,
            defaults={
                'quantity': 0,
                'min_stock': 0,
                'company': product.company
            }
        )
        
        # Obtener costo unitario (del inventario origen)
        unit_cost = inventory_from.product.cost_price
        
        # Crear movimiento
        movement = Movement.objects.create(
            company=product.company,
            movement_type='TRANSFER',
            product=product,
            quantity=quantity,
            warehouse_from=warehouse_from,
            warehouse_to=warehouse_to,
            unit_cost=unit_cost,
            total_cost=unit_cost * quantity,
            reference=reference,
            notes=notes,
            created_by=created_by,
            status='COMPLETED',
            processed_at=timezone.now()
        )
        
        # Actualizar inventario origen
        old_from_quantity = inventory_from.quantity
        inventory_from.quantity = F('quantity') - quantity
        inventory_from.last_movement = timezone.now()
        inventory_from.save()
        inventory_from.refresh_from_db()
        
        # Actualizar inventario destino
        old_to_quantity = inventory_to.quantity
        inventory_to.quantity = F('quantity') + quantity
        inventory_to.last_movement = timezone.now()
        inventory_to.save()
        inventory_to.refresh_from_db()
        
        # Crear registro Kardex para salida de origen
        Kardex.objects.create(
            company=product.company,
            movement=movement,
            product=product,
            warehouse=warehouse_from,
            movement_type='TRANSFER',
            input_quantity=0,
            output_quantity=quantity,
            balance_quantity=inventory_from.quantity,
            input_value=0,
            output_value=unit_cost * quantity,
            balance_value=inventory_from.quantity * unit_cost,
            unit_cost=unit_cost,
            reference=reference,
            notes=f"Transferencia a {warehouse_to.name}: {notes}",
            created_by=created_by
        )
        
        # Crear registro Kardex para entrada en destino
        Kardex.objects.create(
            company=product.company,
            movement=movement,
            product=product,
            warehouse=warehouse_to,
            movement_type='TRANSFER',
            input_quantity=quantity,
            output_quantity=0,
            balance_quantity=inventory_to.quantity,
            input_value=unit_cost * quantity,
            output_value=0,
            balance_value=inventory_to.quantity * unit_cost,
            unit_cost=unit_cost,
            reference=reference,
            notes=f"Transferencia desde {warehouse_from.name}: {notes}",
            created_by=created_by
        )
        
        logger.info(f'Transferencia creada: {movement.id} - {product.sku} - {quantity} - {warehouse_from.code} -> {warehouse_to.code}')
        
        return movement
    
    @staticmethod
    @transaction.atomic
    def create_adjustment(product, warehouse, new_quantity, created_by, reason=''):
        """
        Crear ajuste de inventario
        """
        # Bloquear inventario
        try:
            inventory = Inventory.objects.select_for_update().get(
                company=product.company,
                product=product,
                warehouse=warehouse
            )
        except Inventory.DoesNotExist:
            # Si no existe, crear con cantidad 0
            inventory = Inventory.objects.create(
                company=product.company,
                product=product,
                warehouse=warehouse,
                quantity=0,
                min_stock=0
            )
        
        # Calcular diferencia
        old_quantity = inventory.quantity
        difference = new_quantity - old_quantity
        
        if difference == 0:
            raise ValueError("La cantidad nueva es igual a la actual, no se requiere ajuste")
        
        # Determinar tipo de movimiento
        movement_type = 'ADJUST'
        unit_cost = inventory.product.cost_price
        
        # Crear movimiento
        movement = Movement.objects.create(
            company=product.company,
            movement_type='ADJUST',
            product=product,
            quantity=abs(difference),
            warehouse_to=warehouse if difference > 0 else None,
            warehouse_from=warehouse if difference < 0 else None,
            unit_cost=unit_cost,
            total_cost=unit_cost * abs(difference),
            reference='Ajuste de inventario',
            notes=f"Ajuste: {reason}. Anterior: {old_quantity}, Nuevo: {new_quantity}",
            created_by=created_by,
            status='COMPLETED',
            processed_at=timezone.now()
        )
        
        # Actualizar inventario
        inventory.quantity = new_quantity
        inventory.last_movement = timezone.now()
        inventory.save()
        
        # Crear registro Kardex
        Kardex.objects.create(
            company=product.company,
            movement=movement,
            product=product,
            warehouse=warehouse,
            movement_type='ADJUST',
            input_quantity=abs(difference) if difference > 0 else 0,
            output_quantity=abs(difference) if difference < 0 else 0,
            balance_quantity=new_quantity,
            input_value=unit_cost * abs(difference) if difference > 0 else 0,
            output_value=unit_cost * abs(difference) if difference < 0 else 0,
            balance_value=new_quantity * unit_cost,
            unit_cost=unit_cost,
            reference='Ajuste',
            notes=f"Ajuste: {reason}. Diferencia: {difference:+d}",
            created_by=created_by
        )
        
        logger.info(f'Ajuste creado: {movement.id} - {product.sku} - {difference:+d}')
        
        return movement