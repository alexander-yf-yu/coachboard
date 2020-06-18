from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Shifts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shifts')
    date = models.DateField(verbose_name='day of shift', name='date')
    start_time = models.TimeField(name='start_time')
    end_time = models.TimeField(name='end_time')
    name = models.CharField(verbose_name='Name of shift', max_length=30, name='name')

    def get_html_url(self):
        url = '/calendar/view_shift/' + str(self.id)
        return f'<a class="badge badge-primary"href="{url}"> {self.name} </a>'


class ShiftGroups(models.Model):
    name = models.CharField(max_length=30, verbose_name='Shift group name', name='name')


class ShiftGrouper(models.Model):
    shift = models.ForeignKey(Shifts, on_delete=models.CASCADE, related_name='shiftgrouper')
    group = models.ForeignKey(ShiftGroups, on_delete=models.CASCADE, related_name='shiftgrouper')


class SubRequests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subrequest_user_id')
    date = models.DateField(verbose_name='day of subrequest', name='date')
    start_time = models.TimeField(name='start_time')
    end_time = models.TimeField(name='end_time')
    anonymous = models.BooleanField(name='anonymous', blank=True, default=True, verbose_name='Whether or not you want your request to be anonymous')

    name = models.CharField(
        verbose_name='The name for the Subrequest',
        name='name',
        max_length=50,
    )

    approved = models.BooleanField(
        verbose_name="Whether or not the subrequest has been approved",
        name='approved',
        default=False,
    )

    covered_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        name='covered_by',
        related_name='subrequest_covered_by',
    )
    
    def get_html_url(self):
        url = '/calendar/view_subrequest/' + str(self.id)

        if not self.covered_by:
            return f'<a class="badge badge-danger" href="{url}"> {self.name} </a>'
        else:
            return f'<a class="badge badge-success" href="{url}"> {self.name} </a>'


# class SubDays(models.Model):
#     pass