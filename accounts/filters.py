import django_filters
from django_filters import DateFilter, CharFilter
from .models import *

class LogFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="dateCreated", lookup_expr='gte')
    end_date = DateFilter(field_name="dateCreated", lookup_expr='lte')
    employee = CharFilter(field_name='employee', lookup_expr='icontains')
    ticket_Number = CharFilter(field_name='ticket_Number', lookup_expr='icontains')

    class Meta:
        model = Log
        fields = '__all__'
        exclude = ['cognito_Number', 'troubleshoot_Required', 'status', 'clock', 'notes', 'resolution', 'dateCreated']
        order_by_field = 'dateCreated'
        order_by = ('dateCreated',)

class DdtFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="dateCreated", lookup_expr='gte')
    end_date = DateFilter(field_name="dateCreated", lookup_expr='lte')
    class Meta:
        model = Ddt
        fields = '__all__'
        order_by_field = 'dateCreated'
        order_by = ('dateCreated',)