from django.shortcuts import render
from django.contrib import messages


def home(request):
    messages.info(request, 'Success')
    return render(request, 'home.html')
