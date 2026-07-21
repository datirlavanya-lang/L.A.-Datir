from django.shortcuts import render
from django.http import HttpResponse,request

# Create your views here.
def first(request):
    return render(request,"to.html")

def second(request):
    return render(request,"to2.html")