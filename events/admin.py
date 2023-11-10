from django.contrib import admin
from .models import Event, Club, customuser, Registration

# Register your models here.
admin.site.register(Event)
admin.site.register(Club)
admin.site.register(customuser)
admin.site.register(Registration)
