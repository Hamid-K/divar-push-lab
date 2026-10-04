#!/usr/bin/env python3
"""Send one fixed benign vector through a fresh OneSignal test app."""

import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
import uuid
import xml.etree.ElementTree as ET

from send_cloud_sample import PACKAGE, PUSH_ID, LabSendError, command_output, sample_data


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


def fixed_request(sample, one_signal_app_id, subscription_id):
    """Map the fixed provider input to the OneSignal notification API."""
    if sample not in SAMPLES:
        raise ValueError("Unknown fixed sample")
    data = sample_data("accepted")
    return {
        "app_id": one_signal_app_id,
        "target_channel": "push",
        "include_subscription_ids": [subscription_id],
        "headings": {"en": PUSH_ID if sample == "accepted" else "different-title"},
        "contents": {"en": data["body"]},
        "data": {"push_id": PUSH_ID},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", choices=SAMPLES)
    args = parser.parse_args()

    key = os.environ.get("ONESIGNAL_API_KEY", "").strip()
    if not key:
        raise LabSendError("Set ONESIGNAL_API_KEY to the fresh test app's REST API key.")
    if any(character.isspace() for character in key):
        raise LabSendError("ONESIGNAL_API_KEY must contain only the single copied key, with no shell text.")
    body = fixed_request(args.sample, app_id(), test_subscription_id())
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


if __name__ == "__main__":
    try:
        main()
    except LabSendError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
