from django.contrib import admin

# Register your models here.

from .models import Shift, SubRequest

admin.site.register(Shift)
admin.site.register(SubRequest)
