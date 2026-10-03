# Evidence behind the lab

The lab models a narrow point: notification delivery can put an encoded endpoint in reach of installed app code, and the endpoint can then provide a second instruction set. It does not replay the Divar code or claim an observed attack. The following distinctions should travel with any screenshot or video of the demo.

## The sampled APK record

| Sample | SHA-256 | Observation |
| --- | --- | --- |
| `11.14.9` | `1636d586bd89ae68cf9d8214b3ab31ddda60f3c05b8b4a4eed724520f2cc7bad` | Known worker class absent from the parsed APK. |
| `11.14.10` | `9e6a9955d9b6e1db5636d4213c386944da8e740170f4e6159b2ecb202decb0db` | Earliest confirmed APK containing the inserted worker in this sample set. Archive file date: 24 February 2026. |
| `11.14.15-b` | `9c02f4467d5495bdcdd2c9783a496d665ba128a81f6793e7018e8b59382b4a6f` | Known inserted chain absent between positive samples. |
| `11.14.20-b` | `cdaf0bf256269eec249787299b5ebb7058f3944c86b14debfa41f9c263ad17da` | Worker, receiver and inspected notification relay present. |
| `11.15.0-w` | `2c57177e254ec914883a2ed33716e703fad1e2cd21f022332b79a06667852db8` | Known worker class absent from the parsed APK. |

These hashes were checked against the preserved APK inventory and release audit on 3 October 2026. The source CSVs are in the companion local research folder and are not bundled here. Archive file dates are not verified developer release, installation, or activation dates. Different distribution variants need separate inspection.

The inserted route in inspected positive builds is: OneSignal notification extender or Divar Firebase Messaging service → field gate in the handler → internal relay → non-exported receiver → `ir.divar.chat.util.ReportDeserializer`. The worker Base64-decodes and XORs the push-supplied `campaign` value to obtain a URL, GETs one JSON line, writes decoded `data` bytes to a path, invokes a compatible method by reflection, then removes the file after a delay. The push itself provides the encoded URL; the HTTP response can provide the file bytes and invocation details. These are code observations. No qualifying real push, command response, payload file, on-device execution, or LPE was recovered.

In `11.14.19-b`, the receiver and worker remain but the inspected notification sender lacks the relay; an alternate route has not been proven or excluded. This is why the repo never labels every intermediate release as having an identical working path. The first confirmed insertion in sampled APKs has no new manifest permission. `RECORD_AUDIO` was already declared; the later foreground-service microphone delta belongs to a VoIP service and does not establish recording by the inserted worker.

## What the synthetic code stands in for

| Historical code observation | Lab stand-in | Difference |
| --- | --- | --- |
| OneSignal or Firebase notification ingress | App button or ADB event | No cloud push is sent or received. |
| Push-supplied encoded address | Fixed allowlisted `http://10.0.2.2:18765/marker` | No arbitrary destination or attacker server. |
| Server response can name bytes and methods | Fixed `lab-marker` JSON | No executable content or server-selected method. |
| File write, reflective invocation, cleanup | Harmless marker and precompiled method | No reflection, dynamic loading, native invocation, or LPE. |

The lab receiver checks a fixed action and nonce. It does not reproduce Divar's title/`push_id` and JSON field gate. The encoded endpoint in this app is a constant that must decode to one allowlisted emulator URL.

The fixed server binds to the host loopback interface. Its negative controls reject other routes and uploads. The app's rejected samples should make no request to `/marker`.

The lab uses package `org.hamidk.divarpushlab` and targets Android API 34. The sampled Divar `11.14.20-b` APK is package `ir.divar` and targets API 35. The demo is an analogy of the delivery boundary, not a patched build or a platform-parity test.

## The missing evidence that would change the assessment

1. A push request or retained provider message with the exact title and body fields, sender identity, recipient set, and timestamp.
2. Correlated phone, Divar backend, OneSignal, or FCM records tying that push to a command fetch. A delivery export may omit message body; verify the actual retention and export fields.
3. The fetched response and file bytes, with hashes, and an on-device trace of write, invocation, and deletion.
4. Separate evidence for any attempted or successful sandbox escape: exact OS image, patch level, process identity before and after, and a trace of the boundary crossed.

Each item answers a different question. A signed APK demonstrates code in a sampled app lineage, not who inserted it. A matching push demonstrates delivery, not command execution. A worker log demonstrates execution in the app, not an LPE. A privilege change would need its own trace and vulnerability analysis.

## Sources

- [raminfp, technical disclosure and code notes](https://gist.github.com/raminfp/a548a2af86108eb40b8bffc5c8f07aaa)
- [Hamid Kashfi, X post about the Divar finding and possible device-delivery use](https://x.com/hkashfi/status/2106147963332633025)
- [Uptodown's Divar version archive](https://divar.en.uptodown.com/android/versions) and [APKPure's Divar listing](https://apkpure.net/divar/ir.divar) for sampled distribution files; their dates and files do not constitute a complete release record.
- [OneSignal message API and audience selection](https://documentation.onesignal.com/reference/create-message)
- [Firebase Cloud Messaging architecture](https://firebase.google.com/docs/cloud-messaging/fcm-architecture)
- [Android application sandbox](https://source.android.com/docs/security/app-sandbox)
- [Android 10 app-home execution rule](https://developer.android.com/about/versions/10/behavior-changes-10)
