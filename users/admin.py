from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Fields to display in the list view
    list_display = ('username', 'email', 'role', 'section' ,'level','is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'role','level')  # Filters in the sidebar
    search_fields = ('username', 'email', 'phone')  # Search bar fields
    ordering = ('date_joined',)  # Default ordering
    
    # Fieldsets for detail/edit view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'phone', 'avatar','description')}),
        ('Access Info', {'fields': ('role', 'section','level',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    
    # Fields for the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'role', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')  # Horizontal filter for many-to-many fields

# Register the custom user model
admin.site.register(CustomUser, CustomUserAdmin)
