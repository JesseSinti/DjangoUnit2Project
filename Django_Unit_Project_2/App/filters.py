import django_filters
from .models import *

class TicketFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='min_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='max_price', lookup_expr='lte')
    location = django_filters.CharFilter(field_name="location", lookup_expr='icontains')
    start_time = django_filters.TimeFilter(field_name='start_time', lookup_expr='exact')

    class Meta:
        fields = ['tickettier__min_price', 'ticketier__max_price', 'event__start_time', 'event__location' ]