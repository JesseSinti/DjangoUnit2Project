from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Customer(models.Model):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.IntegerField()
    is_admin = models.BooleanField(default=True)
    organization_name = models.CharField(max_length=150)

class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    banner_image = models.ImageField(upload_to='event_images/', required=True)
    location = models.CharField(max_length=100)
    