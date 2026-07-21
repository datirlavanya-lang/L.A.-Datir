from django.urls import path
from . import views

urlpatterns=[
    path('', views.say_hello),
    path('one/',views.first),
    path("two/",views.second)
]
