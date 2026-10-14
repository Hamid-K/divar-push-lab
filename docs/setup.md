# Cloud setup for the Divar push-handler lab

Use a dedicated Firebase project and, for the OneSignal route, a separate OneSignal test app. The lab package is `org.hamidk.divarpushlab`. No Divar production credentials or original APK are needed.

## Direct FCM

1. [Register an Android app](https://firebase.google.com/docs/android/setup) with the exact package `org.hamidk.divarpushlab` in your Firebase project. Put its `google-services.json` at `app/google-services.json`. The build applies the Google services plugin when this file exists.
2. Confirm **Firebase Cloud Messaging API (HTTP v1)** is enabled. Use a `gcloud` login or an impersonated test service account with `cloudmessaging.messages.create` on this project. The sender calls `gcloud auth print-access-token`; it does not need a downloaded service-account key. See [FCM HTTP v1 authorization](https://firebase.google.com/docs/cloud-messaging/send/v1-api).
3. Start a Google Play services emulator, then build, install, and open the app. Wait for “FCM registration succeeded” on its screen. The helper reads its token privately through ADB.

   ```sh
   ./gradlew :app:assembleDebug
   adb install -r app/build/outputs/apk/debug/app-debug.apk
   ```

4. Start `python3 tools/marker_server.py` in another terminal. It listens on host loopback `127.0.0.1:18765`; the emulator addresses that host as `10.0.2.2`.
5. Send the matching vector, then the title-mismatch control:

   ```sh
   python3 tools/send_cloud_sample.py --project YOUR_FIREBASE_PROJECT_ID accepted
   python3 tools/send_cloud_sample.py --project YOUR_FIREBASE_PROJECT_ID title-mismatch
   adb logcat -d -s DivarPushLab:I '*:S'
   ```

The first vector should produce one `GET /marker` and app `PASS`; the control should not reach the marker. Check the emulator and marker-server logs. An FCM API response proves only that FCM accepted the send request.

## OneSignal test app

OneSignal sends through the **same Firebase project** to the stock OneSignal 3.15.3 SDK in this synthetic app.

1. Create a dedicated Firebase service account whose permissions are limited to `cloudmessaging.messages.create` and `firebase.projects.get`. Generate its JSON key and upload it to the new OneSignal test app under **Settings → Push & In-App → Platforms → Google Android (FCM)**. [OneSignal's credential guide](https://documentation.onesignal.com/docs/en/android-firebase-credentials) gives the current dashboard steps. Keep this private key out of Git.
2. Add this ignored file at `app/onesignal.properties`:

   ```properties
   app_id=YOUR_ONESIGNAL_APP_ID
   sender_id=YOUR_NUMERIC_FIREBASE_PROJECT_NUMBER
   ```

   Rebuild, install, and open the app. Wait until it shows both **Push token present: true** and **Subscribed: true**. Add that lab subscription to **Test Subscriptions** in the OneSignal dashboard.
3. Send `title-mismatch` before `accepted` through the dashboard using the exact [title, message, and Additional Data](sample-events.md#onesignal-test-app-route). For the CLI alternative, set `ONESIGNAL_API_KEY` privately to the test app's App API key, then run:

   ```sh
   python3 tools/send_onesignal_sample.py title-mismatch
   python3 tools/send_onesignal_sample.py accepted
   ```

   The CLI reads the App ID and subscribed emulator ID locally; it does not take a destination ID. Optional `--url`, `--callback-url`, `--push-id`, and `--title` fields are described in the [sample messages](sample-events.md). Even with a custom encoded URL, the lab worker fetches only `http://10.0.2.2:18765/marker`.

Watch the marker-server terminal, app screen, and `adb logcat -v epoch -s DivarPushLab:I '*:S'`. The matching push should run the fixed stage on receipt; the control should not. The stage only checks that a read-only open of a protected Android file is denied and that app UID and SELinux context do not change. The [video](evidence/onesignal_cli_simulated_lpe_2026-10-04.mp4) and [device log](evidence/onesignal_cli_simulated_lpe_2026-10-04.txt) record the verified run.

## Credentials and cleanup

`app/google-services.json` and `app/onesignal.properties` are Git-ignored. Keep FCM tokens, OneSignal subscription IDs, App API keys, and service-account JSON out of commits and recordings. When retiring the lab, revoke the OneSignal App API key and Firebase service-account key, remove the sender permission, and clear or uninstall the emulator app. The public checkout builds without Firebase configuration, but cloud registration and delivery require your own project.
