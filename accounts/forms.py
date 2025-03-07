from django.forms import ModelForm, Textarea, ModelChoiceField, formset_factory
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django_filters.filters import MultipleChoiceFilter
from .models import *

class LogForm(ModelForm):
    class Meta:
        model = Log
        #fields = '__all__'
        fields = ['ticket_Number', 'source', 'site', 'services','troubleshoot_Required',  'notes', 'status', 'resolution', 'secure_Plus_Checker']
        #exclude = ['employee', 'dateCreated', 'clock']
        widgets = {
            'notes': Textarea(attrs={'cols': 80, 'rows': 8}),
        }
    def __init__(self, *args, **kwargs):
        super(LogForm, self).__init__(*args, **kwargs)
        self.fields['site'].required = False
        self.fields['services'].required = False
        self.fields['notes'].required = False
        self.fields['status'].required = False
        self.fields['resolution'].required = False
        self.fields['troubleshoot_Required'].required = False
        self.fields['secure_Plus_Checker'].required = False

class ListSelect(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()

class ListForm(forms.Form):
    employee = ListSelect(queryset=User.objects.all(), empty_label="Choose an Employee")

ListFormSet = formset_factory(ListForm)

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['full_Name']