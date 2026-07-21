from django.urls import path,include
from django.conf import settings
from . import views

urlpatterns = [
    # RESIDENT URLS
    path('',views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.ResidentDashboardView.as_view(), name='resident-dashboard'),
    path('unit/<int:pk>/dues/', views.ResidentDuesView.as_view(), name='resident-dues'),
    path('payments/history/', views.ResidentPaymentHistoryView.as_view(), name='payment-history'),
    path('duty/', views.ResidentDutyView.as_view(), name='resident-duty'),
    path('payment/add/', views.PaymentCreateView.as_view(), name='add-payment'),
    
    # ADMIN URLS
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('dashboard/units/', views.AdminUnitsListView.as_view(), name='admin-units'),
    path('dashboard/unit/add/', views.UnitCreateView.as_view(), name='add-unit'),
    path('dashboard/unit/<int:pk>/', views.UnitDetailView.as_view(), name='unit-detail'),
    
    # MAINTENANCE URLS
    path('dashboard/maintenance/add/', views.MaintenanceChargeCreateView.as_view(), name='add-maintenance'),
    path('dashboard/maintenance/bulk/', views.BulkMaintenanceChargeView.as_view(), name='bulk-maintenance'),
    path('dashboard/maintenance/<int:pk>/edit/', views.MaintenanceChargeUpdateView.as_view(), name='edit-maintenance'),
    path('dashboard/maintenance/<int:pk>/delete/', views.MaintenanceChargeDeleteView.as_view(), name='delete-maintenance'),
    
    # EXTRA CHARGE URLS
    path('dashboard/extra-charge/add/', views.ExtraChargeCreateView.as_view(), name='add-extra-charge'),
    path('dashboard/extra-charge/<int:pk>/edit/', views.ExtraChargeUpdateView.as_view(), name='edit-extra-charge'),
    path('dashboard/extra-charge/<int:pk>/delete/', views.ExtraChargeDeleteView.as_view(), name='delete-extra-charge'),
    
    # PAYMENT URLS
    path('dashboard/payments/', views.PaymentListView.as_view(), name='payment-list'),
    
    # DUTY URLS
    path('dashboard/duty/add/', views.DutyTurnCreateView.as_view(), name='add-duty'),
    path('dashboard/duty/', views.DutyTurnListView.as_view(), name='duty-list'),
    path('dashboard/duty/<int:pk>/edit/', views.DutyTurnUpdateView.as_view(), name='edit-duty'),
    path('dashboard/duty/<int:pk>/delete/', views.DutyTurnDeleteView.as_view(), name='delete-duty'),
]
