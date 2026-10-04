"""Check the OneSignal lab request before any network send."""

import base64
import json
import unittest

from send_cloud_sample import HANDLER, MARKER_URL, PUSH_ID, LabSendError, sample_data
from send_onesignal_sample import notification_request


APP_ID = "00000000-0000-4000-8000-000000000001"
SUBSCRIPTION_ID = "00000000-0000-4000-8000-000000000002"


class OneSignalRequestTest(unittest.TestCase):
    def request(self, sample="accepted", **overrides):
        return notification_request(sample, APP_ID, SUBSCRIPTION_ID, **overrides)

    def test_default_vector_still_targets_the_local_lab_subscription(self):
        request = self.request()
        body = json.loads(request["contents"]["en"])
        self.assertEqual(request["include_subscription_ids"], [SUBSCRIPTION_ID])
        self.assertEqual(request["headings"]["en"], PUSH_ID)
        self.assertEqual(request["data"]["push_id"], PUSH_ID)
        self.assertEqual(request["contents"]["en"], sample_data("accepted")["body"])
        self.assertEqual(body["action"], HANDLER)
        decoded = base64.b64decode(body["campaign"])
        self.assertEqual(bytes(byte ^ 0x68 for byte in decoded).decode(), MARKER_URL)

    def test_custom_url_and_handler_fields_are_encoded_independently(self):
        url = "https://example.invalid/stage?case=one&part=two"
        request = self.request(url=url, callback_url="guard-only", push_id="lab-42",
                               title="lab-42")
        body = json.loads(request["contents"]["en"])
        decoded = base64.b64decode(body["campaign"])
        self.assertEqual(bytes(byte ^ 0x68 for byte in decoded).decode(), url)
        self.assertEqual(body["callback_url"], "guard-only")
        self.assertEqual(body["action"], HANDLER)
        self.assertEqual(request["headings"]["en"], request["data"]["push_id"])

    def test_mismatch_control_stays_a_mismatch_with_custom_push_id(self):
        request = self.request("title-mismatch", push_id="different-title")
        self.assertNotEqual(request["headings"]["en"], request["data"]["push_id"])

    def test_invalid_campaign_urls_are_rejected(self):
        for url in ("", "file:///tmp/stage", "https://", "https://bad host/stage",
                    "https://user:secret@example.invalid/stage", "https://example.invalid:bad/stage",
                    "https://example.invalid/" + "😀" * 1000):
            with self.subTest(url=url), self.assertRaises(LabSendError):
                self.request(url=url)


if __name__ == "__main__":
    unittest.main()
