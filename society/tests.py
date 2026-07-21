from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from .models import Unit, MaintenanceCharge, ExtraCharge, Payment, DutyTurn, ActivityLog


class UnitModelTest(TestCase):
    """Test cases for Unit model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.unit = Unit.objects.create(
            unit_number='A-101',
            floor=1,
            resident=self.user,
            sqft=1000
        )
    
    def test_unit_creation(self):
        self.assertEqual(self.unit.unit_number, 'A-101')
        self.assertEqual(self.unit.floor, 1)
        self.assertEqual(self.unit.resident, self.user)
    
    def test_get_pending_dues_no_charges(self):
        self.assertEqual(self.unit.get_pending_dues(), 0)
    
    def test_get_pending_dues_with_charges(self):
        MaintenanceCharge.objects.create(
            unit=self.unit,
            amount=500.00,
            month=date.today(),
            due_date=date.today() + timedelta(days=30)
        )
        self.assertEqual(self.unit.get_pending_dues(), 500.00)


class PaymentModelTest(TestCase):
    """Test cases for Payment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.unit = Unit.objects.create(
            unit_number='A-101',
            floor=1,
            resident=self.user,
            sqft=1000
        )
        self.maintenance = MaintenanceCharge.objects.create(
            unit=self.unit,
            amount=500.00,
            month=date.today(),
            due_date=date.today() + timedelta(days=30)
        )
    
    def test_payment_creation(self):
        payment = Payment.objects.create(
            unit=self.unit,
            maintenance=self.maintenance,
            amount=500.00,
            payment_date=date.today(),
            payment_method='upi',
            transaction_id='UPI123456'
        )
        self.assertEqual(payment.amount, 500.00)
        self.assertEqual(payment.payment_method, 'upi')
    
    def test_payment_auto_marks_charge_paid(self):
        self.assertEqual(self.maintenance.status, 'pending')
        
        Payment.objects.create(
            unit=self.unit,
            maintenance=self.maintenance,
            amount=500.00,
            payment_date=date.today(),
            payment_method='upi',
            transaction_id='UPI123456'
        )
        
        self.maintenance.refresh_from_db()
        self.assertEqual(self.maintenance.status, 'paid')


class ViewTest(TestCase):
    """Test cases for views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.admin_user = User.objects.create_superuser(username='admin', password='admin123')
        self.unit = Unit.objects.create(
            unit_number='A-101',
            floor=1,
            resident=self.user,
            sqft=1000
        )
    
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_dashboard_requires_login(self):
        response = self.client.get('/dashboard/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_dashboard_accessible_to_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/dashboard/admin/')
        self.assertEqual(response.status_code, 200)


class ActivityLogTest(TestCase):
    """Test cases for ActivityLog model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_activity_log_creation(self):
        log = ActivityLog.objects.create(
            user=self.user,
            action='login',
            model_name='User',
            description='User logged in',
            ip_address='127.0.0.1'
        )
        self.assertEqual(log.action, 'login')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.model_name, 'User')


class IntegrationTest(TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.admin_user = User.objects.create_superuser(username='admin', password='admin123')
        self.unit = Unit.objects.create(
            unit_number='A-101',
            floor=1,
            resident=self.user,
            sqft=1000
        )
    
    def test_complete_payment_workflow(self):
        """Test the complete workflow from charge creation to payment"""
        # Create maintenance charge
        maintenance = MaintenanceCharge.objects.create(
            unit=self.unit,
            amount=500.00,
            month=date.today(),
            due_date=date.today() + timedelta(days=30)
        )
        
        # Verify charge is pending
        self.assertEqual(maintenance.status, 'pending')
        self.assertEqual(self.unit.get_pending_dues(), 500.00)
        
        # Create payment
        payment = Payment.objects.create(
            unit=self.unit,
            maintenance=maintenance,
            amount=500.00,
            payment_date=date.today(),
            payment_method='upi',
            transaction_id='UPI123456'
        )
        
        # Verify charge is now paid
        maintenance.refresh_from_db()
        self.assertEqual(maintenance.status, 'paid')
        self.assertEqual(self.unit.get_pending_dues(), 0)
