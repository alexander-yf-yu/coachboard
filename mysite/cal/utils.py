from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import SubRequest, Shift, Client, Location
from django.contrib.auth.models import User
import calendar

class htmlCalendar(HTMLCalendar):
    def __init__(self, user_id, client_name, location_name, year=None, month=None):
        super(htmlCalendar, self).__init__()
        
        self.user = User.objects.get(pk=user_id)
        self.client = Client.objects.get(name__iexact=str(client_name))
        self.location = Location.objects.get(name__iexact=str(location_name))

        if (year is None) and (month is None):
            t = datetime.today()
            self.year = t.year
            self.month = t.month
        else:
            self.year = year
            self.month = month

    def is_staff(self):
        return self.user.is_staff

    # formats a day as a td
    # filter SubRequests by day
    def formatday(self, day, req, shifts):

        if self.is_staff():
            shifts_per_day = shifts.filter(date__day=day)
        else:
            shifts_per_day = shifts.filter(date__day=day, user=self.user)
        
        subrequests_per_day = req.filter(date__day=day)

        d = ''

        for requests in subrequests_per_day:
            d += f'<li class="subrequest_link"> {requests.get_html_url()} </li>'

        for s in shifts_per_day:
            d += f'<li class="shift_link"> {s.get_html_url()} </li>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek, req, shifts):
        week = ''
        for d, _ in theweek:
            week += self.formatday(d, req, shifts)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter SubRequests by year and month
    def formatmonth(self, withyear=True):
        req = SubRequest.objects.filter(date__year=self.year, date__month=self.month, client=self.client, location=self.location)
        shifts = Shift.objects.filter(date__year=self.year, date__month=self.month, client=self.client, location=self.location)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'

        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, req, shifts)}\n'

        return cal

    
    def generate_staff_view(self):
        unapproved_subrequests = SubRequest.objects.filter(date__gte=datetime.today(), client=self.client, location=self.location, approved__exact=False)
        approved_subrequests = SubRequest.objects.filter(date__gte=datetime.today(), client=self.client, location=self.location, approved__exact=True)
        uncovered_subrequests = SubRequest.objects.filter(date__gte=datetime.today(), client=self.client, location=self.location, covered_by__exact=None)

        len_unapproved = len(unapproved_subrequests)
        len_unc = len(uncovered_subrequests)
        len_approved = len(approved_subrequests)

        content = '<div class="accordion" id="accordionStaffView">'

        content += '<div class="card">'
        content += f'<div class="card-header" id="headingOneStaffView"><h2 class="mb-0"><button class="btn btn-link btn-block text-left text-dark collapsed" type="button" data-toggle="collapse" data-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">Unapproved Subrequests <span class="badge badge-secondary"> {len_unapproved}</span></button></h2></div>'
        content += '<div id="collapseOne" class="collapse" aria-labelledby="headingOneStaffView" data-parent="#accordionStaffView"><div class="card-body">'
        for req in unapproved_subrequests:
            content += f'<li class="unapproved">{req.get_html_url()}</li>'      
        content += '</div></div></div>'

        content += '<div class="card">'
        content += f'<div class="card-header" id="headingThreeStaffView"><h2 class="mb-0"><button class="btn btn-link btn-block text-left text-dark collapsed" type="button" data-toggle="collapse" data-target="#collapseThree" aria-expanded="true" aria-controls="collapseThree">Uncovered Subrequests <span class="badge badge-secondary"> {len_unc}</span></button></h2></div>'
        content += '<div id="collapseThree" class="collapse" aria-labelledby="headingThreeStaffView" data-parent="#accordionStaffView"><div class="card-body">'
        for day in uncovered_subrequests:
            content += f'<li class="uncovered_subdays">{day.get_html_url()}</li>'
        content += '</div></div></div>'
        
        content += '<div class="card">'
        content += f'<div class="card-header" id="headingTwoStaffView"><h2 class="mb-0"><button class="btn btn-link btn-block text-left text-dark collapsed" type="button" data-toggle="collapse" data-target="#collapseTwo" aria-expanded="true" aria-controls="collapseTwo">Approved Subrequests <span class="badge badge-secondary"> {len_approved}</span></button></h2></div>'
        content += '<div id="collapseTwo" class="collapse" aria-labelledby="headingTwoStaffView" data-parent="#accordionStaffView"><div class="card-body">'
        for req in approved_subrequests:
            content += f'<li class="approved">{req.get_html_url()}</li>'
        content += '</div></div></div>'

        content += '</div>'

        return f'<div class="container">{content}</div>' 


    def generate_notifications(self):
        your_subrequests = SubRequest.objects.filter(date__gte=datetime.today(), client=self.client, location=self.location, user=self.user)
        your_subdays = SubRequest.objects.filter(date__gte=datetime.today(), client=self.client, location=self.location, covered_by=self.user)
        uncovered_subrequests = SubRequest.objects.filter(date__gte=datetime.today(), client=self.client, location=self.location, covered_by__exact=None)

        len_req = len(your_subrequests)
        len_days = len(your_subdays)
        len_unc = len(uncovered_subrequests)

        content = '<div class="accordion" id="accordionNotifications">'

        content += '<div class="card">'
        content += f'<div class="card-header" id="headingOneNotifications"><h2 class="mb-0"><button class="btn btn-link btn-block text-left text-dark collapsed" type="button" data-toggle="collapse" data-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">Uncovered Subrequests <span class="badge badge-secondary"> {len_unc}</span></button></h2></div>'
        content += '<div id="collapseOne" class="collapse" aria-labelledby="headingOneNotifications" data-parent="#accordionNotifications"><div class="card-body">'
        for day in uncovered_subrequests:
            content += f'<li class="uncovered_subdays">{day.get_html_url()}</li>'        
        content += '</div></div></div>'

        content += '<div class="card">'
        content += f'<div class="card-header" id="headingTwoNotifications"><h2 class="mb-0"><button class="btn btn-link btn-block text-left text-dark collapsed" type="button" data-toggle="collapse" data-target="#collapseTwo" aria-expanded="true" aria-controls="collapseTwo">Your Subdays <span class="badge badge-secondary"> {len_days}</span></button></h2></div>'
        content += '<div id="collapseTwo" class="collapse" aria-labelledby="headingTwoNotifications" data-parent="#accordionNotifications"><div class="card-body">'
        for day in your_subdays:
            content += f'<li class="your_pending_subdays">{day.get_html_url()}</li>'       
        content += '</div></div></div>'

        content += '<div class="card">'
        content += f'<div class="card-header" id="headingThreeNotifications"><h2 class="mb-0"><button class="btn btn-link btn-block text-left text-dark collapsed" type="button" data-toggle="collapse" data-target="#collapseThree" aria-expanded="true" aria-controls="collapseThree">Your Subrequests <span class="badge badge-secondary"> {len_req}</span></button></h2></div>'
        content += '<div id="collapseThree" class="collapse" aria-labelledby="headingThreeNotifications" data-parent="#accordionNotifications"><div class="card-body">'
        for req in your_subrequests:
            content += f'<li class="your_pending_subreq">{req.get_html_url()}</li>'      
        content += '</div></div></div>'
        
        content += '</div>'

        return f'<div class="container">{content}</div>' 


def prev_month(year, month):
    first = datetime(year=year, month=month, day=1)
    prev_month = first - timedelta(days=1)
    return str(prev_month.year) + '/' + str(prev_month.month)


def next_month(year, month):
    days_in_month = calendar.monthrange(year, month)[1]
    last = datetime(year=year, month=month, day=days_in_month)
    next_month = last + timedelta(days=1)
    return str(next_month.year) + '/' + str(next_month.month)


def create_shifts_from_pattern(client, location, user_id, name, start_date, end_date, start_time, end_time, repeat_on, repeat_interval):

    curr = start_date
    loop_end = end_date + timedelta(days=1)
    week_count = 0

    while curr < loop_end:
        weekday = str(curr.isoweekday())

        if weekday in repeat_on and week_count == 0:

            shift = Shift(
                client=client,
                location=location,
                user_id=user_id,
                name=name,
                date=curr,
                start_time=start_time,
                end_time=end_time,
            )

            shift.save()

        if week_count == 0 and weekday == '7':
            week_count = int(repeat_interval)

        if weekday == '7':
            week_count -= 1

        curr = curr + timedelta(days=1)  
