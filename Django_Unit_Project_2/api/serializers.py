from rest_framework import serializers
from App.models import *

class OrganizationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id','name','created_at']
        
    def create(self, validated_data):
        org, created = Organization.objects.get_or_create(
            name=validated_data['name'],
            defaults=validated_data
        )
        return org

class EventSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializers(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset = Organization.objects.all(),
        source = 'organization',
        write_only = True
    )
    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'banner_image',
            'location',
            'date',
            'start_time',
            'end_time',
            'capacity',
            'organization',
            'organization_id'
        ]

class TicketTierSerializer(serializers.ModelSerializer):
    tickets_remaining = serializers.SerializerMethodField()

    class Meta:
        model = TicketTier
        fields = ['id',
                  'type',
                  'price',
                  'quantity',
                  'tickets_remaining',
                  'event'
                  ]
        
    def get_tickets_remaining(self, obj):
        return obj.tickets_remaining()
    
class EventDetailSerializer(serializers.ModelSerializer):
    ticket_tiers = TicketTierSerializer(many=True, read_only=True)

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['ticket_tiers']