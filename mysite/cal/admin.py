from django.contrib import admin

# Register your models here.

from .models import Shifts, ShiftGroups, ShiftGrouper, SubRequests

admin.site.register(Shifts)
admin.site.register(ShiftGroups)
admin.site.register(SubRequests)
