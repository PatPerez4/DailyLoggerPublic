from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Log)
admin.site.register(Employee)
admin.site.register(Day)
