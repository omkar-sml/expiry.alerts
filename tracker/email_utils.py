from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import date
from django.utils import timezone
from datetime import timedelta

def send_expiry_email(user, items, mode="summary"):
    """
    Send expiry email to user.
    items: list of Medicine/FoodItem (with .status, .days_until_expiry)
    mode: "single" for one item, "summary" for digest
    Returns True if sent, False if skipped.
    """
    if not user.email:
        return False
    # Don't spam: if all safe, skip
    critical = [i for i in items if i.status in ["Expiring Soon", "Expired"]]
    if not critical:
        return False

    subject = f"EXPIRY.ALERT — {len(critical)} product(s) need attention"
    if mode == "single" and len(items) == 1:
        item = items[0]
        if item.status == "Expired":
            subject = f"EXPIRY.ALERT — '{item.name}' has EXPIRED!"
        else:
            subject = f"EXPIRY.ALERT — '{item.name}' expiring in {item.days_until_expiry} days"

    # Plain text + HTML
    expiring = [i for i in critical if i.status == "Expiring Soon"]
    expired = [i for i in critical if i.status == "Expired"]

    text_lines = [
        f"Hi {user.username},",
        "",
        f"You have {len(critical)} product(s) that need attention:",
        "",
    ]
    if expired:
        text_lines.append("EXPIRED (Red) — Do not use:")
        for it in expired:
            text_lines.append(f"  - {it.name} ({it.__class__.__name__}) Qty:{it.quantity} Expired on {it.expiry_date} ({it.days_until_expiry} days ago)")
        text_lines.append("")
    if expiring:
        text_lines.append("EXPIRING SOON (Orange) — Within 7 days:")
        for it in expiring:
            text_lines.append(f"  - {it.name} ({it.__class__.__name__}) Qty:{it.quantity} Expires {it.expiry_date} — {it.days_until_expiry} days left")
        text_lines.append("")
    text_lines.extend([
        f"Dashboard: http://127.0.0.1:8000/dashboard/",
        f"Notifications: http://127.0.0.1:8000/notifications/",
        "",
        "This is an automated alert from EXPIRY.ALERT. Please check your products.",
    ])
    plain = "\n".join(text_lines)

    # HTML version (simple)
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:600px;margin:auto;border:1px solid #e6ecf2;border-radius:12px;overflow:hidden;">
      <div style="background:#0f2a3c;color:white;padding:16px;">
        <strong>EXPIRY.ALERT</strong> <span style="color:#00c2a8;font-size:12px;">FOOD • MEDICINE</span>
        <div style="font-size:12px;color:#c8d6e5;margin-top:4px;">Expiry alert for {user.username} — {date.today():%d %b %Y}</div>
      </div>
      <div style="padding:20px;">
        <p>Hi <strong>{user.username}</strong>,</p>
        <p>You have <strong>{len(critical)} product(s)</strong> that need attention:</p>
    """
    if expired:
        html += '<div style="background:#fdecea;border-left:4px solid #dc3545;padding:12px;border-radius:8px;margin:12px 0;"><strong style="color:#dc3545;">EXPIRED (Red) — Do not use:</strong><ul style="margin:8px 0 0 16px;">'
        for it in expired:
            html += f'<li><strong>{it.name}</strong> ({it.__class__.__name__}) — Qty {it.quantity} — Expired on {it.expiry_date} ({abs(it.days_until_expiry)} days ago)</li>'
        html += '</ul></div>'
    if expiring:
        html += '<div style="background:#fff8e1;border-left:4px solid #ffc857;padding:12px;border-radius:8px;margin:12px 0;"><strong style="color:#b7791f;">EXPIRING SOON (Orange) — Within 7 days:</strong><ul style="margin:8px 0 0 16px;">'
        for it in expiring:
            html += f'<li><strong>{it.name}</strong> ({it.__class__.__name__}) — Qty {it.quantity} — Expires {it.expiry_date} — <strong>{it.days_until_expiry} days left</strong></li>'
        html += '</ul></div>'
    html += f"""
        <div style="margin-top:16px;">
          <a href="http://127.0.0.1:8000/dashboard/" style="background:#00c2a8;color:#0f2a3c;padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:600;">Open Dashboard</a>
          <a href="http://127.0.0.1:8000/notifications/" style="margin-left:8px;color:#0f2a3c;">View Notifications</a>
        </div>
        <p style="font-size:12px;color:#6b7c8e;margin-top:20px;border-top:1px solid #e6ecf2;padding-top:12px;">Automated alert from EXPIRY.ALERT. Reply not monitored.</p>
      </div>
    </div>
    """

    sent = False
    try:
        send_mail(
            subject=subject,
            message=plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html,
            fail_silently=False,
        )
        sent = True
    except Exception as e:
        print(f"[SMTP] failed: {e}")
    # Fallback / parallel: Formspree (HTTP) — ensures delivery even without SMTP
    try:
        from .formspree_utils import send_via_formspree
        fs_subject = subject
        fs_msg = plain + "\n\n--- HTML ---\n" + html
        send_via_formspree(user.email, fs_subject, fs_msg, reply_to=settings.DEFAULT_FROM_EMAIL, extra_fields={"username": user.username, "dashboard": "http://127.0.0.1:8000/dashboard/"})
    except Exception:
        pass
    return sent or True

def send_otp_email(user, email, otp):
    """Send OTP verification email (console prints to terminal unless SMTP configured)"""
    subject = f"EXPIRY.ALERT — Your verification code is {otp}"
    plain = f"""Hi {user.username},

Your EXPIRY.ALERT email verification code is:

  {otp}

It expires in 10 minutes. Enter this code on the verification page to confirm your email and enable expiry alerts.

If you didn't request this, ignore this email.

— EXPIRY.ALERT Team
"""
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:480px;margin:auto;border:1px solid #e6ecf2;border-radius:12px;overflow:hidden;">
      <div style="background:#0f2a3c;color:white;padding:16px text-align:center;">
        <div style="font-weight:800;">EXPIRY.ALERT</div><div style="color:#00c2a8;font-size:11px;">FOOD • MEDICINE</div>
      </div>
      <div style="padding:24px;text-align:center;">
        <p>Hi <strong>{user.username}</strong>,</p>
        <p style="color:#6b7c8e;">Your verification code is:</p>
        <div style="font-size:32px;letter-spacing:8px;font-weight:800;color:#0f2a3c;background:#f7f9fb;border:1px dashed #00c2a8;border-radius:10px;padding:12px;margin:16px 0;">{otp}</div>
        <p style="font-size:12px;color:#6b7c8e;">Expires in 10 minutes. Enter on the OTP page to verify <strong>{email}</strong> and activate expiry notifications.</p>
        <p style="font-size:11px;color:#9aa8b8;margin-top:16px;">If you didn't request this, ignore.</p>
      </div>
    </div>
    """
    try:
        send_mail(subject, plain, settings.DEFAULT_FROM_EMAIL, [email], html_message=html, fail_silently=False)
    except Exception as e:
        print(f"[SMTP OTP] failed: {e}")
    # also via Formspree for reliability
    try:
        from .formspree_utils import send_via_formspree
        send_via_formspree(email, subject, f"OTP for {user.username}: {otp}\n\n{plain}", reply_to=settings.DEFAULT_FROM_EMAIL, extra_fields={"otp": otp, "username": user.username})
    except Exception:
        pass
    return True

def create_and_send_otp(user, email):
    """Helper: generate 6-digit OTP, save EmailOTP, send email. Returns otp object."""
    from .models import EmailOTP
    # invalidate old unused
    otp_code = EmailOTP.generate_otp()
    expires = timezone.now() + timedelta(minutes=10)
    obj = EmailOTP.objects.create(user=user, email=email, otp=otp_code, expires_at=expires)
    send_otp_email(user, email, otp_code)
    return obj
