#!/usr/bin/env python3
"""Send a lab push through the locally registered OneSignal test app."""

import argparse
import base64
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET

from send_cloud_sample import (
    HANDLER, MARKER_URL, PACKAGE, PUSH_ID, LabSendError, command_output,
)


CONFIG = Path(__file__).resolve().parent.parent / "app" / "onesignal.properties"
API_URL = "https://api.onesignal.com/notifications"
SAMPLES = ("accepted", "title-mismatch")


def checked_uuid(value, description):
    try:
        return str(uuid.UUID(value.strip()))
    except (AttributeError, ValueError) as error:
        raise LabSendError(f"The {description} is missing or malformed.") from error


def app_id():
    try:
        lines = CONFIG.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise LabSendError("Missing ignored app/onesignal.properties with app_id=... .") from error
    for line in lines:
        if line.strip().startswith("app_id="):
            return checked_uuid(line.split("=", 1)[1], "OneSignal app ID")
    raise LabSendError("Missing app_id in ignored app/onesignal.properties.")


def test_subscription_id():
    preferences = command_output(
        ["adb", "exec-out", "run-as", PACKAGE, "cat", "shared_prefs/lab.xml"],
        "Cannot read the debug lab app's local OneSignal registration. "
        "Check adb devices, install/open the app, and wait for subscription.",
    )
    try:
        root = ET.fromstring(preferences)
    except ET.ParseError as error:
        raise LabSendError("The lab app's local registration data is malformed.") from error
    subscribed = root.find("./boolean[@name='onesignal_subscribed']")
    push_token_present = root.find("./boolean[@name='onesignal_push_token_present']")
    if subscribed is None or subscribed.get("value") != "true":
        raise LabSendError("The lab app has not confirmed a OneSignal push subscription yet.")
    if push_token_present is None or push_token_present.get("value") != "true":
        raise LabSendError("The lab app has not confirmed a OneSignal push token yet.")
    node = root.find("./string[@name='onesignal_player_id']")
    return checked_uuid(node.text if node is not None else None, "test subscription ID")


def encoded_campaign(url):
    """Encode the worker URL in the format used by the sampled Divar handler."""
    if (not url or len(url.encode("utf-8")) > 2048
            or any(ord(char) <= 32 or ord(char) == 127 for char in url)
            or "\\" in url):
        raise LabSendError(
            "--url must be a single HTTP(S) URL without whitespace or control characters."
        )
    try:
        parsed = urllib.parse.urlsplit(url)
        valid = (parsed.scheme in ("http", "https") and parsed.hostname
                 and parsed.username is None and parsed.password is None)
        parsed.port  # Reject malformed ports before sending.
    except ValueError as error:
        raise LabSendError("--url is not a valid HTTP(S) URL.") from error
    if not valid:
        raise LabSendError("--url must be an absolute HTTP(S) URL without embedded credentials.")
    encoded = bytes(byte ^ 0x68 for byte in url.encode("utf-8"))
    return base64.b64encode(encoded).decode("ascii")


def notification_request(sample, one_signal_app_id, subscription_id, *,
                         url=MARKER_URL, callback_url="present-but-not-fetched",
                         push_id=PUSH_ID, title=None):
    """Map handler fields to a notification addressed to the local lab subscription."""
    if sample not in SAMPLES:
        raise ValueError("Unknown sample")
    if title is None:
        title = push_id if sample == "accepted" else "different-title"
        if sample == "title-mismatch" and title == push_id:
            title += "-mismatch"
    body = {
        "callback_url": callback_url,
        "campaign": encoded_campaign(url),
        "action": HANDLER,
    }
    return {
        "app_id": one_signal_app_id,
        "target_channel": "push",
        "include_subscription_ids": [subscription_id],
        "headings": {"en": title},
        "contents": {"en": json.dumps(body, separators=(",", ":"))},
        "data": {"push_id": push_id},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", choices=SAMPLES)
    parser.add_argument("--url", "--campaign-url", default=MARKER_URL,
                        help="HTTP(S) URL encoded into campaign; the lab app fetches only its fixed marker URL")
    parser.add_argument("--callback-url", default="present-but-not-fetched",
                        help="Nonempty handler guard; this is not the fetched URL")
    parser.add_argument("--push-id", default=PUSH_ID,
                        help="Additional Data push_id used in the title equality check")
    parser.add_argument("--title", help="Notification title; defaults to a match or mismatch for the selected sample")
    args = parser.parse_args()

    key = os.environ.get("ONESIGNAL_API_KEY", "").strip()
    if not key:
        raise LabSendError("Set ONESIGNAL_API_KEY to the fresh test app's REST API key.")
    if any(character.isspace() for character in key):
        raise LabSendError("ONESIGNAL_API_KEY must contain only the single copied key, with no shell text.")
    body = notification_request(
        args.sample, app_id(), test_subscription_id(), url=args.url,
        callback_url=args.callback_url, push_id=args.push_id,
        title=args.title,
    )
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body, separators=(",", ":")).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Key {key}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        # The response body may echo routing details; never print credentials or IDs.
        raise LabSendError(
            f"OneSignal returned HTTP {error.code}. Check the test app's API key, "
            "FCM credentials, and subscription."
        ) from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise LabSendError("Cannot reach OneSignal. Check network access and retry.") from error
    except ValueError as error:
        raise LabSendError("OneSignal returned an unreadable response.") from error
    if not isinstance(result, dict) or not result.get("id"):
        raise LabSendError("OneSignal accepted the request but created no targeted message.")
    print(f"OneSignal accepted the {args.sample} test message for delivery. "
          "Check the emulator, app log, and marker-server log for receipt.")
    if args.url != MARKER_URL:
        print("If delivered, the lab worker will reject this custom URL before fetching it.")


if __name__ == "__main__":
    try:
        main()
    except LabSendError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
