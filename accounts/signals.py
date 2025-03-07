from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Employee

def employee_profile(sender, instance, created, **kwargs):
    if created:

        Employee.objects.create(
            username=instance,
            full_Name=instance.get_full_name(),
        )

post_save.connect(employee_profile, sender=User)