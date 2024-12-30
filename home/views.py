from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from arcade.models import Sale as A_Sale, SaleItem as A_SaleItem, Inventory as A_Inventory, Payment as A_Payment, Day as A_Day,SaleDiscount as A_SaleDiscount
from Resturant.models import Sale as R_Sale, SaleItem as R_SaleItem, Inventory as R_Inventory, Payment as R_Payment, Day as R_Day, Category as  R_Category,SaleDiscount as R_SaleDiscount
from users.models import CustomUser
from django.utils.timezone import now

@login_required
def combined_dashboard(request):
    # Common data
    current_month = now().month
    current_year = now().year

    # Restaurant metrics
    restaurant_sales = R_Sale.objects.filter(completed=True, paid=True)
    restaurant_total_sales = restaurant_sales.aggregate(total=Sum('total'))['total'] or 0
    restaurant_items_sold = R_SaleItem.objects.filter(sale__paid=True).aggregate(total=Sum('quantity'))['total'] or 0
    restaurant_inventory_value = R_Inventory.objects.aggregate(total=Sum('price'))['total'] or 0
    restaurant_staff_count = CustomUser.objects.filter(section="restaurant").count()

    # Arcade metrics
    arcade_sales = A_Sale.objects.filter(completed=True, date__month=current_month, date__year=current_year)
    arcade_total_sales = arcade_sales.aggregate(total=Sum('total'))['total'] or 0
    arcade_total_discounts = A_SaleDiscount.objects.filter(approved=True, sale__date__month=current_month, sale__date__year=current_year).count()
    arcade_pending_days = A_Day.objects.filter(end=True, end_time=None, date__month=current_month, date__year=current_year).count()
    arcade_pending_discounts = A_SaleDiscount.objects.filter(approved=False, sale__date__month=current_month, sale__date__year=current_year).count()

    # Shared metrics
    total_categories =  R_Category.objects.count()
    days_count = A_Day.objects.count() + R_Day.objects.count()

    # Top-performing waiters (Restaurant)
    waiter_sales = (
        restaurant_sales.values("waiter__username")
        .annotate(total_sales=Sum("total"), sales_count=Count("id"))
        .order_by("-total_sales")[:5]
    )

    # Top-selling products (Restaurant)
    top_products = (
        R_SaleItem.objects.filter(sale__paid=True)
        .values("product__name")
        .annotate(quantity_sold=Sum("quantity"))
        .order_by("-quantity_sold")[:5]
    )

    # Payments Breakdown (Restaurant)
    payment_breakdown = (
        R_Payment.objects.filter(sale__paid=True)
        .values("payment_type")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    # Sales grouped by month (Arcade)
    sales_by_month = (
        A_Sale.objects.filter(completed=True)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total'))
        .order_by('month')
    )

    monthly_sales_labels = [entry['month'].strftime('%Y-%m') for entry in sales_by_month]
    monthly_sales_values = [float(entry['total']) for entry in sales_by_month]

    # Prepare context for rendering
    context = {
        # Restaurant-specific data
        "restaurant_total_sales": restaurant_total_sales,
        "restaurant_items_sold": restaurant_items_sold,
        "restaurant_inventory_value": restaurant_inventory_value,
        "restaurant_staff_count": restaurant_staff_count,
        "waiter_sales": waiter_sales,
        "top_products": top_products,
        "payment_breakdown": payment_breakdown,

        # Arcade-specific data
        "arcade_total_sales": arcade_total_sales,
        "arcade_total_discounts": arcade_total_discounts,
        "arcade_pending_days": arcade_pending_days,
        "arcade_pending_discounts": arcade_pending_discounts,

        # Shared data
        "total_categories": total_categories,
        "days_count": days_count,
        "monthly_sales_labels": monthly_sales_labels,
        "monthly_sales_values": monthly_sales_values,
    }

    return render(request, "dashboard/combined_dashboard.html", context)
