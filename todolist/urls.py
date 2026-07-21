from django.urls import path
from . import views

urlpatterns = [
    path("",views.first),
    path("b/",views.second)
]
