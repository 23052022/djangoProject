from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def route_filter(request, route_type=None, country=None, location=None):
    print(route_type)
    print(country)
    print(location)
    print('<-------------->>')
    return HttpResponse('Ok')

# def route_detail(request):
#     return HttpResponse('Ok')

def route_detail(request):
     pass

def route_reviews(request):
    pass

