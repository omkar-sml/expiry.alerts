from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random

class Medicine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(help_text="e.g. 10 tablets / 2 bottles")
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['expiry_date']
        verbose_name = "Medicine"
        verbose_name_plural = "Medicines"

    def __str__(self):
        return f"{self.name} ({self.expiry_date})"

    @property
    def days_until_expiry(self):
        return (self.expiry_date - date.today()).days

    @property
    def status(self):
        """Return Safe / Expiring Soon / Expired"""
        days = self.days_until_expiry
        if days < 0:
            return "Expired"
        elif days <= 7:
            return "Expiring Soon"
        else:
            return "Safe"

    @property
    def status_color(self):
        mapping = {
            "Safe": "success",
            "Expiring Soon": "warning",
            "Expired": "danger",
        }
        return mapping.get(self.status, "secondary")

    @property
    def status_badge(self):
        mapping = {
            "Safe": "bg-success",
            "Expiring Soon": "bg-warning text-dark",
            "Expired": "bg-danger",
        }
        return mapping.get(self.status, "bg-secondary")


class FoodItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(help_text="e.g. 2 kg / 5 packets")
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['expiry_date']
        verbose_name = "Food Item"
        verbose_name_plural = "Food Items"

    def __str__(self):
        return f"{self.name} ({self.expiry_date})"

    @property
    def days_until_expiry(self):
        return (self.expiry_date - date.today()).days

    @property
    def status(self):
        days = self.days_until_expiry
        if days < 0:
            return "Expired"
        elif days <= 7:
            return "Expiring Soon"
        else:
            return "Safe"

    @property
    def status_color(self):
        mapping = {
            "Safe": "success",
            "Expiring Soon": "warning",
            "Expired": "danger",
        }
        return mapping.get(self.status, "secondary")

    @property
    def status_badge(self):
        mapping = {
            "Safe": "bg-success",
            "Expiring Soon": "bg-warning text-dark",
            "Expired": "bg-danger",
        }
        return mapping.get(self.status, "bg-secondary")


class Notification(models.Model):
    """Notification for expiring/expired items"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=[('warning','Warning'),('danger','Danger'),('info','Info')], default='warning')
    item_type = models.CharField(max_length=20, choices=[('medicine','Medicine'),('food','Food')], blank=True)
    item_id = models.IntegerField(null=True, blank=True)
    item_name = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    # store the verified email snapshot
    verified_email = models.EmailField(blank=True)

    def __str__(self):
        return f"Profile {self.user.username} verified={self.is_email_verified}"


class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_otps')
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP {self.otp} for {self.email} ({self.user.username})"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()

    @classmethod
    def generate_otp(cls):
        return f"{random.randint(100000, 999999)}"
