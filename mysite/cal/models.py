from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=30, verbose_name='Location name', unique=True)
    address = models.CharField(max_length=100)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name

class Client(models.Model):
    name = models.CharField(max_length=30, verbose_name='Client name', unique=True)
    address = models.CharField(max_length=100)
    locations = models.ManyToManyField(Location)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name

class Shift(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(verbose_name='day of shift', name='date')
    start_time = models.TimeField(name='start_time')
    end_time = models.TimeField(name='end_time')
    name = models.CharField(verbose_name='Name of shift', max_length=30, name='name')

    #TODO
    def get_html_url(self):
        url = f'/{self.client.name}/{self.location.name}/calendar/view_shift/{self.id}'
        return f'<a class="badge badge-primary"href="{url}"> {self.name} </a>'
    
    def __str__(self):
        return self.user.first_name + self.name


class SubRequest(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_subrequest')
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
        related_name='my_subday',
    )
    
    def get_html_url(self):
        url = f'/{self.client.name}/{self.location.name}/calendar/view_subrequest/{self.id}'

        if not self.covered_by:
            return f'<a class="badge badge-danger" href="{url}"> {self.name} </a>'
        else:
            return f'<a class="badge badge-success" href="{url}"> {self.name} </a>'

    def __str__(self):
        return self.user.first_name + self.name


# class Client_Location(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE)


# class User_Location(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE)


# class User_Client(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)

