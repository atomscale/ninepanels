import hashlib
import os
import re
import requests
import logging
import rollbar

from typing import Dict
from dataclasses import dataclass
from collections import defaultdict, deque
from datetime import datetime

from . import errors
from . import config
from . import pydmodels as pyd


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


def dispatch_welcome_email(recipient_email: str, recipient_name: str) -> bool:
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
        resp = requests.post(
            "https://api.postmarkapp.com/email", json=json, headers=headers
        )
    except requests.exceptions.RequestException as e:
        raise errors.WelcomeEmailException(f"problem sending welcome email {str(e)}")

    if resp.status_code == 200:
        return True
    else:
        raise errors.WelcomeEmailException(
            detail=f"problem sending welcome email {str(e)}"
        )


def dispatch_welcome_catch_up(recipient_email: str, recipient_name: str) -> bool:
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


def dispatch_mid_sept(recipient_email: str, recipient_name: str) -> bool:
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
        resp = requests.post(
            "https://api.postmarkapp.com/email", json=json, headers=headers
        )
    except requests.exceptions.RequestException as e:
        raise errors.WelcomeEmailException(f"problem sending mid sept email {str(e)}")

    if resp.status_code == 200:
        return True
    else:
        raise errors.WelcomeEmailException(f"problem sending mid sept email {str(e)}")


pattern = re.compile(r"(?<=/)\d+(?=/|$)")


def replace_numbers_in_path(path: str) -> str:
    return pattern.sub("x", path)


class Timer:

    """single, ephemeral per request"""

    def __init__(
        self, factory: object, method: str, request_id: str, path: str
    ) -> None:
        self.request_id = request_id
        self.path = path
        self.method = method
        self.start_ts: datetime = None
        self.stop_ts: datetime = None
        self.factory = factory

        self.diff_ms: float = None
        self.is_running: bool = False

    def start(self):
        self.start_ts = datetime.utcnow()
        self.is_running = True

    def stop(self) -> float:
        self.stop_ts = datetime.utcnow()
        self.is_running = False
        diff_timedelta = self.stop_ts - self.start_ts

        self.diff_ms: float = diff_timedelta.total_seconds() * 1000
        self.factory.update(
            method_path=f"{self.method}_{self.path}", request_id=self.request_id
        )


class TimerFactory:
    timers = {}
    stats = {}

    window_size = 100
    alert_thresholds = {
        "GET_/": 10,
        "GET_/users": 20,
        "GET_/panels": 40,
        "GET_/admin/performance/route": 10,
        "POST_/panels/x": 50,
        "POST_/panels/x/entries": 40,
        "PATCH_/panels/x": 40,
        "DELETE_/panels/x": 40,
        "DELETE_/panels/x/entries": 40,
        "POST_/token": 500,
        "GET_/docs": 10,
        "GET_/openapi.json": 40
    }
    alert_threshold = 40

    def __init__(self) -> None:
        self.readings =  defaultdict(lambda: deque([], maxlen=self.window_size))
        self.request_ids = deque([], maxlen=self.window_size)
        self.component_timers = deque([], maxlen=self.window_size)

    def create_timer(self, request_id, method, path) -> Timer:
        path = replace_numbers_in_path(path)
        method_path = f"{method}_{path}"

        timer = Timer(factory=self, method=method, request_id=request_id, path=path)

        if method_path not in self.timers:
            self.timers[method_path] = deque(maxlen=self.window_size)
            self.timers[method_path].append(timer)
        else:
            self.timers[method_path].append(timer)
        return timer

    def update(self, method_path, request_id):
        path_timer_stats = {}
        times = [
            i.diff_ms
            for i in self.timers[method_path]
            if not i.is_running and i.diff_ms
        ]
        if times:
            path_timer_stats = {
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "last": times[len(times) - 1],
            }

            self.stats[method_path] = path_timer_stats

            reading = {
                "timestamp": datetime.utcnow(),
                "request_id": request_id,
                "reading": path_timer_stats["last"],
            }
            self.readings[method_path].append(reading)
            self.request_ids.append(reading)

        self.assess_performance()

    def assess_performance(self):
        for method_path in self.stats:
            if method_path in self.alert_thresholds:
                self.alert_threshold = self.alert_thresholds[method_path]

            self.stats[method_path]["alert_threshold"] = self.alert_threshold
            self.stats[method_path]["in_alert"] = False

            if self.stats[method_path]["avg"] > self.alert_threshold:
                self.stats[method_path]["in_alert"] = True
                # TODO logging and monitoring code here

    @property
    def route_performance(self) -> list[dict]:
        output = []


        for method_path in self.stats:
            ts_arr = []
            req_arr = []
            read_arr = []
            for mp_reading in self.readings[method_path]:
                ts_arr.append(mp_reading['timestamp'])
                req_arr.append(mp_reading['request_id'])
                read_arr.append(mp_reading['reading'])

            reading_out = {
                'timestamp': ts_arr,
                'request_id': req_arr,
                'reading': read_arr
            }

            method, path = method_path.split("_")
            output.append(
                {
                    "id": method_path,
                    "method": method,
                    "path": path,
                    "stats": self.stats[method_path],
                    "readings": reading_out
                }
            )





        return output

    @property
    def request_performance(self) -> list[dict]:
        return self.request_ids
