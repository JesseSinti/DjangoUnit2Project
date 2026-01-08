from rest_framework import serializers
from App.models import *

# Converts json data to data for the organization model and adds it to the models
# if it passes the checks
class OrganizationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id','name','created_at']
        
# Converts json data to data for the event model if it passes checks
class EventSerializer(serializers.ModelSerializer):
    # reads the data from the organizaitons (read only specifies it to only read the data not store it)
    organization = OrganizationSerializers(read_only=True)
    # collects all the ids in the Organization model and checks the data the serializer got as the source
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


# converts the json data to data that can be added to the TicketTier Model
# as long as it passes all the checks
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

# converts the json data for the events and includes the data from each events tickettiers too
class EventDetailSerializer(serializers.ModelSerializer):
    ticket_tiers = TicketTierSerializer(many=True, read_only=True)

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['ticket_tiers']