from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# --- NEW CUSTOM USER MODEL ---
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        PHARMACIST = "PHARMACIST", "Pharmacist"
        DONOR = "DONOR", "Donor"
        PATIENT = "PATIENT", "Patient"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    license_number = models.CharField(max_length=50, blank=True, null=True) # Only for Pharmacists
    phone = models.CharField(max_length=15, blank=True)

# --- UPDATED MEDICINE MODEL ---
class Medicine(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified & Available'),
        ('rejected', 'Rejected'),
    ]

    # Change User to 'myapp.User' to point to your custom model
    donor = models.ForeignKey('myapp.User', on_delete=models.CASCADE, related_name='donations')
    name = models.CharField(max_length=255)
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    resale_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    is_physical_intact = models.BooleanField(default=False)
    is_authentic = models.BooleanField(default=False)
    is_expiry_valid = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    qr_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        self.resale_price = float(self.original_price) * 0.30
        if self.is_physical_intact and self.is_authentic and self.is_expiry_valid:
            self.status = 'verified'
        super().save(*args, **kwargs)

class ReMediCorner(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100, default="Feni") # Useful for filtering
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __cl__str__(self):
        return f"{self.name} ({self.city})"        