from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def say_hello(request):
    return render(request,"one.html",{"Rank": 100})

def first(request):
    return HttpResponse("My first Django page!")

def second(request):
    x=1
    y=2
    return HttpResponse("Hey guys! I'm learning Django!")

