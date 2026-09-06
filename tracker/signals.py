from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Medicine, FoodItem, Notification, Profile

def create_notification_if_needed(instance, item_type):
    status = instance.status
    if status not in ["Expiring Soon", "Expired"]:
        return
    level = "danger" if status == "Expired" else "warning"
    if Notification.objects.filter(user=instance.user, item_type=item_type, item_id=instance.pk, level=level, is_read=False).exists():
        return
    title = f"{instance.name} expired!" if status == "Expired" else f"{instance.name} expiring in {instance.days_until_expiry} days"
    msg = f"{item_type.title()} '{instance.name}' (Qty: {instance.quantity}) expired on {instance.expiry_date}." if status == "Expired" else f"{item_type.title()} '{instance.name}' (Qty: {instance.quantity}) expires on {instance.expiry_date} — {instance.days_until_expiry} days left!"
    Notification.objects.create(
        user=instance.user,
        title=title,
        message=msg,
        level=level,
        item_type=item_type,
        item_id=instance.pk,
        item_name=instance.name,
        expiry_date=instance.expiry_date
    )
    # Email removed — offline app uses in-app + phone notification only

@receiver(post_save, sender=Medicine)
def medicine_post_save(sender, instance, created, **kwargs):
    create_notification_if_needed(instance, "medicine")

@receiver(post_save, sender=FoodItem)
def food_post_save(sender, instance, created, **kwargs):
    create_notification_if_needed(instance, "food")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
