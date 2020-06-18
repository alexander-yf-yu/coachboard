from django.shortcuts import render

def index(request):
    return render(request, 'login/landing_index.html', {})
