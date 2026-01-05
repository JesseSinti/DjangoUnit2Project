import uuid
from decimal import Decimal 
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
        ('Non-active', 'Non-active')
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

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_tiers')
    type = models.CharField(max_length=10,choices=Status.choices, default="Basic")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField()
    def sold_count(self):
        return self.ticket_set.count()

    def tickets_remaining(self):
        return self.quantity - self.ticket_set.count()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ticket') 
    tier = models.ForeignKey(TicketTier, on_delete=models.CASCADE)
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code_image = models.ImageField(upload_to='qr_code_img/', blank=True, null=True)
    is_used = models.BooleanField(default=False)

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def total(self):
        return sum(ticket.subtotal() for ticket in self.tickets.all())

class TicketsSaved(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='tickets')
    ticket = models.ForeignKey(TicketTier, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def subtotal(self):
        return self.ticket.price * self.quantity
    