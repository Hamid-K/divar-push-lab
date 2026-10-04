#!/usr/bin/env python3
"""Send one fixed FCM data message to this synthetic emulator lab."""

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


PACKAGE = "org.hamidk.divarpushlab"
PROJECT_ID = re.compile(r"[a-z][a-z0-9-]{4,28}[a-z0-9]\Z")


class LabSendError(Exception):
    """An expected setup or send failure with no credential details."""


def command_output(argv, failure_message):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=20)
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        raise LabSendError(failure_message) from error
    if result.returncode != 0 or not result.stdout.strip():
        raise LabSendError(failure_message)
    return result.stdout.strip()


def registered_fid():
    preferences = command_output(
        ["adb", "exec-out", "run-as", PACKAGE, "cat", "shared_prefs/lab.xml"],
        "Cannot read the lab app's registration. Check adb devices, install/open "
        "the debug app, and wait for FCM registration.",
    )
    try:
        node = ET.fromstring(preferences).find("./string[@name='registered_fid']")
    except ET.ParseError as error:
        raise LabSendError("The lab app's local registration data is malformed.") from error
    if node is None or not node.text or not node.text.strip():
        raise LabSendError("No FCM installation ID yet. Open the app and wait for registration.")
    return node.text.strip()


def access_token():
    return command_output(
        ["gcloud", "auth", "print-access-token"],
        "Cannot obtain a short-lived gcloud token. Log in with a sender account "
        "that has FCM send permission in your Firebase project.",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Your Firebase project ID")
    parser.add_argument("--validate-only", action="store_true",
                        help="Ask FCM to validate the request without delivery")
    parser.add_argument("sample", choices=("accepted", "rejected"),
                        help="Fixed valid data or the wrong-nonce control")
    args = parser.parse_args()
    if not PROJECT_ID.fullmatch(args.project):
        parser.error("--project must be a Firebase project ID (lowercase letters, digits, hyphens)")

    fid = registered_fid()
    token = access_token()
    body = {
        "message": {
            "fid": fid,
            "data": {
                "lab_action": "deliver_marker",
                "lab_nonce": "divar-lab" if args.sample == "accepted" else "wrong-nonce",
            },
            "android": {"priority": "HIGH"},
        }
    }
    if args.validate_only:
        body["validate_only"] = True

    request = urllib.request.Request(
        f"https://fcm.googleapis.com/v1/projects/{args.project}/messages:send",
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "x-goog-user-project": args.project,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        # The response body could echo routing data. Do not print it.
        raise LabSendError(
            f"FCM returned HTTP {error.code}. Check the project ID, app config, "
            "sender permission, and FCM API enablement."
        ) from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise LabSendError("Cannot reach FCM. Check network access and retry.") from error
    except (ValueError, json.JSONDecodeError) as error:
        raise LabSendError("FCM returned an unreadable response.") from error
    if not isinstance(result, dict) or not result.get("name"):
        raise LabSendError("FCM did not return a message acknowledgement.")
    if args.validate_only:
        print("FCM accepted validation only; no message was delivered.")
    else:
        print(f"FCM accepted the {args.sample} sample for delivery. "
              "Check the emulator and app log for actual reception.")


if __name__ == "__main__":
    try:
        main()
    except LabSendError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
