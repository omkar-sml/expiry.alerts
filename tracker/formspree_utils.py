import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_via_formspree(to_email, subject, message, reply_to=None, extra_fields=None):
    """
    Send an email via Formspree endpoint as HTTP POST fallback (no SMTP needed).
    Works like: POST https://formspree.io/f/xeaqlvwp  {email, _subject, message}
    Returns True if Formspree accepted (200), else False.
    Note: Free Formspree requires verifying the form first via email click — check form owner inbox after first submit.
    """
    endpoint = getattr(settings, 'FORMSPREE_ENDPOINT', 'https://formspree.io/f/xeaqlvwp')
    if not getattr(settings, 'FORMSPREE_ENABLED', True):
        return False
    if not endpoint or 'formspree.io' not in endpoint:
        return False
    data = {
        'email': to_email,
        '_subject': subject,
        'message': message,
        '_replyto': reply_to or to_email,
    }
    if extra_fields:
        data.update(extra_fields)
    try:
        # Formspree expects form-encoded, not JSON, for direct endpoint
        resp = requests.post(endpoint, data=data, headers={'Accept': 'application/json'}, timeout=10)
        if resp.status_code in (200, 201):
            logger.info(f"Formspree sent to {to_email}: {resp.json()}")
            return True
        else:
            logger.warning(f"Formspree failed {resp.status_code}: {resp.text[:500]}")
            return False
    except Exception as e:
        logger.warning(f"Formspree exception: {e}")
        return False
