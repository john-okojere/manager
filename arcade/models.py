from django.db import models
from decimal import Decimal
from django.db.models import Sum
from users.models import CustomUser


class Day(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_amount = models.DecimalField(max_digits=60, decimal_places=2)
    end_amount = models.DecimalField(max_digits=60, decimal_places=2, null=True, blank=True)
    start = models.BooleanField(default=True)
    end = models.BooleanField(default=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    no_of_sales = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def end_day(self):
        total_sales = self.sale_set.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        self.end_amount = total_sales
        self.end_time = models.DateTimeField(auto_now=True)
        self.save()


    def __str__(self):
        return f"Day by {self.staff} - started by {self.start_time}"


class Inventory(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    icon = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=60, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.staff} items"

    def is_in_stock(self):
        return True

class Sale(models.Model):
    cashier = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Who handled the sale
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=60, decimal_places=2)  # Total amount for the sale
    completed = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)  # When the sale occurred

    def __str__(self):
        return f"Sale #{self.id} by {self.cashier}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")  # Reference to the sale
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE)  # The product being sold
    quantity = models.PositiveIntegerField()  # Quantity sold
    price = models.DecimalField(max_digits=60, decimal_places=2)  # Price per unit
    total = models.DecimalField(max_digits=60, decimal_places=2)  # Total price for this line item (price * quantity)

    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)
        self.sale.total = self.sale.items.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        self.sale.save()

    def __str__(self):
        return f"{self.product.name} x{self.quantity} in Sale #{self.sale.id}"


class Receipt(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SaleDiscount(models.Model):
    cashier = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    proposed_discount = models.DecimalField(max_digits=60, decimal_places=2)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_approver')

class SaleItemDiscount(models.Model):
    cashier = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sale = models.ForeignKey(SaleItem, on_delete=models.CASCADE)
    proposed_discount = models.DecimalField(max_digits=60, decimal_places=2)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='saleitem_approver')

# models.py
from django.db import models

class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('card', 'Card'),
    ]
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='arcade_payment')
    cashier = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=60, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    paid_by = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.cashier} - {self.amount} ({self.payment_type})"

class Refund(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=60, decimal_places=2)
    refunded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund of {self.amount} by {self.refunded_by}"