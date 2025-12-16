from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.

class User(AbstractUser):
    is_customer = models.BooleanField(default=False)

    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class OrganizationMembership(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Organization Admin'),
        ('user', 'Organization User'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('kicked', 'Kicked'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"


class Event(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    banner_image = models.ImageField(upload_to='event_images/')
    location = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.organization.name}"


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event =  models.ForeignKey(Event, on_delete=models.CASCADE)
    total_price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE) 
    tier = models.ForeignKey(TicketTier, on_delete=models.CASCADE)
    ticket_id = models.IntegerField(unique=True)
    qr_code_image = models.ImageField(upload_to='qr_code_img/', blank=True, null=True)
    is_used = models.BooleanField(default=False)
    