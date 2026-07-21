from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from django.contrib import messages
from datetime import date
from .models import Unit, MaintenanceCharge, ExtraCharge, Payment, DutyTurn
from .forms import PaymentForm, ExtraChargeForm, MaintenanceChargeForm, DutyTurnForm, BulkMaintenanceForm, UserRegistrationForm, UnitForm


# ====================== RESIDENT VIEWS ======================

def home(request):
        """Home page - show welcome page"""
        if request.user.is_authenticated:
            # Redirect authenticated users to appropriate dashboard
            if request.user.is_staff or request.user.is_superuser:
                return redirect('admin-dashboard')
            else:
                # Check if user has a unit assigned
                try:
                    unit = Unit.objects.get(resident=request.user)
                    return redirect('resident-dashboard')
                except Unit.DoesNotExist:
                    # User is logged in but has no unit assigned - show a welcome page for new users
                    return render(request, "society/home.html", {
                        'new_user': True,
                        'message': 'Welcome! Your account has been created successfully. Please contact your society administrator to assign you to a unit.'
                    })
        return render(request, "society/home.html")

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'society/register.html', {'form': form})
class ResidentDashboardView(LoginRequiredMixin, ListView):
    """Resident's main dashboard showing dues and payment history"""
    template_name = 'society/resident_dashboard.html'
    context_object_name = 'units'
    

    def get_queryset(self):
        # Get units assigned to this resident
        return Unit.objects.filter(resident=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_units = self.get_queryset()
        
        # Calculate totals
        total_pending = 0
        total_overdue = 0
        
        for unit in user_units:
            pending_maintenance = MaintenanceCharge.objects.filter(
                unit=unit, status='pending').aggregate(total=Sum('amount'))['total'] or 0
            pending_extra = ExtraCharge.objects.filter(
                unit=unit, status='pending').aggregate(total=Sum('amount'))['total'] or 0
            
            total_pending += pending_maintenance + pending_extra
            
            # Count overdue
            overdue_maintenance = MaintenanceCharge.objects.filter(
                unit=unit, status='pending', due_date__lt=date.today()).count()
            overdue_extra = ExtraCharge.objects.filter(
                unit=unit, status='pending', charge_date__lt=date.today()).count()
            
            total_overdue += overdue_maintenance + overdue_extra
        
        context['total_pending'] = total_pending
        context['total_overdue'] = total_overdue
        context['recent_payments'] = Payment.objects.filter(
            unit__resident=self.request.user).order_by('-payment_date')[:5]
        
        return context


class ResidentDuesView(LoginRequiredMixin, DetailView):
    """View all dues (maintenance + extra charges) for a unit"""
    model = Unit
    template_name = 'society/resident_dues.html'
    context_object_name = 'unit'
    
    def get_object(self):
        return get_object_or_404(Unit, pk=self.kwargs['pk'], resident=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unit = self.object
        
        context['maintenance_charges'] = MaintenanceCharge.objects.filter(unit=unit).order_by('-month')
        context['extra_charges'] = ExtraCharge.objects.filter(unit=unit).order_by('-charge_date')
        context['total_pending'] = unit.get_pending_dues()
        
        return context


class ResidentPaymentHistoryView(LoginRequiredMixin, ListView):
    """View payment history"""
    model = Payment
    template_name = 'society/resident_payments.html'
    context_object_name = 'payments'
    paginate_by = 10
    
    def get_queryset(self):
        return Payment.objects.filter(unit__resident=self.request.user).order_by('-payment_date')


class ResidentDutyView(LoginRequiredMixin, ListView):
    """View current and upcoming duty turns"""
    model = DutyTurn
    template_name = 'society/resident_duty.html'
    context_object_name = 'duties'
    
    def get_queryset(self):
        user_units = Unit.objects.filter(resident=self.request.user)
        return DutyTurn.objects.filter(unit__in=user_units).order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_units = Unit.objects.filter(resident=self.request.user)
        
        current_duties = DutyTurn.objects.filter(
            unit__in=user_units, 
            start_date__lte=date.today(), 
            end_date__gte=date.today()
        )
        context['current_duties'] = current_duties
        
        return context


# ====================== ADMIN VIEWS ======================

class IsAdminMixin(UserPassesTestMixin):
    """Check if user is admin (superuser or staff)"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


def admin_dashboard_test(request):
    """Simple test view for admin dashboard"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('login')
    
    return render(request, "society/admin_dashboard_test.html")

class AdminDashboardView(IsAdminMixin, ListView):
    """Admin dashboard with overall statistics"""
    template_name = 'society/admin_dashboard.html'
    context_object_name = 'units'
    
    def get_queryset(self):
        try:
            return Unit.objects.all().order_by('unit_number')
        except:
            return Unit.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Overall statistics
            total_units = Unit.objects.count()
            total_pending = MaintenanceCharge.objects.filter(status='pending').aggregate(
                total=Sum('amount'))['total'] or 0
            total_extra_pending = ExtraCharge.objects.filter(status='pending').aggregate(
                total=Sum('amount'))['total'] or 0
            total_collected = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
            
            context['total_units'] = total_units
            context['total_pending_dues'] = total_pending + total_extra_pending
            context['total_collected'] = total_collected
            
            # Units with overdue payments
            overdue_units = []
            for unit in self.get_queryset():
                overdue_count = MaintenanceCharge.objects.filter(
                    unit=unit, status='pending', due_date__lt=date.today()).count()
                overdue_count += ExtraCharge.objects.filter(
                    unit=unit, status='pending', charge_date__lt=date.today()).count()
                if overdue_count > 0:
                    overdue_units.append((unit, overdue_count))
            
            context['overdue_units'] = overdue_units
            context['recent_payments'] = Payment.objects.all().order_by('-payment_date')[:5]
        except Exception as e:
            context['error'] = str(e)
            context['total_units'] = 0
            context['total_pending_dues'] = 0
            context['total_collected'] = 0
            context['overdue_units'] = []
            context['recent_payments'] = []
        
        return context


class AdminUnitsListView(IsAdminMixin, ListView):
    """List all units with resident info"""
    model = Unit
    template_name = 'society/admin_units.html'
    context_object_name = 'units'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Unit.objects.all().order_by('unit_number')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(unit_number__icontains=search) | 
                                      Q(resident__first_name__icontains=search))
        return queryset


class UnitCreateView(IsAdminMixin, CreateView):
    """Create a new unit"""
    model = Unit
    form_class = UnitForm
    template_name = 'society/unit_form.html'
    success_url = reverse_lazy('admin-units')
    
    def form_valid(self, form):
        messages.success(self.request, 'Unit created successfully!')
        return super().form_valid(form)


class UnitDetailView(IsAdminMixin, DetailView):
    """View unit details with all dues and payments"""
    model = Unit
    template_name = 'society/unit_detail.html'
    context_object_name = 'unit'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unit = self.object
        
        context['maintenance_charges'] = MaintenanceCharge.objects.filter(unit=unit).order_by('-month')
        context['extra_charges'] = ExtraCharge.objects.filter(unit=unit).order_by('-charge_date')
        context['payments'] = Payment.objects.filter(unit=unit).order_by('-payment_date')
        context['duty_turns'] = DutyTurn.objects.filter(unit=unit).order_by('-start_date')
        context['total_pending'] = unit.get_pending_dues()
        
        return context


# ====================== MAINTENANCE VIEWS ======================

class MaintenanceChargeCreateView(IsAdminMixin, CreateView):
    """Create a single maintenance charge"""
    model = MaintenanceCharge
    form_class = MaintenanceChargeForm
    template_name = 'society/maintenance_form.html'
    success_url = reverse_lazy('admin-dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, 'Maintenance charge created successfully!')
        return super().form_valid(form)


class BulkMaintenanceChargeView(IsAdminMixin, View):
    """Generate maintenance charges for all units"""
    template_name = 'society/bulk_maintenance.html'
    
    def get(self, request, *args, **kwargs):
        form = BulkMaintenanceForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = BulkMaintenanceForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            month = form.cleaned_data['month']
            due_date = form.cleaned_data['due_date']
            
            units = Unit.objects.all()
            created_count = 0
            
            for unit in units:
                charge, created = MaintenanceCharge.objects.get_or_create(
                    unit=unit,
                    month=month,
                    defaults={
                        'amount': amount,
                        'due_date': due_date,
                        'status': 'pending'
                    }
                )
                if created:
                    created_count += 1
            
            messages.success(request, f'{created_count} maintenance charges created!')
            return redirect('/dashboard/admin/')
        
        return render(request, self.template_name, {'form': form})


class MaintenanceChargeUpdateView(IsAdminMixin, UpdateView):
    """Edit maintenance charge"""
    model = MaintenanceCharge
    form_class = MaintenanceChargeForm
    template_name = 'society/maintenance_form.html'
    success_url = reverse_lazy('admin-dashboard')


class MaintenanceChargeDeleteView(IsAdminMixin, DeleteView):
    """Delete maintenance charge"""
    model = MaintenanceCharge
    template_name = 'society/confirm_delete.html'
    success_url = reverse_lazy('admin-dashboard')


# ====================== EXTRA CHARGE VIEWS ======================

class ExtraChargeCreateView(IsAdminMixin, CreateView):
    """Create an extra charge (fine, damage, etc.)"""
    model = ExtraCharge
    form_class = ExtraChargeForm
    template_name = 'society/extra_charge_form.html'
    success_url = reverse_lazy('admin-dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, 'Extra charge created successfully!')
        return super().form_valid(form)


class ExtraChargeUpdateView(IsAdminMixin, UpdateView):
    """Edit extra charge"""
    model = ExtraCharge
    form_class = ExtraChargeForm
    template_name = 'society/extra_charge_form.html'
    success_url = reverse_lazy('admin-dashboard')


class ExtraChargeDeleteView(IsAdminMixin, DeleteView):
    """Delete extra charge"""
    model = ExtraCharge
    template_name = 'society/confirm_delete.html'
    success_url = reverse_lazy('admin-dashboard')


# ====================== PAYMENT VIEWS ======================

class PaymentCreateView(LoginRequiredMixin, CreateView):
    """Record a payment for maintenance or extra charge"""
    model = Payment
    form_class = PaymentForm
    template_name = 'society/payment_form.html'
    success_url = reverse_lazy('resident-dashboard')
    
    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # Limit unit dropdown to user's units
        user_units = Unit.objects.filter(resident=self.request.user)
        form.fields['unit'].queryset = user_units
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Show pending charges for this resident
        user_units = Unit.objects.filter(resident=self.request.user)
        context['pending_maintenance'] = MaintenanceCharge.objects.filter(
            unit__in=user_units, status='pending')
        context['pending_extra'] = ExtraCharge.objects.filter(
            unit__in=user_units, status='pending')
        return context
    
    def form_valid(self, form):
        payment = form.save(commit=False)
        
        # Verify the user is assigned to this unit
        if payment.unit.resident != self.request.user:
            messages.error(self.request, 'You can only make payments for units assigned to you.')
            return redirect('add-payment')
        
        payment.save()
        messages.success(self.request, 'Payment recorded successfully!')
        return redirect('resident-dashboard')


class PaymentListView(IsAdminMixin, ListView):
    """View all payments"""
    model = Payment
    template_name = 'society/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Payment.objects.all().order_by('-payment_date')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(unit__unit_number__icontains=search)
        return queryset


# ====================== DUTY VIEWS ======================

class DutyTurnCreateView(IsAdminMixin, CreateView):
    """Assign a duty to a unit"""
    model = DutyTurn
    form_class = DutyTurnForm
    template_name = 'society/duty_form.html'
    success_url = reverse_lazy('admin-dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, 'Duty assigned successfully!')
        return super().form_valid(form)


class DutyTurnListView(IsAdminMixin, ListView):
    """View all duty assignments"""
    model = DutyTurn
    template_name = 'society/duty_list.html'
    context_object_name = 'duties'
    paginate_by = 20
    
    def get_queryset(self):
        return DutyTurn.objects.all().order_by('-start_date')


class DutyTurnUpdateView(IsAdminMixin, UpdateView):
    """Update duty assignment"""
    model = DutyTurn
    form_class = DutyTurnForm
    template_name = 'society/duty_form.html'
    success_url = reverse_lazy('duty-list')


class DutyTurnDeleteView(IsAdminMixin, DeleteView):
    """Remove duty assignment"""
    model = DutyTurn
    template_name = 'society/confirm_delete.html'
    success_url = reverse_lazy('duty-list')
