from django.contrib import admin
from .models import User, Medicine
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'original_price', 'resale_price', 'expiry_date')
    list_filter = ('status',)
    search_fields = ('name', 'batch_number')



@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'is_active', 'license_number')
    list_filter = ('role', 'is_active')
    # Allow quick activation from the list view
    list_editable = ('is_active',)