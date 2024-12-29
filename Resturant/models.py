from django.db import models
from decimal import Decimal
from django.db.models import Sum
from users.models import CustomUser


class Day(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resturant_days')
    waiter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='waiter_days')
    start_amount = models.DecimalField(max_digits=15, decimal_places=2)
    end_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
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

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField( max_length=50, unique=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resturant_inventories')
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='resturant_category')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.category} items"

    def is_in_stock(self):
        return self.category > 0

class Sale(models.Model):
    type = models.CharField(max_length=100, default='Dine In', choices=[('Take Away', 'Take Away'), ('Dine In', 'Dine In')])
    Table_no = models.CharField(max_length=100)
    cashier = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE, related_name="resturant_sale")  # Who handled the sale
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=15, decimal_places=2)  # Total amount for the sale
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)  # When the sale occurred
    waiter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="resturant_waiter")
    approved = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Sale #{self.id} by {self.cashier}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="resturant_items")  # Reference to the sale
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="resturant_product")  # The product being sold
    quantity = models.PositiveIntegerField()  # Quantity sold
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total price for this line item (price * quantity)

    def __str__(self):
        return f"{self.product.name} x{self.quantity} in Sale #{self.sale.id}"


class Receipt(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SaleDiscount(models.Model):
    cashier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resturant_discounts')
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='discounts')
    proposed_discount = models.DecimalField(max_digits=10, decimal_places=2)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='resturant_approver')

class SaleItemDiscount(models.Model):
    cashier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resturant_saleitem_discounts')
    sale = models.ForeignKey(SaleItem, on_delete=models.CASCADE, related_name='resturant_discounts')
    proposed_discount = models.DecimalField(max_digits=10, decimal_places=2)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='resturant_saleitem_approver')

# models.py
from django.db import models

class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('card', 'Card'),
    ]
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='resturant_payments')
    cashier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resturant_cashier_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    paid_by = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.cashier} - {self.amount} ({self.payment_type})"
