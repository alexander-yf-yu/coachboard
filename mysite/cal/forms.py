from django import forms
from django.forms import ModelChoiceField
from datetime import time, date
from django.contrib.auth.models import User

class CreateSubrequestForm(forms.Form):
    name = forms.CharField(max_length=30)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    anonymous = forms.BooleanField(initial=True, required=False)

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if not (isinstance(start_time, time) and isinstance(end_time, time)):
                raise forms.ValidationError("Time fields must have time inputs")
            if start_time > end_time:
                raise forms.ValidationError("Start time must be before end time")

class CreateShiftsForm(forms.Form):
    # user = ModelChoiceField(queryset=User.objects.all(), to_field_name='username', label='User')
    name = forms.CharField(max_length=30, label_suffix=': (all shifts have the same name)')
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    

    repeat_interval = forms.ChoiceField(
        choices=[(1,1), (2,2), (3,3), (4,4)],
        widget=forms.Select(),
        initial='1',
        label_suffix=' in weeks:',
    )

    repeat_on = forms.MultipleChoiceField(
        choices=[
            (1, 'Monday'),
            (2, 'Tuesday'),
            (3, 'Wednesday'),
            (4, 'Thursday'),
            (5, 'Friday'),
            (6, 'Saturday'),
            (7, 'Sunday'),
        ],
        widget=forms.CheckboxSelectMultiple(),
    )

    def __init__(self, *args, **kwargs):
        client = kwargs.pop('client')
        location = kwargs.pop('location')
        super(CreateShiftsForm, self).__init__(*args, **kwargs)
        
        client_users = client.users.all()
        location_users = location.users.all()

        self.fields['user'] = ModelChoiceField(queryset=client_users.intersection(location_users), to_field_name='username', label='User')

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if not (isinstance(start_time, time) and isinstance(end_time, time)):
                raise forms.ValidationError("Time fields must have time inputs")
            if start_time > end_time:
                raise forms.ValidationError("Start time must be before end time")

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if not (isinstance(start_date, date) and isinstance(end_date, date)):
                raise forms.ValidationError("Date fields must have date inputs")
            if start_date > end_date:
                raise forms.ValidationError("Start time must be before end time")

         
class CreateShiftForm(forms.Form):
    # user = ModelChoiceField(queryset=User.objects.all(), to_field_name='username', label='User')
    name = forms.CharField(max_length=30)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    def __init__(self, *args, **kwargs):
        client = kwargs.pop('client')
        location = kwargs.pop('location')
        super(CreateShiftForm, self).__init__(*args, **kwargs)
        
        client_users = client.users.all()
        location_users = location.users.all()

        self.fields['user'] = ModelChoiceField(queryset=client_users.intersection(location_users), to_field_name='username', label='User')

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if not (isinstance(start_time, time) and isinstance(end_time, time)):
                raise forms.ValidationError("Time fields must have time inputs")
            if start_time > end_time:
                raise forms.ValidationError("Start time must be before end time")


class CalculateHoursForm(forms.Form):
    # user = ModelChoiceField(queryset=User.objects.all(), to_field_name='username', label='User:')
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Start Date (Inclusive):')
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='End Date (Inclusive):')

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if not (isinstance(start_date, date) and isinstance(end_date, date)):
                raise forms.ValidationError("Date fields must have date inputs")
            if start_date > end_date:
                raise forms.ValidationError("Start date must be before end date")
