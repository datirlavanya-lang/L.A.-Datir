from django.contrib import admin
from .models import Unit, MaintenanceCharge, ExtraCharge, Payment, DutyTurn, ActivityLog


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['unit_number', 'floor', 'resident', 'sqft']
    list_filter = ['floor', 'created_at']
    search_fields = ['unit_number', 'resident__first_name', 'resident__last_name']
    raw_id_fields = ['resident']


@admin.register(MaintenanceCharge)
class MaintenanceChargeAdmin(admin.ModelAdmin):
    list_display = ['unit', 'month', 'amount', 'status', 'due_date']
    list_filter = ['status', 'month', 'created_at']
    search_fields = ['unit__unit_number']
    readonly_fields = ['created_at']
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        from datetime import date
        updated = queryset.update(status='paid', paid_date=date.today())
        self.message_user(request, f'{updated} charges marked as paid.')
    mark_as_paid.short_description = "Mark selected as paid"


@admin.register(ExtraCharge)
class ExtraChargeAdmin(admin.ModelAdmin):
    list_display = ['unit', 'description', 'amount', 'status', 'charge_date']
    list_filter = ['status', 'charge_date', 'created_at']
    search_fields = ['unit__unit_number', 'description']
    readonly_fields = ['created_at']
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        from datetime import date
        updated = queryset.update(status='paid', paid_date=date.today())
        self.message_user(request, f'{updated} charges marked as paid.')
    mark_as_paid.short_description = "Mark selected as paid"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(DutyTurn)
class DutyTurnAdmin(admin.ModelAdmin):
    list_display = ['unit', 'duty_type', 'start_date', 'end_date', 'assigned_to', 'completed']
    list_filter = ['duty_type', 'start_date', 'completed']
    search_fields = ['unit__unit_number', 'assigned_to__first_name']
    raw_id_fields = ['assigned_to', 'unit']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'model_name', 'description']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
