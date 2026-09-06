from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tracker.models import Medicine, FoodItem
from tracker.email_utils import send_expiry_email
from tracker.models import Notification

class Command(BaseCommand):
    help = "Check all users' medicines & foods for expiring/expired items, create notifications and send email summaries. Run daily via cron."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be sent without sending emails')
        parser.add_argument('--user', type=str, help='Only check this username')

    def handle(self, *args, **options):
        dry = options['dry_run']
        username = options['user']
        users = User.objects.filter(username=username) if username else User.objects.all()
        total_emails = 0
        for user in users:
            if not user.email:
                self.stdout.write(f"SKIP {user.username}: no email set")
                continue
            medicines = Medicine.objects.filter(user=user)
            foods = FoodItem.objects.filter(user=user)
            critical = [i for i in list(medicines) + list(foods) if i.status in ["Expiring Soon","Expired"]]
            if not critical:
                self.stdout.write(f"OK {user.username}: no critical items")
                continue
            # Create missing notifications (idempotent)
            for item in critical:
                item_type = "medicine" if isinstance(item, Medicine) else "food"
                level = "danger" if item.status == "Expired" else "warning"
                if not Notification.objects.filter(user=user, item_type=item_type, item_id=item.pk, level=level, is_read=False).exists():
                    title = f"{item.name} expired!" if item.status=="Expired" else f"{item.name} expiring in {item.days_until_expiry} days"
                    msg = f"{item_type.title()} '{item.name}' Qty:{item.quantity} — {item.status} on {item.expiry_date}"
                    Notification.objects.create(user=user, title=title, message=msg, level=level, item_type=item_type, item_id=item.pk, item_name=item.name, expiry_date=item.expiry_date)

            if dry:
                self.stdout.write(f"DRY {user.username} ({user.email}): would send email for {len(critical)} items: " + ", ".join([f"{i.name}({i.status})" for i in critical]))
            else:
                try:
                    sent = send_expiry_email(user, critical, mode="summary")
                    if sent:
                        total_emails += 1
                        self.stdout.write(self.style.SUCCESS(f"EMAIL {user.username} ({user.email}): {len(critical)} items — " + ", ".join([i.name for i in critical])))
                    else:
                        self.stdout.write(f"SKIP {user.username}: email not sent")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"FAIL {user.username}: {e}"))
        self.stdout.write(self.style.SUCCESS(f"Done. Emails sent: {total_emails} (dry_run={dry})"))
        self.stdout.write("Tip: console backend prints emails to terminal. For real SMTP, set EMAIL_BACKEND, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD in env.")
