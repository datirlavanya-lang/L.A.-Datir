from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import date

class Unit(models.Model):
    unit_number = models.CharField(max_length=10, unique=True)
    floor = models.IntegerField(validators=[MinValueValidator(0)])
    resident = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    sqft = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['unit_number']
    
    def __str__(self):
        return f"Unit {self.unit_number}"

    def get_pending_dues(self):
        """Return total pending maintenance + extra charges"""
        maintenance = self.maintenancecharge_set.filter(status='pending').aggregate(
            total=models.Sum('amount'))['total'] or 0
        extra = self.extracharge_set.filter(status='pending').aggregate(
            total=models.Sum('amount'))['total'] or 0
        return maintenance + extra


class MaintenanceCharge(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('paid', 'Paid')]
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(help_text="Month for which maintenance is due")
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-month']
        unique_together = ['unit', 'month']
    
    def __str__(self):
        return f"{self.unit.unit_number} - {self.month.strftime('%B %Y')} - ₹{self.amount}"

    def is_overdue(self):
        return self.status == 'pending' and date.today() > self.due_date


class ExtraCharge(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('paid', 'Paid')]
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    charge_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-charge_date']
    
    def __str__(self):
        return f"{self.unit.unit_number} - {self.description} - ₹{self.amount}"

    def is_overdue(self):
        days_past = (date.today() - self.charge_date).days
        return self.status == 'pending' and days_past > 7


class Payment(models.Model):
    METHODS = [('upi', 'UPI'), ('check', 'Check'), ('cash', 'Cash'), ('transfer', 'Bank Transfer')]
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    maintenance = models.ForeignKey(MaintenanceCharge, on_delete=models.CASCADE, null=True, blank=True)
    extra_charge = models.ForeignKey(ExtraCharge, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.unit.unit_number} - ₹{self.amount} on {self.payment_date}"
    
    def save(self, *args, **kwargs):
        # If this is a new payment (not an update)
        if not self.pk:
            super().save(*args, **kwargs)
            
            # Automatically mark associated charges as paid
            if self.maintenance and self.maintenance.status == 'pending':
                self.maintenance.status = 'paid'
                self.maintenance.paid_date = self.payment_date
                self.maintenance.save()
            
            if self.extra_charge and self.extra_charge.status == 'pending':
                self.extra_charge.status = 'paid'
                self.extra_charge.paid_date = self.payment_date
                self.extra_charge.save()
        else:
            super().save(*args, **kwargs)


class DutyTurn(models.Model):
    DUTY_TYPES = [
        ('water', 'Water Manager'),
        ('security', 'Security Guard'),
        ('cleanliness', 'Cleanliness'),
        ('parking', 'Parking Manager'),
        ('complaint', 'Complaint Handler')
    ]
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    duty_type = models.CharField(max_length=20, choices=DUTY_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.unit.unit_number} - {self.get_duty_type_display()} ({self.start_date} to {self.end_date})"

    def is_active(self):
        return self.start_date <= date.today() <= self.end_date
    
    def is_upcoming(self):
        return self.start_date > date.today()


class ActivityLog(models.Model):
    """Audit trail for all system activities"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('payment', 'Payment'),
        ('charge', 'Charge Created'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{user_str} - {self.action} - {self.model_name} at {self.timestamp}"
