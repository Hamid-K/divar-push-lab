# FCM sample messages for the synthetic lab

These examples target **this lab app only**. They are FCM HTTP v1 requests, not Android ADB broadcasts, OneSignal messages, or recovered Divar attacker notifications. Replace `<REGISTERED_FID>` with the current Firebase Installation ID copied from the lab app. Keep that identifier, your OAuth token, and any service-account credentials out of the repository and published demo.

For the included sender, start `python3 tools/marker_server.py`, grant the app Android notification permission, log in to `gcloud` with an account allowed to send FCM messages in your project, and run:

```sh
gcloud auth login
python3 tools/send_cloud_sample.py --project YOUR_FIREBASE_PROJECT_ID accepted
python3 tools/send_cloud_sample.py --project YOUR_FIREBASE_PROJECT_ID rejected
```

The helper reads the current FID privately from the emulator's debug app with `adb run-as`, obtains a short-lived OAuth token from `gcloud`, and sends the fixed accepted or wrong-nonce body below. It prints only FCM API acceptance; check the emulator and app log for actual delivery. Add `--validate-only` before the sample name for an API schema check without delivery. The extra-field example below is a manual control and is not a helper mode.

For a manual send, use each JSON body with `POST https://fcm.googleapis.com/v1/projects/<YOUR_FIREBASE_PROJECT_ID>/messages:send`, `Content-Type: application/json`, and `Authorization: Bearer <SHORT_LIVED_OAUTH_TOKEN>`. The sender needs `cloudmessaging.messages.create` permission. See [Firebase's HTTP v1 authorization guide](https://firebase.google.com/docs/cloud-messaging/send/v1-api) and [FCM IAM roles](https://cloud.google.com/iam/docs/roles-permissions/firebasecloudmessaging).

## 1. Accepted data-only message

```json
{
  "message": {
    "fid": "<REGISTERED_FID>",
    "data": {
      "lab_action": "deliver_marker",
      "lab_nonce": "divar-lab"
    },
    "android": { "priority": "HIGH" }
  }
}
```

The app receives the data in `LabFirebaseMessagingService.onMessageReceived`, checks the **exact two-field map**, then posts its own Android notification titled **Cloud lab message received**. Open the notification shade and tap it. That tap invokes a non-exported receiver through an immutable app-created `PendingIntent`. The receiver then runs the fixed marker path. The FCM message alone does not trigger the marker fetch.

In the verified API 33 emulator run on 4 October 2026, this cloud message posted the notification; the tap led to one `GET /marker`, a harmless in-app file write, a call to a precompiled method, cleanup, and `PASS` in the app log.

## 2. Wrong nonce control

```json
{
  "message": {
    "fid": "<REGISTERED_FID>",
    "data": {
      "lab_action": "deliver_marker",
      "lab_nonce": "wrong-nonce"
    },
    "android": { "priority": "HIGH" }
  }
}
```

Expected: the app rejects the data message, posts no lab notification, and makes no marker request. The log says `Rejected FCM message: expected exact data-only action and nonce.`

## 3. Extra-field control

```json
{
  "message": {
    "fid": "<REGISTERED_FID>",
    "data": {
      "lab_action": "deliver_marker",
      "lab_nonce": "divar-lab",
      "extra": "ignored-by-design"
    },
    "android": { "priority": "HIGH" }
  }
}
```

Expected: the same rejection. Although the two required values are present, the app requires exactly two data fields. This is a lab gate, not the field check found in Divar.

## What each part does

| Field or boundary | Role in this lab |
| --- | --- |
| `message.fid` | Identifies this particular emulator app installation for FCM delivery. It can rotate. It is not a Divar user ID or a payload field. |
| `message.data` | Sends string values to the app's FCM callback. No top-level `notification` object is used. |
| `lab_action` | Must equal `deliver_marker` to pass the app's first gate. It does not select an arbitrary operation. |
| `lab_nonce` | Must equal `divar-lab`. It is a fixed demo check, not a cryptographic challenge or proof of a trusted sender. |
| `android.priority` | Requests FCM's high delivery priority. It does not make delivery immediate, bypass Android permissions, or control the notification's display priority. |
| Android notification | Created locally **after** the app accepts the FCM data. Notification permission is needed on Android 13 and later. |
| User tap | Starts the fixed marker pipeline through the app-created `PendingIntent`; FCM receipt itself stops at notification posting. |

This is deliberately **data-only**. Firebase documents that a backgrounded app may receive a top-level FCM `notification` object in the system tray without its `onMessageReceived` callback handling it. A combined notification-and-data payload behaves differently again. These examples make the app's validation and notification-posting code part of the observed route. See [Firebase's Android receive guide](https://firebase.google.com/docs/cloud-messaging/android/receive-messages) and [HTTP v1 message schema](https://firebase.google.com/docs/reference/fcm/rest/v1/projects.messages).

The push does not contain an address or executable. After a valid notification is tapped, the app decodes its **compiled-in** endpoint and requires it to equal `http://10.0.2.2:18765/marker`. The host server returns only:

```json
{"kind":"lab-marker","nonce":"divar-lab","message":"benign"}
```

The app checks those three response values, writes `divar-lab:benign` as text in app-private storage, calls a precompiled handler, and removes the text. The server cannot nominate code, a method, or another URL. This differs materially from the broader behavior reported in the inserted Divar worker.
