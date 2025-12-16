import django_filters
from .models import *

class EventFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name='tickettier__price',
        lookup_expr='gte'
    )
    max_price = django_filters.NumberFilter(
        field_name='tickettier__price',
        lookup_expr='lte'
    )
    location = django_filters.CharFilter(
        field_name='location',
        lookup_expr='icontains'
    )

    start_time = django_filters.TimeFilter(
        field_name='start_time',
        input_formats=['%H:%M',
        '%H:%M:%S',     
        '%I:%M %p',     
        '%I:%M:%S %p'],
        lookup_expr='exact'
    )

    organizer = django_filters.CharFilter(
        field_name='organizer__username',
        lookup_expr='icontains'
    )

    class Meta:
        model = Event
        fields = ['location', 'start_time' ]

class MembersFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name="user__username", lookup_expr='icontains')

    class Meta:
        model = OrganizationMembership
        fields = ['username']