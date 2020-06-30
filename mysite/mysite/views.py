from django.shortcuts import render, redirect
from django.http import HttpResponse
from cal.models import Client, Location
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

def index(request):
    return render(request, 'mysite/index.html', {})

def client_dispatch(request, client_name=None):
    
    if client_name is None:
        return HttpResponse(status=500)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
    except ObjectDoesNotExist:
        return render(request, 'mysite/no_client_exists.html', {})
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    locations = client.locations.all()

    context = {
        'client_name': str(client_name),
        'locations': locations,
    }

    return render(request, 'login/client_dispatch.html', context)


def client_location_dispatch(request, client_name=None, location_name=None):
    
    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
    except ObjectDoesNotExist:
        return render(request, 'mysite/no_client_exists.html', {})
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    try:
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})
    
    context = {
        'client_name': client_name,
        'location_name': location_name,
    }

    return render(request, f'landing/{client_name.lower()}.html', context)


