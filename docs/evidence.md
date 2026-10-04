# Evidence and limits: `11.14.20-b`

This lab is anchored to the preserved infected Divar APK `divar-11-14-20-b.apk`, SHA-256 `cdaf0bf256269eec249787299b5ebb7058f3944c86b14debfa41f9c263ad17da`. Its package is `ir.divar`. The public lab uses a separate package and does not distribute the original APK or DEX files.

## Code path observed in the APK

1. The bundled OneSignal parser maps `custom.a` to provider data, `alert` to body, and `title` to title. `PushNotificationExtender.h` passes those values to the shared notification provider. Decompiled references: `com.onesignal.AbstractC3677v0.a` and `ir.divar.chat.notification.onesingnal.PushNotificationExtender.h`.
2. Divar’s Firebase service routes a flat data map through the same provider when `source` is `divar` or `default`; it takes body and title from the map. Other source values do not enter this branch. Decompiled reference: the Firebase service’s message callback in the sampled APK.
3. In provider method `Wk.g.f`, nonempty `title` must equal provider-data `push_id`. It parses the body as JSON and requires nonempty `callback_url`, `campaign`, and `action`. It sends an explicit broadcast to the class named by `action`, sets the Intent URI to `campaign`, stores `campaign` as both an extra key and its value, then **returns before the provider’s ordinary notification code**. The calling OneSignal extender can still continue its SDK display path. Companion source: `divar-backdoor-analysis/src/Wk_g.java`, around lines 619–655.
4. The non-exported `ChatPushNotificationOpenHandler.onReceive` reads the URI and compares it with the extra selected by that URI. On equality it starts `ReportDeserializer(context, dataString)` on a new thread and returns before its ordinary notification-open behavior. Companion source: `divar-backdoor-analysis/src/ChatPushNotificationOpenHandler.java`, around lines 40–49.
5. The original worker Base64-decodes and XORs `campaign` with `0x68` to form a fetch URL. Its fetched JSON can determine file bytes and an invoked method. Companion source: `divar-backdoor-analysis/src/ReportDeserializer.java`, around lines 54–79 and 135–174. **The lab substitutes a fixed, non-executable simulated-LPE stage at this point.**

The broadcast and receiver check run **on push receipt**. No tap or Android notification display is required for this branch. `callback_url` is a nonempty guard; it is not the URL given to `ReportDeserializer`. Merely finding these strings in another APK would not establish the same control flow.

The sampled APK’s `classes3.dex` contains `onesignal/android/031503`, identifying the OneSignal 3.15.3 SDK generation. The sampled DEX class `Lcom/onesignal/I0;` also contains `https://push.divar.ir/_nrto_/`. That address **suggests a Divar-specific modification to OneSignal REST transport**; its complete runtime use has not been established. The lab builds against stock `com.onesignal:OneSignal:3.15.3`, not that apparent modification. Its `LabOneSignalExtenderService` subclasses the real `NotificationExtenderService` and passes SDK-normalized `additionalData`, `body`, and `title` to `LabNotificationProvider`. The earlier cloud-test build returned `false` so stock SDK display processing could continue. On the API 33/target 34 lab setup, that stock display path crashed because its `PendingIntent` lacked a required mutability flag. The current extender returns `true` **after** the cloned provider call to suppress only that display path. This compatibility shim does not change the receipt-time provider and receiver checks, but it does limit display fidelity. The sampled app's display behavior has not been runtime-tested. The observed callback and inserted provider/receiver path are the fidelity target; the transport backend and ordinary Divar fallback are not cloned.

## Fidelity boundary

| Question | Current answer |
| --- | --- |
| Which release is modeled? | The observed `11.14.20-b` inserted branch in the APK hash above. Other versions had code changes; this lab makes no claim that their paths are identical. |
| Is the handler bytecode copied? | No. The app independently implements the observed logic and internal handoff. The original worker and the normal Divar notification path are deliberately absent. |
| Does the lab reproduce notification display? | No. Current `LabOneSignalExtenderService` returns `true` after the cloned provider call to suppress the crashing stock SDK 3.15.3 display path on this emulator. Earlier cloud logs used `return false`. The sampled APK's display behavior is not established by either run. |
| Is direct FCM cloud push real? | On the combined OneSignal/FCM build, an HTTP v1 send to the emulator’s registration token reached the handler. The accepted vector ran the receiver and fixed marker without a tap; a title-mismatch control did not relay. Device and marker logs establish this beyond API acceptance. |
| Does the OneSignal SDK parser path work? | Yes. A direct FCM send containing a fixed OneSignal-shaped `custom`/`title`/`alert` envelope reached the stock 3.15.3 extender, shared provider, receiver, and marker [on receipt](onesignal_envelope_receipt_log.txt). A title-mismatch [control](onesignal_envelope_title_mismatch_log.txt) reached the extender without dispatching. These test SDK handling, not OneSignal's sending service. |
| Is OneSignal delivery real? | Yes for this synthetic lab: both dashboard and API CLI pushes from the OneSignal test app reached the emulator through FCM and its stock 3.15.3 SDK. In each pair, the title-mismatch control did not dispatch; the matching push ran the receiver on receipt. This does not test the sampled APK’s apparent Divar-specific REST transport or establish any historical Divar send. |
| Did the lab achieve privilege escalation? | No. In the end-to-end OneSignal API run, the precompiled stage attempted a read-only open of a protected Android file; Android denied it. The stage read no bytes, and UID and SELinux context stayed unchanged. |
| Was an attack observed? | No historical matching push, fetched command, payload, on-device execution, or Android privilege escalation was recovered for this lab. |

The API run showed the cloud message reaching the app and the stage status changing **without interaction with a system notification**. The current lab shim suppresses stock SDK notification display after the cloned provider call; display is not the inserted branch's trigger.

The [34-second emulator recording](divar_cloud_push_demo.mp4) captures a fresh direct FCM run on 4 October 2026. At 03:22:16 CEST, a title mismatch produced no dispatch. At 03:22:28.848, the matching push entered the inserted branch; the receiver started its worker by .851, the local server logged `GET /marker` at 03:22:28, and the app logged cleanup and `PASS` by .867. No screen interaction triggered the worker.

## Live OneSignal cloud check

On 4 October 2026, the OneSignal test app's **Test & preview** sent two pushes through OneSignal → FCM → the emulator. Its dashboard reported both sends successful. The emulator and marker-server observations distinguish the two handler outcomes:

| UTC time | Vector | Device and marker result |
| --- | --- | --- |
| 01:50:59.098 | [Title mismatch](divar-onesignal-title-mismatch-20261004.txt) | The OneSignal extender received a normalized payload. The inserted branch did not match, so there was no internal dispatch or marker `GET`. |
| 01:51:55.223 | [Matching title](divar-onesignal-accepted-20261004.txt) | The extender received the payload and the cloned branch sent its explicit broadcast on receipt. The receiver equality check matched at .238; the fixed `GET /marker` returned HTTP 200. The app wrote the non-executable marker at .328, its precompiled handler consumed it at .333, and cleanup plus `PASS` appeared at .334. No tap occurred. |

The accepted handler ran as app UID `10175` in Android's `untrusted_app` SELinux domain. This verifies the synthetic app's OneSignal cloud route and benign marker; it does not demonstrate execution of downloaded code, privilege escalation, or a notification sent through Divar's production account.

## OneSignal API CLI run: simulated-LPE stage

The fixed host response includes `"stage":"simulated-lpe"`. The app validates that exact three-field JSON, writes a non-executable marker in app-private storage, and calls a handler already compiled into the APK. That handler attempts `O_RDONLY` on Android's protected `/data/system/packages.xml`; `EACCES` or `EPERM` is the expected result. It reads **no bytes**, stops if opening unexpectedly succeeds, and checks that the process UID and SELinux context are unchanged. The marker is then removed.

On 4 October 2026, the fixed OneSignal API CLI vectors produced this sequence ([40-second split-screen video](evidence/onesignal_cli_simulated_lpe_2026-10-04.mp4); [device log](evidence/onesignal_cli_simulated_lpe_2026-10-04.txt)):

| Time | Vector | Observed result |
| --- | --- | --- |
| 02:25:20.173 UTC / 04:25:20 CEST | `title-mismatch` | The SDK extender received the push; the inserted branch did not match. No internal dispatch or marker `GET` appeared. |
| 02:25:37.252 UTC / 04:25:37 CEST | `accepted` | The extender received the push; the provider sent its explicit broadcast at .254, and the receiver check matched at .270. The fixed host served one `GET /marker`; the app fetched the stage descriptor by .286. |
| 02:25:37.289–.291 UTC | Fixed stage | The precompiled handler logged “Running simulated LPE payload...”; Android denied its read-only protected-file open, no bytes were read, UID `10175` and SELinux context stayed unchanged, the marker was removed, and `PASS` appeared by .291. |

The device log records handler execution; the concurrent marker-server observation establishes the single host request. This is a visible sandbox boundary check, not an LPE attempt against a vulnerability. No external code, exploit, or privilege escalation ran. The earlier dashboard logs above document the prior benign marker implementation; this API run verifies the revised stage.

## Sources

- [raminfp’s original code analysis](https://gist.github.com/raminfp/a548a2af86108eb40b8bffc5c8f07aaa)
- [Hamid Kashfi’s X post](https://x.com/hkashfi/status/2106147963332633025)
- [Firebase Android receive behavior](https://firebase.google.com/docs/cloud-messaging/android/receive-messages) and [FCM HTTP v1 sends](https://firebase.google.com/docs/cloud-messaging/send/v1-api)
- Companion local analysis: `divar-backdoor-analysis/src/Wk_g.java`, `ChatPushNotificationOpenHandler.java`, and `ReportDeserializer.java`, extracted from the APK hash above.
