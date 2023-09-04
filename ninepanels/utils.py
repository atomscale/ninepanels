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


def dispatch_welcome_email(
    recipient_email: str, recipient_name: str
) -> bool:
    """send email using mail provider api

    Returns:
        True on email success (200)
    Raises:
        errors.WelcomeEmailException on any failure
    """
    headers = {"X-Postmark-Server-Token": config.POSTMARK_API_KEY}

    json = {
        "From": "ben@ninepanels.com",
        "To": recipient_email,
        "Subject": f"Nine Panels: {recipient_name}, a warm welcome!",
        "HtmlBody": f"""<p>Hello {recipient_name},</p>
        <p><b>Thank you so much for signing up to Nine Panels!</b></p>
        <p>Nine Panels nurtures daily connection with the important areas of your life. And it shows how consistently you make those connections.</p>
        <p>I built it for myself - I struggle to be consistent with one thing, let alone all the things! - and I'm properly honoured to share it with you. </p>
        <p>The app is still early, and there is more to come.</p>
        <p>I really hope you get value from seeing your consistency becoming visible, and your balanced, good days becoming more regular.</p>
        <p>Let me know what you think, and any ideas you have would be amazing to hear</p>
        <p></p>
        <p>Cheers, Ben. </p>
        <p></p>
        <p>p.s. for you geeks out there, this is an open source project and you can see the code and feature roadmap at https://github.com/atomscale/ninepanels</p>""",
        "MessageStream": "outbound",
    }

    try:
        resp = requests.post(
            "https://api.postmarkapp.com/email", json=json, headers=headers
        )
    except requests.exceptions.RequestException as e:
        raise errors.WelcomeEmailException(f"problem sending welcome email {str(e)}")

    if resp.status_code == 200:
        return True
    else:
        raise errors.WelcomeEmailException(f"problem sending welcome email {str(e)}")


def dispatch_welcome_catch_up(
    recipient_email: str, recipient_name: str
) -> bool:
    """send email using mail provider api

    Returns:
        True on email success (200)
    Raises:
        errors.WelcomeEmailException on any failure
    """
    headers = {"X-Postmark-Server-Token": config.POSTMARK_API_KEY}

    json = {
        "From": "ben@ninepanels.com",
        "To": recipient_email,
        "Subject": f"Nine Panels: {recipient_name}, a long overdue welcome email!",
        "HtmlBody": f"""<p>Hey {recipient_name},</p>
        <p><b>I just wanted to say a big thank you for signing up to Nine Panels!</b></p>
        <p>If you haven't checked in recently, a few new features have been released:<p>
        <li> the consistency visualisation (the reason the app was built);</li>
        <li> free text notes/description on each panel, that supports markdown;</li>
        <li> panel ordering and the ability to visually reorder the panels;</li>
        <li> forgot password;</li>
        <li> native sharing on mobile (in the left menu);</li>
        <li> reset history on each panel (a clean slate!);</li>
        <li> a help/how to area, replete with videos;</li>
        <li> a refined landing page and a unified message about "Daily balance, long-term consistency";</li>
        <li> emoji support throughout (vital!)</li>
        <p>I know you might have just signed up to show interest out of friend-duty, which is greatly appreciated! Thank you again! But I also know some of you are finding it useful. Different strokes I guess!</p>
        <p>I wondered if I could possibly ask you to share the app with anyone you think might find it useful too. The app will always be free, and I'd love to be able to show a decent active user base in the app when it becomes part of my 'portfolio' of software development. Any help you could lend would be amazing.</p>
        <p>There are more features and refinement to come, and if you had any ideas or thoughts, just respond to this email.</p>
        <p>Thanks again {recipient_name}!</p>
        <p>Cheers, Ben. </p>
        <p></p>
        <p>p.s. for you geeks out there, this is an open source project and you can see the code and feature roadmap at https://github.com/atomscale/ninepanels</p>""",
        "MessageStream": "outbound",
    }

    try:
        resp = requests.post(
            "https://api.postmarkapp.com/email", json=json, headers=headers
        )
    except requests.exceptions.RequestException as e:
        raise errors.WelcomeEmailException(f"problem sending welcome email {str(e)}")

    if resp.status_code == 200:
        return True
    else:
        raise errors.WelcomeEmailException(f"problem sending welcome email {str(e)}")
