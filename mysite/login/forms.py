from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    name_with_initial = forms.CharField(
        label='First name with last initial',
        max_length=20,
        required=True,
    )

    class Meta:
        model = User
        fields = ['name_with_initial', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        p1 = self.fields.get('password1')
        p1.label_suffix = ' (temporary):'
 

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["name_with_initial"]
        if commit:
            user.save()
        return user
