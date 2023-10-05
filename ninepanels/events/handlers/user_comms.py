import httpx

from ...core import config
from ... import exceptions
from ... import pydmodels as pyd
from .. import event_models


async def password_reset(
    event: event_models.PasswordResetRequested
) -> bool:


    headers = {"X-Postmark-Server-Token": config.POSTMARK_API_KEY}

    json = {
        "From": "ben@ninepanels.com",
        "To": event.email,
        "Subject": f"Nine Panels: {event.name}, let's reset your password...",
        "HtmlBody": f"<p>Hello {event.name},</p> <p>Let's get your password reset! Click the link here:</p> <p>{event.url}</p> <p>See you back on Nine Panels.</p> <p> Cheers, Ben. </p> ",
        "MessageStream": "outbound",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.postmarkapp.com/email", json=json, headers=headers
            )
    except httpx.HTTPError as e:
        raise exceptions.PasswordResetTokenException(f"problem sending email {str(e)}")

    if resp.status_code == 200:
        return True
    else:
        raise exceptions.PasswordResetTokenException(f"problem sending email {str(e)}")


async def welcome(event: event_models.NewUserCreated) -> bool:
    """send email using mail provider api

    Returns:
        True on email success (200)
    Raises:
        exceptions.EmailException on any failure
    """
    headers = {"X-Postmark-Server-Token": config.POSTMARK_API_KEY}

    json = {
        "From": "ben@ninepanels.com",
        "To": event.email,
        "Subject": f"Nine Panels: {event.name}, a warm welcome!",
        "HtmlBody": f"""<p>Hello {event.name},</p>
        <p><b>Thank you so much for signing up to Nine Panels!</b></p>
        <p>Nine Panels nurtures daily balance the important areas of your life. And it shows how consistently you engage with those areas.</p>
        <p>I built it for myself - I struggle to be consistent with one thing, let alone all the things! - and I'm properly honoured to share it with you. </p>
        <p>The app is installable on your mobile just like an app you woudl download from the App or Play Store. Instructions on how to install are in the download icon in the top right.</p>
        <p>It's still early days for Nine Panels, and there is much more to come. I'm really glad you are here.</p>
        <p>I hope you get value from seeing your consistency becoming visible, and your balanced, good days becoming more regular.</p>
        <p>Let me know what you think, and any ideas you have would be amazing to hear.</p>
        <p></p>
        <p>Cheers, Ben. </p>
        <p></p>
        <p>p.s. for you geeks out there, this is an open source project and you can see the code and feature roadmap at https://github.com/atomscale/ninepanels</p>""",
        "MessageStream": "outbound",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.postmarkapp.com/email", json=json, headers=headers
            )
    except httpx.HTTPError as e:
        raise exceptions.EmailException(f"problem sending email {str(e)}")

    if resp.status_code == 200:
        return True
    else:
        raise exceptions.EmailException(detail=f"problem sending welcome email {str(e)}")


async def dispatch_user_update(recipient_email: str, recipient_name: str) -> bool:
    """send email using mail provider api

    Returns:
        True on email success (200)
    Raises:
        exceptions.EmailException on any failure
    """
    headers = {"X-Postmark-Server-Token": config.POSTMARK_API_KEY}

    json = {
        "From": "ben@ninepanels.com",
        "To": recipient_email,
        "Subject": f"Nine Panels: a couple of neat new features...",
        "HtmlBody": f"""<p>Hey again {recipient_name},</p>
        <p><b>A couple of new features have been released to make Nine Panels easier and prettier to use.</b></p>
        <p>If you haven't checked in recently, a couple of core new features have dropped:<p>
        <li><b>Nine Panels is now installable on your mobile device.</b> Installing makes it look and feel like an app you would download from your App or Play Store. This makes it easier to open and tap your panels, and enhances the overall vibe of the app no end! Tap the download icon in the top right for instructions. If you can, please install the app today as it paves the way for many future features!</li>
        <li><b>Colour themes!</b> You can now select from no less than five (five!!) colour themes, including a swanky dark mode.</li>
        <li>There's also a new settings screen, improved panel design and lots of optimisation behind the scenes.</li>

        <p>I wondered if I could possibly ask again for you to share the app with anyone you think might find it useful too. It's free forever, free of trackers and third party nasties, and totally open source.</p>
        <p>There are more features to come and, as always, if you have any ideas or thoughts, please just respond to this email.</p>
        <p>Until next time, {recipient_name}!</p>
        <p>Cheers, Ben. </p>
        <p></p>
        <p><i>If you don't want these feature announcements anymore, please reply with 'unsubscribe' in the email, and you won't get optional emails anymore.</i></p>""",
        "MessageStream": "outbound",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.postmarkapp.com/email", json=json, headers=headers
            )
    except httpx.HTTPError as e:
        raise exceptions.PasswordResetTokenException(f"problem sending email {str(e)}")

    if resp.status_code == 200:
        return True
    else:
        raise exceptions.EmailException(f"problem sending update email {str(e)}")

async def handle_new_user_created(event: event_models.NewUserCreated):
    await welcome(event)
