from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect
from cal.models import Client, Location
from .forms import LoginForm, RegisterForm
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# Create your views here.
def index(request):
    return render(request, 'login/index.html', {})


def login_view(request, client_name=None, location_name=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)

        if form.is_valid():

            field_dict = form.cleaned_data
            
            user = authenticate(username=field_dict.get('username'), password=field_dict.get('password'))

            if user not in client.users.all() or user not in location.users.all():
                return render(request, 'cal/client_location_user_error.html', {'client_name': client_name, 'location_name': location_name})

            if user is not None:
                login(request, user)
                return redirect('month_view', client_name=client_name, location_name=location_name)
            else:
                return render(request, 'login/login_fail.html', {'client_name': client_name, 'location_name': location_name})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, 'login/login.html', {'form': form})


def register(request, client_name=None, location_name=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)

        if form.is_valid():
            field_dict = form.cleaned_data
            username = field_dict.get('username')
            password = field_dict.get('password1')
            name_with_initial = field_dict.get('name_with_initial')

            user = User.objects.create_user(username=username, password=password, first_name=name_with_initial)

            client.users.add(user)
            location.users.add(user)

            login(request, user)
            
            return redirect('month_view', client_name=client_name, location_name=location_name)
        
    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()
    
    return render(request, 'login/register.html', {'form': form})


def login_fail(request, client_name=None, location_name=None):
    return render(request, 'login/login_fail.html', {'client_name': client_name, 'location_name': location_name})
