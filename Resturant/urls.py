from django.urls import path
from . import views

urlpatterns = [
    path('waiter/', views.waiter, name='resturant_waiter'),
    path('cashier/', views.cashier, name='resturant_cashier'),
    path('start_day/', views.start_day, name='resturant_start_day'),
    path('end_day/', views.end_day, name='resturant_end_day'),
    path('dashboard/', views.dashboard, name='resturant_dashboard'),
    


    path('end_of_day_report/', views.end_of_day_report, name='resturant_end_of_day_report'),


    #Inventory
    path('inventory/', views.inventory_list, name='resturant_inventory_list'),
    path('inventory/category', views.create_category, name='resturant_inventory_categorry'),
    path('inventory/add/', views.add_inventory, name='resturant_add_inventory'),
    path('inventory/update/<int:pk>/', views.update_inventory, name='resturant_update_inventory'),
    path('inventory/delete/<int:pk>/', views.delete_inventory, name='resturant_delete_inventory'),

    #sales
    path('create-sale/', views.create_sale, name='resturant_create_sale'),
    path('increase-sale-item/', views.increase_sale_item, name='resturant_increase_sale_item'),
    path('decrease-sale-item/', views.decrease_sale_item, name='resturant_decrease_sale_item'),
    path('set-sale-type/', views.set_sale_type, name='resturant_link_sale_type'),
    path('add-sale-item/', views.add_sale_item, name='resturant_add_sale_item'),
    path('delete-sale-item/', views.delete_sale_item, name='resturant_add_sale_item'),
    path('complete-sale/', views.complete_sale, name='resturant_complete_sale'),
    path('Pay-for-sale/', views.pay_for_sale, name='resturant_pay_for_sale'),
    path('sale/<int:sale_id>/receipt/', views.sale_receipt, name='resturant_sale_receipt'),
    path('update-item-quantity/<int:item_id>/', views.update_item_quantity, name='resturant_update_item_quantity'),
    path('update-table-number/', views.set_sale_table, name='resturant_link_sale_type'),

    #discount
    path('apply-sale-item-discount/', views.apply_sale_item_discount, name='resturant_apply_sale_item_discount'),
    path('create-sale-discount/', views.apply_sale_discount, name='resturant_apply_sale_discount'),

    #history 
    path('sales-history/', views.sales_history, name='resturant_sales_history'),
    path('fetch-sales-data/', views.fetch_sales_data, name='resturant_fetch_sales_data'),

    # Manage Appproval
    path('manage-approvals/', views.manage_approvals, name='resturant_manage_approvals'),
    path('approve-day/<int:day_id>/', views.approve_day, name='resturant_approve_day'),
    path('approve-discount/<int:discount_id>/', views.approve_discount, name='resturant_approve_discount'),

    #Report
    path('audit-report/', views.audit_report, name='resturant_audit_report'),
    path('end-of-day-report/', views.end_of_day_report, name='resturant_end_of_day_report'),
    path('api/sales/', views.fetch_eod_sales_data, name='resturant_fetch_sales_data'),

    path('make-payment/', views.make_payment, name='resturant_make_payment'),
    path('send-cashier/', views.complete_sale, name='send_to_cashier'),
    path('process-payment/', views.process_payment, name='resturant_process_payment'),
    path('approve-order/', views.approve_order, name='resturant_approve_order'),
    path('get-order-details/<int:sale_id>/', views.get_order_details, name='get_order_details'),
    path('get-receipt-details/<int:sale_id>/', views.get_receipt_details, name='get_receipt_details'),
]
