from django.shortcuts import render
from django.contrib import messages

from vendors.models import Vendor


def home(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    return render(request, 'home.html', context={'vendors': vendors})
