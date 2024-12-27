from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='arcade_dashboard'),
    path('cashier/', views.cashier, name='arcade_cashier'),
    path('start_day/', views.start_day, name='start_day'),
    path('end_day/', views.end_day, name='end_day'),
    path('end_of_day_report/', views.end_of_day_report, name='end_of_day_report'),\
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/doc/', views.export_doc, name='export_doc'),

    # Sales
    path('create-sale/', views.create_sale, name='create_sale'),
    path('add-sale-item/', views.add_sale_item, name='add_sale_item'),
    path('complete-sale/', views.complete_sale, name='complete_sale'),
    path('Pay-for-sale/', views.pay_for_sale, name='pay_for_sale'),
    path('sale/receipt/<int:sale_id>/', views.sale_receipt, name='sale_receipt'),

    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    path('inventory/update/<int:pk>/', views.update_inventory, name='update_inventory'),
    path('inventory/delete/<int:pk>/', views.delete_inventory, name='delete_inventory'),

    # Discount
    path('apply-sale-item-discount/', views.apply_sale_item_discount, name='apply_sale_item_discount'),
    path('create-sale-discount/', views.apply_sale_discount, name='apply_sale_discount'),

    # History
    path('sales-history/', views.sales_history, name='sales_history'),
    path('fetch-sales-data/', views.fetch_sales_data, name='fetch_sales_data'),

    # Report
    path('audit-report/', views.audit_report, name='audit_report'),
    path('end-of-day-report/', views.end_of_day_report, name='end_of_day_report'),
    path('api/sales/', views.fetch_eod_sales_data, name='fetch_sales_data'),

    # Payments
    path('make-payment/', views.make_payment, name='make_payment'),

    # Approvals
    path("manage-approvals/", views.manage_approvals, name="manage_approvals"),
    path("approve-day/<int:day_id>/", views.approve_day, name="approve_day"),
    path("approve-discount/<int:discount_id>/", views.approve_discount, name="approve_discount"),

    # Newly Added URLs
    # Sales Reports
    path('daily-sales-report/', views.daily_sales_report, name='daily_sales_report'),
    path('weekly-sales-report/', views.weekly_sales_report, name='weekly_sales_report'),
    path('monthly-sales-report/', views.monthly_sales_report, name='monthly_sales_report'),
    path('sales-by-staff/', views.sales_by_staff_report, name='sales_by_staff_report'),
    path('sales-by-product/', views.sales_by_product_report, name='sales_by_product_report'),

    # Inventory Reports
    path('low-stock-report/', views.low_stock_report, name='low_stock_report'),
    path('inventory-turnover-report/', views.inventory_turnover_report, name='inventory_turnover_report'),

    # Financial Reports
    path('daily-cashflow-report/', views.daily_cashflow_report, name='daily_cashflow_report'),
    path('sales-tax-report/', views.sales_tax_report, name='sales_tax_report'),

    # Discounts and Refunds
    path('discounts-report/', views.discounts_report, name='discounts_report'),
    path('refunds-report/', views.refunds_report, name='refunds_report'),

    # API Endpoints
    path('api/sales-growth/', views.api_sales_growth, name='api_sales_growth'),
    path('api/sales-performance/', views.api_sales_performance, name='api_sales_performance'),
    path('api/sales-by-product/', views.api_sales_by_product, name='api_sales_by_product'),
    path('api/payment-summary/', views.api_payment_summary, name='api_payment_summary'),
]
