import hashlib
import os
import requests

from . import errors
from . import config

def generate_random_hash() -> str:
    """ Generate a random hash

    Returns
        hash: 64 character hexademcial string

    """

    random_bytes = os.urandom(32)
    hash_bytes = hashlib.sha256(random_bytes)
    hash = hash_bytes.hexdigest()

    return hash

def dispatch_password_reset_email(recipient_email: str, recipient_name: str, url: str) -> bool:
    """ send email using mail provider api



    on success message respond with True, else False
    """
    headers = {"X-Postmark-Server-Token": config.POSTMARK_API_KEY}

    json = {
        "From": "ben@ninepanels.com",
        "To": recipient_email,
        "Subject": "Nine Panels: let's reset your password",
        "HtmlBody": f"Hello {recipient_name} \n \n Let's get your password reset. Click the link below \n \n {url} \n\n See you back on Nine Panels. \n Cheers, Ben. \n \n p.s. Sorry for the very plain email, will look nicer soon :)",
        "MessageStream": "outbound"
      }

    try:
        resp = requests.post("https://api.postmarkapp.com/email", json=json, headers=headers)
    except requests.exceptions.RequestException as e:
        raise errors.PasswordResetTokenException(f"problem sending email {str(e)}")

    if resp.status_code == 200:
        return True
    else:
        raise errors.PasswordResetTokenException(f"problem sending email {str(e)}")
