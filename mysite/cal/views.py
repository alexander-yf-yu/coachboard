from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.views.generic.edit import DeleteView
from .utils import htmlCalendar, prev_month, next_month, create_shiftgroup_from_pattern
from .forms import CreateShiftForm, CreateSubrequestForm, CreateShiftGroupForm, CalculateHoursForm
from .models import Shifts, SubRequests
from datetime import datetime, timedelta, date, time


# Views here.
def index(request):
    return render(request, 'cal/index.html', {})

def no_auth(request):
    return render(request, 'cal/no_auth.html', {})

def no_perm(request):
    return render(request, 'cal/no_perm.html', {})

def no_exists(request):
    return render(request, 'cal/no_exists.html', {})

def success(request):
    return render(request, 'cal/success.html', {})


def month_view(request, month=None, year=None):

    if not request.user.is_authenticated:
        return redirect('no_auth')

    if request.method == 'GET':
        if year is None and month is None:
            d = datetime.today()
            req_year = d.year
            req_month = d.month
        else:
            req_year = year
            req_month = month

        user_id = request.user.id

        cal = htmlCalendar(user_id, year=req_year, month=req_month)
        html_cal = cal.formatmonth(withyear=True)

        context = {}

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
    
    return render(request, 'cal/month_view.html', {})

 
def logout_user(request):
    # Does nothing if not authenticated in first place
    logout(request)
    return redirect('login_main')


def create_shift(request):
    
    if not request.user.is_authenticated:
        return redirect('no_auth')
    
    if not request.user.is_staff:
        return redirect('no_perm')

    if request.method == 'POST':
        form = CreateShiftForm(request.POST)

        if form.is_valid():
            field_dict = form.cleaned_data

            owner = field_dict.get('user')
            name = field_dict.get('name')
            date = field_dict.get('date')
            start_time = field_dict.get('start_time')
            end_time = field_dict.get('end_time')

            # Creation of new shifts tuple / instance
            new_shift = Shifts(
                user_id=owner.id, 
                date=date,
                start_time=start_time,
                end_time=end_time,
                name=name,
            )

            # saving instance to database
            new_shift.save()

            return redirect('success')
        else:
            print("create_shift_form invalid")

    else:
        form = CreateShiftForm()
        
    return render(request, 'cal/create_shift.html', {'form': form})


def create_shiftgroup(request):

    if not request.user.is_authenticated:
        return redirect('no_auth')

    if not request.user.is_staff:
        return redirect('no_perm')

    if request.method == 'POST':
        form = CreateShiftGroupForm(request.POST)

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

            create_shiftgroup_from_pattern(
                user_id=owner.id,
                name=name,
                start_date=start_date,
                end_date=end_date,
                start_time=start_time,
                end_time=end_time,
                repeat_on=repeat_on,
                repeat_interval=repeat_interval,
            )

            return redirect('success')
    else:
        form = CreateShiftGroupForm()

    return render(request, 'cal/create_shiftgroup.html', {'form': form})


def create_subrequest(request):
    
    if not request.user.is_authenticated:
        return redirect('no_auth')

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
            new_subrequest = SubRequests(
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

            return redirect('success')
        else:
            print("create_subrequest_form invalid")

    else:
        form = CreateSubrequestForm()
        
    return render(request, 'cal/create_subrequest.html', {'form': form})


def view_subrequest(request, sub_id=None):
    # TODO: take action on request

    if not request.user.is_authenticated or sub_id is None:
        return redirect('no_auth')

    try:
        subrequest = SubRequests.objects.get(pk=sub_id)
    except SubRequests.DoesNotExist:
        return redirect('no_exists')
    except:
        print('unknown exception raised')
        return redirect('no_perm')    

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
        actions['Delete'] = f'/calendar/declare_sub/{sub_id}'

    if request_owner.id != request.user.id and not subrequest.covered_by:
        actions['Sub for this person'] = f'/calendar/declare_sub/{sub_id}'

    if subrequest.covered_by is not None:
        if request.user.is_staff or request_owner.id == request.user.id or subrequest.covered_by.id == request.user.id:
            actions['Revoke sub decision'] = f'/calendar/revoke_sub/{sub_id}'

    if request.user.is_staff:
        actions['Approve'] = f'/calendar/approve_subrequest/{sub_id}'
    
    return render(request, 'cal/view_subrequest.html', {'info': info, 'actions': actions})



def view_shift(request, shift_id=None):

    # Convert to subrequest
    # Look at shiftgroup(s) >= 0 that this shift is part of
    # Delete shift

    if not request.user.is_authenticated or shift_id is None:
        return redirect('no_auth')

    try:
        shift = Shifts.objects.get(pk=shift_id)
    except Shifts.DoesNotExist:
        return redirect('no_exists')
    except:
        print('unknown exception raised')
        return redirect('no_perm')
        
    if shift.user_id != request.user.id and not request.user.is_staff:
        return redirect('no_perm')    

    name = shift.name
    date = shift.date
    start_time = shift.start_time
    end_time = shift.end_time

    info = {
        'Shift Name: ': name,
        'Date: ': date,
        'Start Time: ': start_time,
        'End Time: ': end_time,
    }

    actions = {}
    
    if request.user.is_staff:
        info['Owner: '] = shift.user.username
        actions['Delete'] = f'/calendar/delete_shift/{shift_id}'

    return render(request, 'cal/view_shift.html', {'info': info, 'actions': actions})
    

def delete_shift(request, shift_id=None):
    if not request.user.is_authenticated or shift_id is None:
        return redirect('no_auth')

    try:
        shift = Shifts.objects.get(pk=shift_id)
    except Shifts.DoesNotExist:
        return redirect('no_exists')
    except:
        print('unknown exception raised')
        return redirect('no_perm')
        
    if not request.user.is_staff:
        return redirect('no_perm')    

    if request.method == 'POST':
        shift.delete()
        return redirect('success')
    
    return render(request, 'cal/base_delete_view.html', {'object': shift})


def delete_subrequest(request, req_id=None):
    if not request.user.is_authenticated or req_id is None:
        return redirect('no_auth')

    try:
        req = SubRequests.objects.get(pk=req_id)
    except SubRequests.DoesNotExist:
        return redirect('no_exists')
    except:
        print('unknown exception raised')
        return redirect('no_perm')
        
    if req.user_id != request.user.id and not request.user.is_staff:
        return redirect('no_perm')    

    if request.method == 'POST':
        req.delete()
        return redirect('success')
    
    return render(request, 'cal/base_delete_view.html', {'object': req})
            

def declare_sub(request, sub_id=None):
    if not request.user.is_authenticated or sub_id is None:
        return redirect('no_auth')

    try:
        req = SubRequests.objects.get(pk=sub_id)
    except SubRequests.DoesNotExist:
        return redirect('no_exists')
    except:
        print('unknown exception raised')
        return redirect('no_perm')  

    if request.method == 'POST':
        req.covered_by = request.user
        req.approved = False
        req.save()
        return redirect('success')
    
    return render(request, 'cal/declare_sub.html', {})


def revoke_sub(request, sub_id=None):
    if not request.user.is_authenticated or sub_id is None:
        return redirect('no_auth')

    try:
        req = SubRequests.objects.get(pk=sub_id)
    except SubRequests.DoesNotExist:
        return redirect('no_exists')
    except:
        print('unknown exception raised')
        return redirect('no_perm')

    if req.covered_by is None:
        return redirect('no_exists')

    if not request.user.is_staff and req.user_id != request.user.id and req.covered_by.id != request.user.id:
        return redirect('no_perm')

    if request.method == 'POST':
        req.covered_by = None
        req.approved = False
        req.save()
        return redirect('success')
    
    return render(request, 'cal/revoke_sub.html', {})


def approve_subrequest(request, sub_id=None):
    if not request.user.is_authenticated or sub_id is None:
        return redirect('no_auth')

    if not request.user.is_staff:
        return redirect('no_perm')

    try:
        req = SubRequests.objects.get(pk=sub_id)
    except SubRequests.DoesNotExist:
        return redirect('no_exists')
    except:
        print('unknown exception raised')
        return redirect('no_perm')

    if request.method == 'POST':
        req.approved = True
        req.save()
        return redirect('success')
    
    return render(request, 'cal/approve_subrequest.html', {})


def calculate_hours(request):

    if request.method == 'POST':
        form = CalculateHoursForm(request.POST)

        if form.is_valid():
            field_dict = form.cleaned_data
            
            start_date = field_dict.get('start_date')
            end_date = field_dict.get('end_date')
            user = field_dict.get('user')

            shifts = Shifts.objects.filter(user_id=user.id, date__gte=start_date, date__lte=end_date)

            def difference_in_seconds(start_time, end_time):
                end = datetime.combine(date.today(), end_time)
                start = datetime.combine(date.today(), start_time)
                diff = end - start
                return diff.total_seconds()

            total_shift_seconds = 0
            
            for shift in shifts:
                total_shift_seconds += difference_in_seconds(shift.start_time, shift.end_time)
            
            shift_hours = int(total_shift_seconds // 3600)
            shift_leftover_minutes = int((total_shift_seconds % 3600) // 60)

            subdays = SubRequests.objects.filter(date__gte=start_date, date__lte=end_date, covered_by_id__exact=user.id)
            
            total_sub_seconds = 0

            for sub in subdays:
                total_sub_seconds += difference_in_seconds(sub.start_time, sub.end_time)

            subday_hours = int(total_sub_seconds // 3600)
            subday_leftover_minutes = int((total_sub_seconds % 3600) // 60)

            total_seconds = total_shift_seconds + total_sub_seconds
            total_hours = int(total_seconds // 3600)
            total_leftover_mimutes = int((total_seconds % 3600) // 60)


            info = {
                'Employee Shift Hours: ': str(shift_hours) + ' hours and ' + str(shift_leftover_minutes) + ' minutes.',
                'Employee Subday Hours: ': str(subday_hours) + ' hours and ' + str(subday_leftover_minutes) + ' minutes.',
                'Employee Total Hours: ': str(total_hours) + ' hours and ' + str(total_leftover_mimutes) + ' minutes.',
            }
            
            return render(request, 'cal/calculate_results.html', {'info': info})

    else:
        form = CalculateHoursForm()

    return render(request, 'cal/calculate_hours.html', {'form': form})





