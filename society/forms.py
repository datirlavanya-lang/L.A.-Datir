from django import forms
from .models import Payment, MaintenanceCharge, ExtraCharge, DutyTurn, Unit
from django.contrib.auth.models import User


class PaymentForm(forms.ModelForm):
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), 
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Payment
        fields = ['unit', 'amount', 'payment_method', 'transaction_id', 'payment_date']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UPI ID / Check No / Ref No'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ExtraChargeForm(forms.ModelForm):
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), 
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = ExtraCharge
        fields = ['unit', 'description', 'amount', 'charge_date']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Parking Fine, Water Damage'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'charge_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class MaintenanceChargeForm(forms.ModelForm):
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), 
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = MaintenanceCharge
        fields = ['unit', 'amount', 'month', 'due_date']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'month': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class DutyTurnForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), 
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = DutyTurn
        fields = ['unit', 'duty_type', 'start_date', 'end_date', 'assigned_to', 'notes']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'duty_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BulkMaintenanceForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2,
                               widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    month = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    due_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match')
        
        return cleaned_data


class UnitForm(forms.ModelForm):
    resident = forms.ModelChoiceField(queryset=User.objects.all(), 
                                      widget=forms.Select(attrs={'class': 'form-control'}),
                                      required=False)
    
    class Meta:
        model = Unit
        fields = ['unit_number', 'floor', 'resident', 'sqft']
        widgets = {
            'unit_number': forms.TextInput(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'sqft': forms.NumberInput(attrs={'class': 'form-control'}),
        }
