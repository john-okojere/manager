from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Inventory, Payment, Sale, SaleItem, Receipt, SaleDiscount, SaleItemDiscount, Day


# Define resources for each model (optional but provides more control over export/import)
class InventoryResource(resources.ModelResource):
    class Meta:
        model = Inventory
        fields = ('id', 'name', 'price', 'staff', 'date', 'is_in_stock')
        export_order = ('id', 'name', 'price', 'staff', 'date', 'is_in_stock')

class SaleResource(resources.ModelResource):
    class Meta:
        model = Sale
        fields = ('id', 'cashier', 'total', 'date', )
        export_order = ('id', 'cashier', 'total', 'date')

class SaleItemResource(resources.ModelResource):
    class Meta:
        model = SaleItem
        fields = ('id', 'sale', 'product', 'quantity', 'price', 'total')
        export_order = ('id', 'sale', 'product', 'quantity', 'price', 'total')

class ReceiptResource(resources.ModelResource):
    class Meta:
        model = Receipt
        fields = ('receipt_number', 'sale', 'created_at')
        export_order = ('receipt_number', 'sale', 'created_at')

class SaleDiscountResource(resources.ModelResource):
    class Meta:
        model = SaleDiscount
        fields = ('sale', 'cashier', 'proposed_discount', 'approved', 'approved_by')
        export_order = ('sale', 'cashier', 'proposed_discount', 'approved', 'approved_by')

class SaleItemDiscountResource(resources.ModelResource):
    class Meta:
        model = SaleItemDiscount
        fields = ('sale', 'cashier', 'proposed_discount', 'approved', 'approved_by')
        export_order = ('sale', 'cashier', 'proposed_discount', 'approved', 'approved_by')

class DayResource(resources.ModelResource):
    class Meta:
        model = Day
        fields = ('staff', 'start_amount', 'end_amount', 'start_time', 'end_time', 'no_of_sales', 'date')
        export_order = ('staff', 'start_amount', 'end_amount', 'start_time', 'end_time', 'no_of_sales', 'date')

class PaymentResource(resources.ModelResource):
    class Meta:
        model = Payment
        fields = ('cashier', 'amount', 'payment_type', 'sale', 'paid_by', 'date')
        export_order = ('cashier', 'amount', 'payment_type', 'sale', 'paid_by', 'date')


# Registering models with the admin and attaching the resources

@admin.register(Inventory)
class InventoryAdmin(ImportExportModelAdmin):
    resource_class = InventoryResource
    list_display = ('name', 'price', 'staff', 'date' ,'is_in_stock')
    list_filter = ('date', 'staff')
    search_fields = ('name', 'description', 'staff__username')
    ordering = ('-date',)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    fields = ('product', 'quantity', 'price', 'total')
    readonly_fields = ('total',)


@admin.register(Sale)
class SaleAdmin(ImportExportModelAdmin):
    resource_class = SaleResource
    list_display = ('id', 'cashier', 'total', 'date', 'completed', 'paid')
    list_filter = ('date', 'cashier__username')
    search_fields = ('cashier__username', 'id')
    ordering = ('-date',)
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(ImportExportModelAdmin):
    resource_class = SaleItemResource
    list_display = ('id', 'sale', 'product', 'quantity', 'price', 'total')
    list_filter = ('sale__date', 'product__name')
    search_fields = ('sale__id', 'product__name')
    ordering = ('-sale__date',)


@admin.register(Receipt)
class ReceiptAdmin(ImportExportModelAdmin):
    resource_class = ReceiptResource
    list_display = ('receipt_number', 'sale', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('receipt_number', 'sale__id')
    ordering = ('-created_at',)


@admin.register(SaleDiscount)
class SaleDiscountAdmin(ImportExportModelAdmin):
    resource_class = SaleDiscountResource
    list_display = ('sale', 'cashier', 'proposed_discount', 'approved', 'approved_by')
    list_filter = ('approved', 'cashier__username', 'sale__date')
    search_fields = ('sale__id', 'cashier__username')
    ordering = ('-sale__date',)


@admin.register(SaleItemDiscount)
class SaleItemDiscountAdmin(ImportExportModelAdmin):
    resource_class = SaleItemDiscountResource
    list_display = ('sale', 'cashier', 'proposed_discount', 'approved', 'approved_by')
    list_filter = ('approved', 'cashier__username', 'sale__sale__date')
    search_fields = ('sale__sale__id', 'cashier__username')
    ordering = ('-sale__sale__date',)


@admin.register(Day)
class DayAdmin(ImportExportModelAdmin):
    resource_class = DayResource
    list_display = ('staff', 'start_amount', 'end_amount', 'start_time', 'end_time', 'no_of_sales', 'date')
    list_filter = ('staff', 'date')
    search_fields = ('staff__username', 'start_amount', 'end_amount')


@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    resource_class = PaymentResource
    list_display = ('cashier', 'amount', 'payment_type', 'sale', 'paid_by', 'date')
    list_filter = ('cashier', 'date')
    search_fields = ('cashier__username', 'amount')
