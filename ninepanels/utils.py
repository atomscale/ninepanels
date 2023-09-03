import hashlib
import os
import requests

from . import errors
from . import config


def instance_to_dict(instance):
    _dict = {}
    for key in instance.__mapper__.c.keys():
        _dict[key] = getattr(instance, key)
    return _dict


def generate_random_hash() -> str:
    """Generate a random hash

    Returns
        hash: 64 character hexademcial string

    """

    random_bytes = os.urandom(32)
    hash_bytes = hashlib.sha256(random_bytes)
    hash = hash_bytes.hexdigest()

    return hash


def dispatch_password_reset_email(
    recipient_email: str, recipient_name: str, url: str
) -> bool:
    """send email using mail provider api



    on success message respond with True, else False
    """
    headers = {"X-Postmark-Server-Token": config.POSTMARK_API_KEY}

    json = {
        "From": "ben@ninepanels.com",
        "To": recipient_email,
        "Subject": f"Nine Panels: {recipient_name}, let's reset your password...",
        "HtmlBody": f"<p>Hello {recipient_name},</p> <p>Let's get your password reset! Click the link here:</p> <p>{url}</p> <p>See you back on Nine Panels.</p> <p> Cheers, Ben. </p> ",
        "MessageStream": "outbound",
    }

    try:
        resp = requests.post(
            "https://api.postmarkapp.com/email", json=json, headers=headers
        )
    except requests.exceptions.RequestException as e:
        raise errors.PasswordResetTokenException(f"problem sending email {str(e)}")

    if resp.status_code == 200:
        return True
    else:
        raise errors.PasswordResetTokenException(f"problem sending email {str(e)}")
