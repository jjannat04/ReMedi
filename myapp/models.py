from django.db import models
from django.contrib.auth.models import User
import uuid

class Medicine(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified & Available'),
        ('rejected', 'Rejected'),
    ]

    # Core Info
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    name = models.CharField(max_length=255)
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    resale_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # The Triple-Check Audit (Crucial for the 'Market Trust' concern)
    is_physical_intact = models.BooleanField(default=False, verbose_name="Packaging Intact?")
    is_authentic = models.BooleanField(default=False, verbose_name="Authenticity Verified?")
    is_expiry_valid = models.BooleanField(default=False, verbose_name="Expiry Date Clear?")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    qr_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        # Mechanical necessity: Automatic 70% discount for ReMedi
        self.resale_price = float(self.original_price) * 0.30
        
        # Logic: Only move to verified if all 3 checks are passed
        if self.is_physical_intact and self.is_authentic and self.is_expiry_valid:
            self.status = 'verified'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.status})"