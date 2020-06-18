from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import LoginForm, RegisterForm
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    return render(request, 'login/index.html', {})


def login_view(request):

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)

        if form.is_valid():

            field_dict = form.cleaned_data
            
            user = authenticate(username=field_dict.get('username'), password=field_dict.get('password'))

            if user is not None:
                login(request, user)
                return redirect('month_view')
            else:
                return render(request, 'login/login_fail.html', {})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, 'login/login.html', {'form': form})


def register(request):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('no_perm')

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)

        if form.is_valid():
            field_dict = form.cleaned_data
            username = field_dict.get('username')
            password = field_dict.get('password1')
            name_with_initial = field_dict.get('name_with_initial')

            user = User.objects.create_user(username=username, password=password, first_name=name_with_initial)

            login(request, user)
            
            return redirect('month_view')
        else:
            print("register invalid")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()
    
    return render(request, 'login/register.html', {'form': form})


def login_fail(request):
    return render(request, 'login/login_fail.html', {})
