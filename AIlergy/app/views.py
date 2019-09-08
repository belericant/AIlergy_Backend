from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def requestResponse(request):
    sentData = request.POST['data']
    

