from django.contrib import admin
from .models import Medicine, FoodItem, Notification

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'quantity', 'expiry_date', 'status', 'created_at')
    list_filter = ('expiry_date', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'quantity', 'expiry_date', 'status', 'created_at')
    list_filter = ('expiry_date', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'level', 'item_type', 'item_name', 'is_read', 'created_at')
    list_filter = ('level', 'is_read', 'item_type')
    search_fields = ('title', 'message', 'user__username', 'item_name')
    list_editable = ('is_read',)
