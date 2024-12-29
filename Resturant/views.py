from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils.text import slugify
from .models import Inventory, Category, Receipt
from .forms import InventoryForm, StartDayForm, EndDayForm, CategoryForm
from users.models import CustomUser
from .models import Day

from .forms import StartDayForm

@login_required
def start_day(request):
    # Check if there is any day that has not ended
    unfinished_day = Day.objects.filter(staff=request.user, end=False).first()
    if unfinished_day:
            return redirect('resturant_cashier')

    if request.method == 'POST':
        form = StartDayForm(request.POST)
        if form.is_valid():
            day = form.save(commit=False)
            day.staff = request.user
            day.start_time = datetime.now().time()
            day.save()
            return redirect('resturant_cashier')
    else:
        form = StartDayForm()

    return render(request, 'resturant/start_day.html', {'form': form})


@login_required
def waiter(request):
    # Check if there is any day that has not ended
    unfinished_day = Day.objects.filter(waiter=request.user, end=False).first()
    print(unfinished_day,'jkn')

    if not unfinished_day:
        return JsonResponse({'status':''})  # Redirect to the start day view if no day has started

    items = Inventory.objects.all()
    category = Category.objects.all()
    context = {
        'items': items,
        'category': category,
    }
    return render(request, 'resturant/pos.html', context)

@login_required
def cashier(request):
    # Check if there is any day that has not ended
    unfinished_day = Day.objects.filter(staff=request.user, end=False).first()
    if not unfinished_day:
        return redirect('resturant_start_day')  # Redirect to the start day view if no day has started
    pending_orders = Sale.objects.filter(day = unfinished_day, completed=True, paid=False).order_by('-date')
    context = {
     'orders': pending_orders
    }
    return render(request, 'resturant/cashier.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Sale, Payment
from decimal import Decimal

from django.views.decorators.http import require_POST
# View to process payment
@require_POST
def process_payment(request):
    try:
        sale_id = request.POST.get('sale_id')
        amount = request.POST.get('amount')
        payment_type = request.POST.get('payment_type')
        paid_by = request.POST.get('paid_by')

        # Ensure all required fields are present
        if not (sale_id and amount and payment_type and paid_by):
            return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

        sale = get_object_or_404(Sale, id=sale_id)

        # Create the Payment record
        Payment.objects.create(
            sale=sale,
            cashier=request.user,
            amount=amount,
            payment_type=payment_type,
            paid_by=paid_by
        )

        # Mark the sale as paid
        sale.paid = True
        sale.save()

        return JsonResponse({'success': True, 'message': 'Payment processed successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
def approve_order(request):
    try:
        sale_id = request.POST.get('Asale_id')

        # Ensure all required fields are present
        if not (sale_id):
            return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

        sale = get_object_or_404(Sale, id=sale_id)
        sale.cashier = request.user
        sale.approved = True
        # Mark the sale as paid
        sale.save()

        return JsonResponse({'success': True, 'message': 'Payment processed successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def add_inventory(request):
    # Check if the user has an associated staff profile
    try:
        user = request.user
    except AttributeError:
        messages.error(request, "You don't have permission to upload inventory.")
        return redirect('resturant_inventory_list')

    if request.method == "POST":
        form = InventoryForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form but don't commit to the database yet
            inventory_item = form.save(commit=False)
            # Associate the logged-in staff with the inventory
            inventory_item.staff = user
            print(inventory_item)
            inventory_item.save()
            messages.success(request, "Inventory item added successfully!")
            return redirect('resturant_inventory_list')
    else:
        form = InventoryForm()

    return render(request, 'resturant/inventory/add.html', {'form': form, 'name':'Menu'})

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.instance.slug = '_'.join(form.cleaned_data['name'].split())
            form.save()
            return redirect('resturant_inventory_categorry')
    else:
        form = CategoryForm()
    return render(request, 'resturant/inventory/add.html', {'form': form, 'name':'Category'})

def inventory_list(request):
    items = Inventory.objects.all().order_by('-date')
    return render(request, 'resturant/inventory/list.html', {'items': items})


# Update Inventory View
def update_inventory(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            # Respond to AJAX request with success message
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Inventory item updated successfully!"})
            messages.success(request, "Inventory item updated successfully!")
            return redirect('resturant_inventory_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = InventoryForm(instance=item)
    return render(request, 'resturant/inventory/update_inventory.html', {'form': form})


# Delete Inventory View
def delete_inventory(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        item.delete()
        # Respond to AJAX request with success message
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": True, "message": "Inventory item deleted successfully!"})
        messages.success(request, "Inventory item deleted successfully!")
        return redirect('resturant_inventory_list')
    return render(request, 'resturant/inventory/delete_inventory.html', {'item': item})


from django.http import JsonResponse
from .models import Sale, SaleItem, Inventory

def create_sale(request):
    if request.user.role == "Cashier":
        unfinished_day = Day.objects.filter(staff=request.user, end=False).last()
    else:
        unfinished_day = Day.objects.filter(end=False).last()
    if request.method == 'POST':
        cashier_id = request.user.id
        total_amount = request.POST.get('total_amount')
        waiter = CustomUser.objects.get(id=cashier_id)
        sale = Sale.objects.create(waiter=waiter, cashier=unfinished_day.staff, total=total_amount, day=unfinished_day)
        return JsonResponse({'status': 'success', 'sale_id': sale.id})

from django.db.models import F
@login_required
def update_item_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_quantity = int(request.POST.get('new_quantity'))

        try:
            item = Inventory.objects.get(id=item_id)
            item.quantity = new_quantity
            item.save()
            return JsonResponse({'status': 'success', 'message': 'Item quantity updated successfully!'})
        except Inventory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def add_sale_item(request):
    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
        product_id = request.POST.get('product_id')
        print(product_id)
        quantity = int(request.POST.get('quantity'))
        price = float(request.POST.get('price'))
        total = quantity * price

        # Fetch the sale and product
        sale = Sale.objects.get(id=sale_id)
        product = Inventory.objects.get(id=product_id)

        # Create the sale item
        sale_item = SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            price=price,
            total=total
        )

        # Update the sale total
        updated_total = SaleItem.objects.filter(sale=sale).aggregate(total_sum=Sum('total'))['total_sum'] or 0
        sale.total = updated_total
        sale.save(update_fields=['total'])

        # Refresh the sale object to get the updated total
        sale.refresh_from_db()

        return JsonResponse({
            'status': 'success',
            'sale_item_id': sale_item.id,
            'updated_sale_total': float(sale.total)
        })
    

def delete_sale_item(request):
    if request.method == 'POST':
        sale_item_id = request.POST.get('sale_item_id')
        
        try:
            sale_item = SaleItem.objects.get(id=sale_item_id)
            sale_item.delete()
            
            # Update the sale total after deleting the item
            sale = sale_item.sale
            updated_total = SaleItem.objects.filter(sale=sale).aggregate(total_sum=Sum('total'))['total_sum'] or 0
            sale.total = updated_total
            sale.save(update_fields=['total'])
            
            return JsonResponse({'status': 'success', 'message': 'Sale item deleted successfully!'})
        except SaleItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sale item not found.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def increase_sale_item(request):
    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
        product_id = request.POST.get('product_id')

        try:
            sale = Sale.objects.get(id=sale_id)
            sale_item = SaleItem.objects.get(sale=sale, product_id=product_id)
            sale_item.quantity += 1
            sale_item.total = sale_item.quantity * sale_item.price
            sale_item.save()

            # Update the sale total
            updated_total = SaleItem.objects.filter(sale=sale).aggregate(total_sum=Sum('total'))['total_sum'] or 0
            sale.total = updated_total
            sale.save(update_fields=['total'])

            return JsonResponse({'status': 'success', 'message': 'Cart item increased successfully!', 'updated_sale_total': float(sale.total)})
        except (Sale.DoesNotExist, SaleItem.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Sale or Sale item not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def decrease_sale_item(request):
    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
        product_id = request.POST.get('product_id')

        try:
            sale = Sale.objects.get(id=sale_id)
            sale_item = SaleItem.objects.get(sale=sale, product_id=product_id)
            if sale_item.quantity > 1:
                sale_item.quantity -= 1
                sale_item.total = sale_item.quantity * sale_item.price
                sale_item.save()

                # Update the sale total
                updated_total = SaleItem.objects.filter(sale=sale).aggregate(total_sum=Sum('total'))['total_sum'] or 0
                sale.total = updated_total
                sale.save(update_fields=['total'])

                return JsonResponse({'status': 'success', 'message': 'Cart item decreased successfully!', 'updated_sale_total': float(sale.total)})
            else:
                return JsonResponse({'status': 'error', 'message': 'Quantity cannot be less than 1.'})
        except (Sale.DoesNotExist, SaleItem.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Sale or Sale item not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def set_sale_type(request):
    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
        sale_type = request.POST.get('sale_type')  # 'dine' or 'takeaway'
        print(sale_type)

        try:
            sale = Sale.objects.get(id=sale_id)
            sale.type = sale_type
            sale.save()
            return JsonResponse({'status': 'success', 'message': 'Sale type updated successfully!'})
        except Sale.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sale not found.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def set_sale_table(request):
    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
        sale_table = request.POST.get('table_number')  # 'dine' or 'takeaway'

        try:
            sale = Sale.objects.get(id=sale_id)
            sale.Table_no = sale_table
            sale.save()
            return JsonResponse({'status': 'success', 'message': 'Sale type updated successfully!'})
        except Sale.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sale not found.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})



def complete_sale(request):
    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
        print(sale_id)
        
        try:
            sale = Sale.objects.get(id=sale_id)
            sale.completed = True
            sale.save()
            
            return redirect('/restaurant/waiter/')
        except Sale.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sale not found.'})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Sale, SaleItem, SaleDiscount, SaleItemDiscount, CustomUser

def apply_sale_discount(request):
    if request.method == 'POST':
        cashier = request.user
        sale_id = request.POST.get('sale_id')
        proposed_discount = request.POST.get('proposed_discount')

        sale = get_object_or_404(Sale, id=sale_id)

        # Create SaleDiscount
        SaleDiscount.objects.create(
            cashier=cashier,
            sale=sale,
            proposed_discount=proposed_discount,
        )

        return JsonResponse({'success': True, 'message': 'Sale discount created successfully!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def apply_sale_item_discount(request):
    if request.method == 'POST':
        cashier = request.user
        sale_item_id = request.POST.get('sale_item_id')
        proposed_discount = request.POST.get('proposed_discount')

        sale_item = get_object_or_404(SaleItem, id=sale_item_id)

        # Create SaleItemDiscount
        SaleItemDiscount.objects.create(
            cashier=cashier,
            sale=sale_item,
            proposed_discount=proposed_discount,
        )

        return JsonResponse({'success': True, 'message': 'Sale item discount created successfully!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncWeek
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Sum
from django.db.models.functions import TruncDay

def sales_history(request):
    if request.user.role == "Cashier":
        day = Day.objects.filter(staff=request.user, end=False).first()
        if not day:
            return redirect('start_day')

        sales = Sale.objects.filter(paid=True, cashier=request.user, day=day).only('id', 'cashier__username', 'completed', 'total', 'paid', 'date')
    elif request.user.role == "Manager" or request.user.level >= 3:
        sales = Sale.objects.filter(paid=True).only('id', 'cashier__username', 'completed', 'total', 'paid', 'date')
    else:
        sales = Sale.objects.none()

    paginator = Paginator(sales, 50)  # Show 50 sales per page
    page_number = request.GET.get('page')
    page_sales = paginator.get_page(page_number)

    sales_data = [
        {
            'id': sale.id,
            'cashier': sale.cashier.username,
            'completed': sale.completed,
            'total': float(sale.total),
            'paid': sale.paid,
            'date': sale.date.isoformat(),
        }
        for sale in page_sales
    ]

    cache_key = f'graph_data_{request.user.id}'
    graph_data = cache.get(cache_key)

    if not graph_data:
        graph_data = (
            sales
            .annotate(dates=TruncDay('date'))
            .values('dates')
            .annotate(total=Sum('total'))
            .order_by('dates')
        )
        cache.set(cache_key, list(graph_data), 3600)  # Cache for 1 hour

    graph_labels = [entry['dates'].strftime('%Y-%m-%d') for entry in graph_data]
    graph_values = [float(entry['total']) for entry in graph_data]

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'sales': sales_data, 'graph_labels': graph_labels, 'graph_values': graph_values})

    return render(request, 'resturant/sales_history.html', {
        'sales': sales_data,
        'graph_labels': graph_labels,
        'graph_values': graph_values,
        'page_sales': page_sales,
    })


from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncDay
from .models import Sale

def fetch_sales_data(request):
    if request.method == 'GET':
        # Aggregate sales data
        graph_data = (
            Sale.objects.filter(completed=True)
            .annotate(day=TruncDay('date'))
            .values('day')
            .annotate(total=Sum('total'))
            .order_by('day')
        )

        graph_labels = [entry['day'].strftime('%Y-%m-%d') for entry in graph_data]
        graph_values = [float(entry['total']) for entry in graph_data]

        return JsonResponse({
            'graph_labels': graph_labels,
            'graph_values': graph_values,
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


from django.shortcuts import render
from django.http import JsonResponse
from .models import Sale  # Replace with your actual model for transactions
from django.db.models import Sum, Count
import datetime



# Generate a custom report (optional extension for downloadable formats like PDF/Excel)
def custom_report(request):
    # Handle filters and dynamic reports (e.g., by cashier, status, date, etc.)
    # Return processed data for export
    return JsonResponse({'status': 'Custom report generation in progress...'})


from django.shortcuts import render
from django.http import JsonResponse
from .models import Sale  # Assuming you have a Sale model for storing sales data
from datetime import datetime

def end_of_day_report(request):
    day = Day.objects.filter(staff=request.user, end=False).first()

    if not day:
        return redirect('resturant_start_day')  # Redirect to the start day view if no day has started

    # Sales Summary
    sales = Sale.objects.filter(day=day)
    total_sales = sales.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    total_completed_sales = sales.filter(completed=True).count()
    total_pending_sales = sales.filter(completed=False).count()

    # Payment Breakdown
    payments = Payment.objects.filter(sale__day=day)
    total_cash_payments = payments.filter(payment_type='cash').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_card_payments = payments.filter(payment_type='card').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_transfer_payments = payments.filter(payment_type='transfer').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_cash_received = total_cash_payments
    total_change_given = Decimal('0.00')  # Replace with logic if tracked
    expected_cash_at_hand = day.start_amount + total_cash_received - total_change_given

    # Profit Summary
    items = SaleItem.objects.filter(sale__day=day)
    total_revenue = items.aggregate(total=Sum('total'))['total'] or Decimal('0.00')

    # Inventory Impact
    inventory_impact = (
        items.values('product__name', 'product__category__name')
        .annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total'),
        )
        .order_by('product__category__name')
    )

    # Discounts
    total_sale_discounts = SaleDiscount.objects.filter(sale__day=day).aggregate(total=Sum('proposed_discount'))['total'] or Decimal('0.00')
    total_approved_discounts = SaleDiscount.objects.filter(sale__day=day, approved=True).aggregate(total=Sum('proposed_discount'))['total'] or Decimal('0.00')

    context = {
        'day': day,
        'total_sales': total_sales,
        'total_completed_sales': total_completed_sales,
        'total_pending_sales': total_pending_sales,
        'total_cash_payments': total_cash_payments,
        'total_card_payments': total_card_payments,
        'total_transfer_payments': total_transfer_payments,
        'total_cash_received': total_cash_received,
        'total_change_given': total_change_given,
        'expected_cash_at_hand': expected_cash_at_hand,
        'total_revenue': total_revenue,
        'inventory_impact': inventory_impact,
        'total_sale_discounts': total_sale_discounts,
        'total_approved_discounts': total_approved_discounts,
    }


    return render(request, 'resturant/end-of-day.html', context)

import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Payment

@csrf_exempt
def make_payment(request):
    if request.method == "POST":
        data = request.POST
        sale_id = data.get("sale_id")
        amount = data.get("amount")
        payment_method = data.get("payment_method")
        paid_by = data.get("paid_by")

        # For card payments, expect additional data
        if payment_method == "card":
            payment_id = uuid.uuid4().hex
            # Call Paystack API here to verify payment
            # Add your Paystack verification logic (e.g., check transaction ID)
        else:
            payment_id = None
        sale = Sale.objects.get(id = sale_id)
        # Save payment record
        payment = Payment.objects.create(
            sale = sale,
            cashier = request.user,
            amount=amount,
            payment_type=payment_method,
            paid_by=paid_by,
            payment_id=payment_id,
        )
        payment.save()

        return JsonResponse({"status": "success", "payment_id": payment.id})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def pay_for_sale(request):
    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
                
        try:
            sale = Sale.objects.get(id=sale_id)
            sale.paid = True
            sale.save()
            
            return JsonResponse({'status': 'success', 'message': 'Sale marked as completed.'})
        except Sale.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sale not found.'})

def sale_receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    sale_items = sale.items.all()

    receipt_data = {
        "id": sale.id,
        "cashier": sale.cashier.username,  # Adjust as necessary
        "date": sale.date.strftime("%Y-%m-%d %H:%M:%S"),
        "total": sale.total,
        "items": [
            {
                "product": item.product.name,
                "quantity": item.quantity,
                "price": item.price,
                "total": item.total
            }
            for item in sale_items
        ]
    }
    print(receipt_data)
    return JsonResponse(receipt_data)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from .models import Sale
from datetime import datetime

# API to fetch sales data
@require_GET
def fetch_eod_sales_data(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    # Check if the cashier has ended the day
    if not request.user.CustomUser.has_ended_day:
        return JsonResponse({"error": "End of day process not completed."}, status=403)

    # Filter sales for today
    today = datetime.now().date()
    sales = Sale.objects.filter(date__date=today)
    
    data = [
        {
            "id": sale.id,
            "cashier": str(sale.cashier),
            "total": float(sale.total),
            "completed": "Yes" if sale.completed else "No",
            "paid": float(sale.paid),
            "date": sale.date.strftime("%Y-%m-%d %H:%M:%S"),
            "payment_method": sale.payment_method if hasattr(sale, 'payment_method') else "N/A",
        }
        for sale in sales
    ]
    return JsonResponse(data, safe=False)

# API to end the day
def end_day(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    unfinished_day = Day.objects.filter(staff=request.user, end=False).first()
    if not unfinished_day:
        return redirect('resturant_start_day')  # Redirect to the start day view if no day has started
    
    unfinished_day.end_time  = datetime.now().time()
    unfinished_day.end = True
    unfinished_day.no_of_sales = Sale.objects.filter(day = unfinished_day).count()
    unfinished_day.end_amount = Sale.objects.filter(day = unfinished_day).aggregate(Sum('total'))['total__sum']
    unfinished_day.save()
    return redirect('resturant_end_of_day_report')  # Redirect to the start day view if no day has started

# Reset 'end day' status at midnight (Optional: handled via management command or cron job)

def audit_report(request):
    # Aggregate data
    total_sales = Sale.objects.filter(completed=True).aggregate(total=Sum('total'))['total'] or 0
    total_items_sold = SaleItem.objects.aggregate(total=Sum('quantity'))['total'] or 0
    inventory_data = Inventory.objects.all()
    sales_per_day = (
        Sale.objects.filter(completed=True)
        .values('date__date')
        .annotate(total_sales=Sum('total'))
        .order_by('-date__date')
    )

    # Data for charts
    inventory_chart_data = {
        "labels": [item.name for item in inventory_data],
        "values": [item.quantity for item in inventory_data],
    }

    sales_chart_data = {
        "labels": [str(day['date__date']) for day in sales_per_day],
        "values": [float(day['total_sales']) for day in sales_per_day],
    }

    context = {
        "total_sales": total_sales,
        "total_items_sold": total_items_sold,
        "inventory_data": inventory_data,
        "sales_per_day": sales_per_day,
        "inventory_chart_data": inventory_chart_data,
        "sales_chart_data": sales_chart_data,
    }
    return render(request, "resturant/audit_report.html", context)


def fetch_orders(request):
    orders = Sale.objects.values('id', 'waiter', 'resturant_items', 'total', 'completed','Table_no', 'type')
    return JsonResponse({'orders': list(orders)})


def get_order_details(request, sale_id):
    if request.method == 'GET':
        # Fetch the sale and related items
        sale = get_object_or_404(Sale, id=sale_id)
        sale_items = SaleItem.objects.filter(sale=sale)

        # Build the order details dictionary
        order_details = {
            'id': sale.id,
            'tableNumber': sale.Table_no,
            'waiter': sale.waiter.username,
            'items': [
                {
                    'name': item.product.name,
                    'quantity': item.quantity,
                    'notes': '',  # Add notes here if available in your model
                }
                for item in sale_items
            ]
        }

        return JsonResponse(order_details, safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Sale, SaleItem, Inventory, Payment, Day, CustomUser, Category

def dashboard(request):
    # Prefetch and aggregate required data
    sales_data = Sale.objects.filter(completed=True, paid=True)
    sale_items_data = SaleItem.objects.filter(sale__paid=True)
    inventory_data = Inventory.objects.all()
    payment_data = Payment.objects.filter(sale__paid=True)
    days_count = Day.objects.count()
    categories_count = Category.objects.count()
    staff_count = CustomUser.objects.filter(section="restaurant").count()

    # Metrics
    total_sales = sales_data.aggregate(total=Sum('total'))['total'] or 0
    total_items_sold = sale_items_data.aggregate(total=Sum('quantity'))['total'] or 0
    total_inventory_value = inventory_data.aggregate(total=Sum('price'))['total'] or 0
    total_payments = payment_data.aggregate(total=Sum('amount'))['total'] or 0

    # Staff-related Metrics
    waiter_sales = (
        sales_data.values("waiter__username")
        .annotate(total_sales=Sum("total"), sales_count=Count("id"))
        .order_by("-total_sales")[:5]
    )

    # Top-selling Products
    top_products = (
        sale_items_data.values("product__name")
        .annotate(quantity_sold=Sum("quantity"))
        .order_by("-quantity_sold")[:5]
    )

    # Payments Breakdown
    payment_breakdown = (
        payment_data.values("payment_type")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    # Daily Sales Data for Chart
    daily_sales = (
        sales_data.extra({"day": "DATE(date)"})
        .values("day")
        .annotate(total=Sum("total"))
        .order_by("day")
    )
    sales_chart_labels = [entry["day"].strftime("%Y-%m-%d") for entry in daily_sales]
    sales_chart_values = [float(entry["total"]) for entry in daily_sales]

    # Monthly Sales Data for Chart
    monthly_sales = (
        sales_data.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total'))
        .order_by('month')
    )
    monthly_sales_labels = [entry['month'].strftime('%Y-%m') for entry in monthly_sales]
    monthly_sales_values = [float(entry['total']) for entry in monthly_sales]

    # Prepare context for rendering
    context = {
        "total_sales": total_sales,
        "total_items_sold": total_items_sold,
        "total_inventory_value": total_inventory_value,
        "total_payments": total_payments,
        "total_days": days_count,
        "total_categories": categories_count,
        "total_staff": staff_count,
        "waiter_sales": waiter_sales,
        "top_products": top_products,
        "payment_breakdown": payment_breakdown,
        "sales_chart_labels": sales_chart_labels,
        "sales_chart_values": sales_chart_values,
        "inventory_chart_labels": monthly_sales_labels,
        "inventory_chart_values": monthly_sales_values,
    }

    return render(request, "resturant/dashboard.html", context)


@login_required
def manage_approvals(request):
    pending_days = Day.objects.filter(approved=False, end=True)
    pending_discounts = SaleDiscount.objects.filter(approved=False)
    context = {
        "pending_days": pending_days,
        "pending_discounts": pending_discounts,
    }
    return render(request, "resturant/approvals/manage_approvals.html", context)

@login_required
def approve_day(request, day_id):
    if request.method == "POST":
        day = get_object_or_404(Day, id=day_id, approved=False)
        day.approved = True
        day.save()
        return JsonResponse({"message": "Day approved successfully!"})
    return JsonResponse({"error": "Invalid request method."}, status=400)

@login_required
def approve_discount(request, discount_id):
    if request.method == "POST":
        discount = get_object_or_404(SaleDiscount, id=discount_id, approved=False)
        discount.approved = True
        discount.save()
        return JsonResponse({"message": "Discount approved successfully!"})
    return JsonResponse({"error": "Invalid request method."}, status=400)


def generate_receipt_number():
    return str(uuid.uuid4())[:12]  

def get_receipt_details(request, sale_id):
    if request.method == 'GET':
        # Fetch the sale and related receipt
        sale = get_object_or_404(Sale, id=sale_id)
        receipt, created = Receipt.objects.get_or_create(sale=sale, defaults={
            'receipt_number': generate_receipt_number(),  # Replace this with your receipt number generation logic
        })
        payment = Payment.objects.filter(sale=sale).first()

        # Build the receipt details dictionary
        receipt_details = {
            'receipt_number': receipt.receipt_number,
            'sale_id': sale.id,
            'table_number': sale.Table_no,
            'cashier_name': sale.cashier.username,
            'total_amount': sale.total,
            'payment_type': payment.payment_type if payment else 'Unknown',
            'paid_by': payment.paid_by if payment else 'Unknown',
            'items': [
                {
                    'name': item.product.name,
                    'quantity': item.quantity,
                    'price': item.price,
                }
                for item in SaleItem.objects.filter(sale=sale)
            ]
        }
        return JsonResponse(receipt_details, safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)