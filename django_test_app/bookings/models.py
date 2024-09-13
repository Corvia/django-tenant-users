from django.db import models


# Create your models here.
class Booking(models.Model):
    """Test Tenant object."""

    booking_agent_name = models.CharField(max_length=64)
    booking_description = models.TextField()
    booking_type = models.CharField(max_length=100)
    booking_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.booking_agent_name
