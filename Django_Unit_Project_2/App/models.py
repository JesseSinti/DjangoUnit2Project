from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class OrganizationUsers(models.Model):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.IntegerField()
    is_admin = models.BooleanField(default=True)
    organization_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)

class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    banner_image = models.ImageField(upload_to='event_images/')
    location = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class TicketTier(models.Model):

    class Status(models.TextChoices):
        VIP = "VIP",('VIP')
        GENERAL = "General",('General')
        BASIC = "Basic",('Basic')

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    type = models.CharField(max_length=10,choices=Status.choices, default="Basic")
    price = models.FloatField()
    quantity = models.IntegerField()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event =  models.ForeignKey(Event, on_delete=models.CASCADE)
    total_price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    tier = models.ForeignKey(TicketTier, on_delete=models.CASCADE)
    ticket_id = models.IntegerField(unique=True)
    qr_code_image = models.ImageField(upload_to='qr_code_img/', blank=True, null=True)
    is_used = models.BooleanField(default=False)
    