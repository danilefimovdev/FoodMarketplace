from django.shortcuts import render


def v_profile(request):
    return render(request, 'vendors/v_profile.html')