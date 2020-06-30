from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.safestring import mark_safe
from django.views.generic.edit import DeleteView
from .utils import htmlCalendar, prev_month, next_month, create_shifts_from_pattern
from .forms import CreateShiftForm, CreateSubrequestForm, CreateShiftsForm, CalculateHoursForm
from .models import Shift, SubRequest, Location, Client
from datetime import datetime, timedelta, date, time
from mysite.settings import EMAIL_HOST_USER
import csv
from datetime import timedelta

# def user_client_location_auth(request, client_name, location_name):


# Views here.
def no_auth(request, client_name=None, location_name=None):
    return render(request, 'cal/no_auth.html', {'client_name': client_name, 'location_name': location_name})

def no_perm(request, client_name=None, location_name=None):
    return render(request, 'cal/no_perm.html', {'client_name': client_name, 'location_name': location_name})

def no_exists(request, client_name=None, location_name=None):
    return render(request, 'cal/no_exists.html', {})

def success(request, client_name=None, location_name=None):
    return render(request, 'cal/success.html', {'client_name': client_name, 'location_name': location_name})


def switch_location(request, client_name=None, location_name=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    if not request.user.is_authenticated:
        return redirect('no_auth', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)
    
    user = User.objects.get(id=request.user.id)

    if user not in client.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    client_locations = set(client.locations.all())
    user_locations = set(user.location_set.all())

    locations = list(client_locations & user_locations)

    context = {
        'locations': locations,
        'client_name': client_name,
    }

    return render(request, 'cal/switch_location.html', context)


def month_view(request, month=None, year=None, client_name=None, location_name=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)
    
    if not request.user.is_authenticated:
        return redirect('no_auth', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if year is None and month is None:
        d = datetime.today()
        req_year = d.year
        req_month = d.month
    else:
        req_year = year
        req_month = month

    user_id = request.user.id

    cal = htmlCalendar(user_id, client_name, location_name, year=req_year, month=req_month)

    html_cal = cal.formatmonth(withyear=True)

    context = {}

    context['client_name'] = str(client_name)
    context['location_name'] = str(location_name)

    context['calendar'] = mark_safe(html_cal)
    context['prev_month'] = prev_month(req_year, req_month)
    context['next_month'] = next_month(req_year, req_month)
    context['is_staff'] = False
    context['username'] = request.user.username

    if cal.is_staff():
        context['staff_view'] = mark_safe(cal.generate_staff_view())
        context['is_staff'] = True
    else:
        context['notifications'] = mark_safe(cal.generate_notifications())

    return render(request, 'cal/month_view.html', context)

 
def logout_user(request, client_name=None, location_name=None):
    # Does nothing if not authenticated in first place
    logout(request)
    return redirect('login_main', client_name=client_name, location_name=location_name)


def create_shift(request, client_name=None, location_name=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)
    
    if not request.user.is_authenticated:
        return redirect('no_auth', client_name=client_name, location_name=location_name)
    
    if not request.user.is_staff:
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if request.method == 'POST':
        form = CreateShiftForm(request.POST, client=client, location=location)

        if form.is_valid():
            field_dict = form.cleaned_data

            owner = field_dict.get('user')
            name = field_dict.get('name')
            date = field_dict.get('date')
            start_time = field_dict.get('start_time')
            end_time = field_dict.get('end_time')

            # Creation of new shifts tuple / instance
            new_shift = Shift(
                client=client,
                location=location,
                user=owner, 
                date=date,
                start_time=start_time,
                end_time=end_time,
                name=name,
            )

            # saving instance to database
            new_shift.save()

            return redirect('success', client_name=client_name, location_name=location_name)
        
    else:
        form = CreateShiftForm(client=client, location=location)
        
    return render(request, 'cal/create_shift.html', {'form': form, 'client_name': client_name, 'location_name': location_name})


def create_shifts(request, client_name=None, location_name=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    if not request.user.is_authenticated:
        return redirect('no_auth', client_name=client_name, location_name=location_name)

    if not request.user.is_staff:
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if request.method == 'POST':
        form = CreateShiftsForm(request.POST, client=client, location=location)

        if form.is_valid():
            field_dict = form.cleaned_data

            owner = field_dict.get('user')
            name = field_dict.get('name')
            start_date = field_dict.get('start_date')
            end_date = field_dict.get('end_date')
            start_time = field_dict.get('start_time')
            end_time = field_dict.get('end_time')
            repeat_interval = field_dict.get('repeat_interval')
            repeat_on = field_dict.get('repeat_on')

            create_shifts_from_pattern(
                client=client,
                location=location,
                user_id=owner.id,
                name=name,
                start_date=start_date,
                end_date=end_date,
                start_time=start_time,
                end_time=end_time,
                repeat_on=repeat_on,
                repeat_interval=repeat_interval,
            )

            return redirect('success', client_name=client_name, location_name=location_name)
    else:
        form = CreateShiftsForm(client=client, location=location)

    return render(request, 'cal/create_shifts.html', {'form': form, 'client_name': client_name, 'location_name': location_name})


def create_subrequest(request, client_name=None, location_name=None):
    
    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    if not request.user.is_authenticated:
        return redirect('no_auth', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if request.method == 'POST':
        form = CreateSubrequestForm(request.POST)

        if form.is_valid():
            field_dict = form.cleaned_data

            name = field_dict.get('name')
            date = field_dict.get('date')
            start_time = field_dict.get('start_time')
            end_time = field_dict.get('end_time')
            anonymous = field_dict.get('anonymous')
            user_id = request.user.id

            # Creation of new shifts tuple / instance
            new_subrequest = SubRequest(
                client=client,
                location=location,
                user_id=user_id, 
                start_time=start_time,
                end_time=end_time,
                date=date,
                anonymous=anonymous,
                name=name,
                approved=False,
            )

            # saving instance to database
            new_subrequest.save()

            # email

            send_mail(
                f'New Subrequest',
                f'New subrequest at {location.name} on {date}',
                EMAIL_HOST_USER,
                [],
                fail_silently=True,
            )

            return redirect('success', client_name=client_name, location_name=location_name)
        

    else:
        form = CreateSubrequestForm()
        
    return render(request, 'cal/create_subrequest.html', {'form': form, 'client_name': client_name, 'location_name': location_name})


def view_subrequest(request, client_name=None, location_name=None, sub_id=None):
    # TODO: take action on request

    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    if not request.user.is_authenticated or sub_id is None:
        return redirect('no_auth', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)
    
    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    try:
        subrequest = SubRequest.objects.get(pk=sub_id)
    except SubRequest.DoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except:
        return HttpResponse(status=500)

    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if subrequest.client.id != client.id or subrequest.location.id != location.id:   #check if this subrequest / shift is part of this location
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    name = subrequest.name
    date = subrequest.date
    start_time = subrequest.start_time
    end_time = subrequest.end_time
    anonymous = subrequest.anonymous
    approved = subrequest.approved

    if subrequest.covered_by is None:
        covered_by = ''
    else:
        covered_by = subrequest.covered_by.first_name

    # Dictionary containing visible subrequest information
    info = {
        'Location: ': location.name,
        'Approved: ': approved,
        'Subrequest Name: ': name,
        'Date: ': date,
        'Start Time: ': start_time,
        'End Time: ': end_time,
        'Covered by: ': covered_by
    }

    request_owner = User.objects.get(pk=subrequest.user_id)
    owner_name = request_owner.first_name

    if not anonymous and not request.user.is_staff:
        info['Owner Name: '] = owner_name

    if request.user.is_staff:
        info['Owner: '] = request_owner.username

    # Dictionary containing list of available actions based on user
    actions = {}

    if request_owner.id == request.user.id or request.user.is_staff:
        actions['Delete'] = f'/{client.name}/{location.name}/calendar/delete_subrequest/{sub_id}'

    if request_owner.id != request.user.id and not subrequest.covered_by:
        actions['Sub for this person'] = f'/{client.name}/{location.name}/calendar/toggle_declare_sub/{sub_id}'

    if subrequest.covered_by is not None:
        if request.user.is_staff or request_owner.id == request.user.id or subrequest.covered_by.id == request.user.id:
            actions['Revoke sub decision'] = f'/{client.name}/{location.name}/calendar/toggle_declare_sub/{sub_id}'

    if request.user.is_staff:
        if not subrequest.approved:
            actions['Approve'] = f'/{client.name}/{location.name}/calendar/toggle_approve_subrequest/{sub_id}'
        else:
            actions['Unapprove'] = f'/{client.name}/{location.name}/calendar/toggle_approve_subrequest/{sub_id}'
    
    return render(request, 'cal/view_subrequest.html', {'info': info, 'actions': actions, 'client_name': client_name, 'location_name': location_name})



def view_shift(request, client_name=None, location_name=None, shift_id=None):
    
    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    if not request.user.is_authenticated or shift_id is None:
        return redirect('no_auth', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    try:
        shift = Shift.objects.get(pk=shift_id)
    except Shift.DoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except:
        return HttpResponse(status=500)

    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if shift.client.id != client.id or shift.location.id != location.id:   #check if this subrequest / shift is part of this location
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if shift.user_id != request.user.id and not request.user.is_staff:
        return redirect('no_perm', client_name=client_name, location_name=location_name)


    name = shift.name
    date = shift.date
    start_time = shift.start_time
    end_time = shift.end_time

    info = {
        'Location: ': location.name,
        'Shift Name: ': name,
        'Date: ': date,
        'Start Time: ': start_time,
        'End Time: ': end_time,
    }

    actions = {}
    
    if request.user.is_staff:
        info['Owner: '] = shift.user.username
        actions['Delete'] = f'/{client.name}/{location.name}/calendar/delete_shift/{shift_id}'

    return render(request, 'cal/view_shift.html', {'info': info, 'actions': actions, 'client_name': client_name, 'location_name': location_name})
    

def delete_shift(request, client_name=None, location_name=None, shift_id=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    if not request.user.is_authenticated or shift_id is None:
        return redirect('no_auth', client_name=client_name, location_name=location_name)
    
    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    try:
        shift = Shift.objects.get(pk=shift_id)
    except Shift.DoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except:
        return redirect('no_perm', client_name=client_name, location_name=location_name)


    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)
        
    if not request.user.is_staff:
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if shift.client.id != client.id or shift.location.id != location.id:   #check if this subrequest / shift is part of this location
        return redirect('no_perm', client_name=client_name, location_name=location_name)  

    if request.method == 'POST':
        shift.delete()
        return redirect('success', client_name=client_name, location_name=location_name)
    
    return render(request, 'cal/base_delete_view.html', {'object': shift, 'client_name': client_name, 'location_name': location_name})


def delete_subrequest(request, client_name=None, location_name=None, req_id=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    if not request.user.is_authenticated or req_id is None:
        return redirect('no_auth', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    try:
        req = SubRequest.objects.get(pk=req_id)
    except SubRequest.DoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except:
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)
        
    if req.user_id != request.user.id and not request.user.is_staff:
        return redirect('no_perm', client_name=client_name, location_name=location_name)
        
    if req.client.id != client.id or req.location.id != location.id:   #check if this subrequest / shift is part of this location
        return redirect('no_perm', client_name=client_name, location_name=location_name)         

    if request.method == 'POST':
        req.delete()
        return redirect('success', client_name=client_name, location_name=location_name)
    
    return render(request, 'cal/base_delete_view.html', {'object': req, 'client_name': client_name, 'location_name': location_name})
            

def toggle_declare_sub(request, client_name=None, location_name=None, sub_id=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)
        
    if not request.user.is_authenticated or sub_id is None:
        return redirect('no_auth', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    try:
        req = SubRequest.objects.get(pk=sub_id)
    except SubRequest.DoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except:
        return redirect('no_perm', client_name=client_name, location_name=location_name)  

    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if req.client.id != client.id or req.location.id != location.id:   #check if this subrequest / shift is part of this location
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if request.method == 'POST':

        if not req.covered_by:
            req.covered_by = request.user
        else:
            req.covered_by = None
    
        req.approved = False
        req.save()
        return redirect('success', client_name=client_name, location_name=location_name)
    
    return render(request, 'cal/toggle_declare_sub.html', {'client_name': client_name, 'location_name': location_name})


def toggle_approve_subrequest(request, client_name=None, location_name=None, sub_id=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    if not request.user.is_authenticated or sub_id is None:
        return redirect('no_auth', client_name=client_name, location_name=location_name)

    if not request.user.is_staff:
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    try:
        req = SubRequest.objects.get(pk=sub_id)
    except SubRequest.DoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except:
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if req.client.id != client.id or req.location.id != location.id:   #check if this subrequest / shift is part of this location
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    if request.method == 'POST':
        req.approved = not req.approved
        req.save()
        return redirect('success', client_name=client_name, location_name=location_name)
    
    return render(request, 'cal/toggle_approve_subrequest.html', {'client_name': client_name, 'location_name': location_name})


def calculate_hours(request, client_name=None, location_name=None):

    if client_name is None or location_name is None:
        return HttpResponse(status=500)

    if not request.user.is_authenticated:
        return redirect('no_auth', client_name=client_name, location_name=location_name)

    if not request.user.is_staff:
        return redirect('no_perm', client_name=client_name, location_name=location_name)

    try:
        client = Client.objects.get(name__iexact=str(client_name))
        location = Location.objects.get(name__iexact=str(location_name))
    except ObjectDoesNotExist:
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    except MultipleObjectsReturned:
        return HttpResponse(status=500)

    if not location in client.locations.all():
        return render(request, 'mysite/no_location_exists.html', {'client_name': str(client_name)})

    user = User.objects.get(id=request.user.id)
    
    if location not in client.locations.all():
        return redirect('no_exists', client_name=client_name, location_name=location_name)
    
    if user not in client.users.all() or user not in location.users.all():
        return redirect('no_perm', client_name=client_name, location_name=location_name)


    if request.method == 'POST':
        form = CalculateHoursForm(request.POST)

        if form.is_valid():
            field_dict = form.cleaned_data
            
            start_date = field_dict.get('start_date')
            end_date = field_dict.get('end_date')
            
            all_shifts_in_time_period = Shift.objects.filter(date__gte=start_date, date__lte=end_date, client=client)
            all_subdays_in_time_period = SubRequest.objects.exclude(date__gte=start_date, date__lte=end_date, client=client, covered_by__exact=None)

            def difference_in_seconds(start_time, end_time):
                end = datetime.combine(date.today(), end_time)
                start = datetime.combine(date.today(), start_time)
                diff = end - start
                return diff.total_seconds()

            users = client.users.all()

            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{client_name}_hours_{start_date}_to_{end_date}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['User', 'Shift Hours', 'Subday Hours', 'Total Hours'])

            for user in users:
                total_shift_seconds = 0
                total_sub_seconds = 0
                shifts = all_shifts_in_time_period.filter(user_id=user.id)
                subdays = all_subdays_in_time_period.filter(covered_by_id__exact=user.id)

                for shift in shifts:
                    total_shift_seconds += difference_in_seconds(shift.start_time, shift.end_time)

                for sub in subdays:
                    total_sub_seconds += difference_in_seconds(sub.start_time, sub.end_time)
                
                total_seconds = total_shift_seconds + total_sub_seconds
                
                writer.writerow([str(user.username), str(timedelta(seconds=total_shift_seconds)), str(timedelta(seconds=total_sub_seconds)), str(timedelta(seconds=total_seconds))])

            return response

    else:
        form = CalculateHoursForm()

    return render(request, 'cal/calculate_hours.html', {'form': form, 'client_name': client_name, 'location_name': location_name})





