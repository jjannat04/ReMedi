from django.contrib import admin
from .models import Medicine
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'original_price', 'resale_price', 'expiry_date')
    list_filter = ('status',)
    search_fields = ('name', 'batch_number')