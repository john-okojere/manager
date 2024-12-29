from django import forms
from .models import Inventory, Category

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name','price','category']

from .models import Day
from users.models import CustomUser as User
class StartDayForm(forms.ModelForm):
    class Meta:
        model = Day
        fields = ['start_amount', 'waiter']

    def __init__(self, *args, **kwargs):
        super(StartDayForm, self).__init__(*args, **kwargs)
        # Filter the waiter queryset to include only users with role 'waiter' and section 'restaurant'
        self.fields['waiter'].queryset = User.objects.filter(role='Waiter', section='restaurant')
class EndDayForm(forms.Form):
    end_amount = forms.DecimalField(max_digits=15, decimal_places=2, label="End Amount")

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']