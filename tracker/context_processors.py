from .models import Medicine, FoodItem, Notification

def notifications(request):
    if not request.user.is_authenticated:
        return {}
    # auto-create notifications for expiring/expired items (lightweight check)
    # We create missing notifications on each request (idempotent via unique check per day)
    medicines = Medicine.objects.filter(user=request.user)
    foods = FoodItem.objects.filter(user=request.user)
    # ensure notifications exist for current expiring/expired (avoid duplicates per item+status per day)
    from datetime import date
    today = date.today()
    for item in list(medicines) + list(foods):
        status = item.status
        if status in ["Expiring Soon", "Expired"]:
            level = "danger" if status == "Expired" else "warning"
            item_type = "medicine" if isinstance(item, Medicine) else "food"
            # avoid duplicate unread notification for same item+status today
            exists = Notification.objects.filter(
                user=request.user,
                item_type=item_type,
                item_id=item.pk,
                level=level,
                is_read=False,
                created_at__date=today
            ).exists()
            if not exists:
                # also check if we already have an unread for this item+level (any day) - keep one
                exists_any = Notification.objects.filter(
                    user=request.user,
                    item_type=item_type,
                    item_id=item.pk,
                    level=level,
                    is_read=False
                ).exists()
                if not exists_any:
                    title = f"{item.name} {status.lower()}" if status == "Expired" else f"{item.name} expiring in {item.days_until_expiry} days"
                    msg = f"{item_type.title()} '{item.name}' (Qty: {item.quantity}) expired on {item.expiry_date} — please check!" if status == "Expired" else f"{item_type.title()} '{item.name}' (Qty: {item.quantity}) expires on {item.expiry_date} — {item.days_until_expiry} days left!"
                    Notification.objects.create(
                        user=request.user,
                        title=title,
                        message=msg,
                        level=level,
                        item_type=item_type,
                        item_id=item.pk,
                        item_name=item.name,
                        expiry_date=item.expiry_date
                    )

    unread = Notification.objects.filter(user=request.user, is_read=False)
    return {
        'notif_unread_count': unread.count(),
        'notif_unread_list': unread[:5],
        'notif_has_critical': unread.filter(level='danger').exists(),
    }
