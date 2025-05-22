# signals.py (create this file in your app directory)
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import *

@receiver(post_save, sender=OverTheCounterSaleItem)
def reduce_stock_on_sale(sender, instance, created, **kwargs):
    """
    Automatically reduce medicine stock when an OTC sale item is created or updated.
    Only reduces stock for completed sales.
    """
    # Only process if the sale is completed
    if instance.sale.payment_status == 'completed':
        if created:
            # New item created - reduce stock by the quantity
            with transaction.atomic():
                medicine = Medicine.objects.select_for_update().get(pk=instance.medicine.pk)
                if medicine.quantity_in_stock >= instance.quantity:
                    medicine.quantity_in_stock -= instance.quantity
                    medicine.save(update_fields=['quantity_in_stock'])
                else:
                    # Handle insufficient stock - you might want to raise an exception
                    # or handle this case based on your business logic
                    pass
        else:
            # Item updated - we need to check if quantity changed
            # This requires storing the old quantity, which we'll handle in pre_save
            pass

@receiver(pre_save, sender=OverTheCounterSaleItem)
def store_old_quantity(sender, instance, **kwargs):
    """
    Store the old quantity before saving to handle quantity updates.
    """
    if instance.pk:  # Only for existing items
        try:
            old_instance = OverTheCounterSaleItem.objects.get(pk=instance.pk)
            instance._old_quantity = old_instance.quantity
        except OverTheCounterSaleItem.DoesNotExist:
            instance._old_quantity = 0
    else:
        instance._old_quantity = 0

@receiver(post_save, sender=OverTheCounterSaleItem)
def adjust_stock_on_update(sender, instance, created, **kwargs):
    """
    Adjust stock when quantity is updated on an existing item.
    """
    if not created and instance.sale.payment_status == 'completed':
        if hasattr(instance, '_old_quantity'):
            old_quantity = instance._old_quantity
            new_quantity = instance.quantity
            
            if old_quantity != new_quantity:
                quantity_difference = new_quantity - old_quantity
                
                with transaction.atomic():
                    medicine = Medicine.objects.select_for_update().get(pk=instance.medicine.pk)
                    # If quantity increased, reduce more stock
                    # If quantity decreased, add stock back
                    medicine.quantity_in_stock -= quantity_difference
                    medicine.save(update_fields=['quantity_in_stock'])

@receiver(post_delete, sender=OverTheCounterSaleItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    """
    Restore stock when an OTC sale item is deleted.
    """
    if instance.sale.payment_status == 'completed':
        with transaction.atomic():
            medicine = Medicine.objects.select_for_update().get(pk=instance.medicine.pk)
            medicine.quantity_in_stock += instance.quantity
            medicine.save(update_fields=['quantity_in_stock'])

# Handle payment status changes
@receiver(pre_save, sender=OverTheCounterSale)
def store_old_payment_status(sender, instance, **kwargs):
    """
    Store the old payment status before saving.
    """
    if instance.pk:
        try:
            old_instance = OverTheCounterSale.objects.get(pk=instance.pk)
            instance._old_payment_status = old_instance.payment_status
        except OverTheCounterSale.DoesNotExist:
            instance._old_payment_status = None
    else:
        instance._old_payment_status = None

@receiver(post_save, sender=OverTheCounterSale)
def handle_payment_status_change(sender, instance, created, **kwargs):
    """
    Handle stock adjustments when payment status changes.
    """
    if not created and hasattr(instance, '_old_payment_status'):
        old_status = instance._old_payment_status
        new_status = instance.payment_status
        
        # If payment status changed from pending/failed to completed
        if old_status in ['pending', 'failed'] and new_status == 'completed':
            # Reduce stock for all items in this sale
            for item in instance.items.all():
                with transaction.atomic():
                    medicine = Medicine.objects.select_for_update().get(pk=item.medicine.pk)
                    if medicine.quantity_in_stock >= item.quantity:
                        medicine.quantity_in_stock -= item.quantity
                        medicine.save(update_fields=['quantity_in_stock'])
        
        # If payment status changed from completed to pending/failed
        elif old_status == 'completed' and new_status in ['pending', 'failed']:
            # Restore stock for all items in this sale
            for item in instance.items.all():
                with transaction.atomic():
                    medicine = Medicine.objects.select_for_update().get(pk=item.medicine.pk)
                    medicine.quantity_in_stock += item.quantity
                    medicine.save(update_fields=['quantity_in_stock'])