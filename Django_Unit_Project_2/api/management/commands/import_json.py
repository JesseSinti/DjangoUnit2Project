import json
from api.serializers import *
from App.models import *
from django.core.management.base import BaseCommand
from django.core.files import File
import os 

# sets the path for default image to be added
default_banner_path = os.path.join(settings.BASE_DIR, 'media/event_images/default_eventimage.png')

class Command(BaseCommand):
    help = 'Import organizations, events, and ticket tiers from JSON'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']

        with open(json_file, 'r') as f:
            data = json.load(f)
# This specifies that all information regarding the organizations goes to the organization serializer only 
        orgs_data = data.get('organizations', [])
        org_serializer = OrganizationSerializers(data=orgs_data, many=True)
        if org_serializer.is_valid():
            # saves the data onces its succesful
            org_serializer.save()
            # tells which one was saved and successful
            self.stdout.write(self.style.SUCCESS(f"Saved {len(orgs_data)} organizations"))
        else:
            # tells which ones weren't valid and errored
            self.stdout.write(self.style.ERROR(f"Organizationerrors: {org_serializer.errors}"))
        
# sends all data regarding events to the event serializer so it can convert the data
        events_data = data.get('events', [])

        for event in events_data:
            banner_file = None
            if not event.get('banner_image'):
                f = open(default_banner_path, 'rb')
                banner_file = File(f, name='default_eventimage.png')

            
            event_data = event.copy()
            event_data.pop('banner_image', None)

            serializer = EventSerializer(data=event_data)
            if serializer.is_valid():
                instance = serializer.save()
                if banner_file:
                    instance.banner_image.save(banner_file.name, banner_file, save=True)
                    f.close()  
                self.stdout.write(self.style.SUCCESS(f"Saved event: {instance.title}"))
            else:
                self.stdout.write(self.style.ERROR(f"Event Errors: {serializer.errors}"))

# sends all tickettier data to the ticket tier serializer to convert
        ticket_data = data.get('ticket_tiers', [])
        for ticket in ticket_data:
            try:
                event_obj = Event.objects.get(id=ticket.pop('event_id'))
                ticket['event'] = event_obj.id

            except Event.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Event not found for ticket: {ticket}"))
                continue

        ticket_serializer = TicketTierSerializer(data=ticket_data, many=True)
        if ticket_serializer.is_valid():
            ticket_serializer.save()
            self.stdout.write(self.style.SUCCESS(f"Saved {len(ticket_data)} ticket tiers"))     
        else:
            self.stdout.write(self.style.ERROR(f"ticketTier errorsL {ticket_serializer.errors}"))   