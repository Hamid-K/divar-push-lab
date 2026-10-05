# Neshan: command ingress and a separate native path

Package: `org.rajman.neshan.traffic.tehran.navigator`. The sampled command route and native location route are **separate**. No inspected edge connects the pull/FCM dispatcher to the `Impulse` native code.

| Exact APK or extracted base APK | SHA-256 | Evidence role |
| --- | --- | --- |
| 14.7.9 base, from [archived XAPK](https://d.apkpure.net/b/XAPK/org.rajman.neshan.traffic.tehran.navigator?versionCode=70609&nc=arm64-v8a&sv=21) | `302ae08a526f7a97592568242c89703357063f85ded9024adc5d9ca495b79fe6` | `PUSH_LOGGER` already present; archive upload listed 10 November 2025. The link serves the XAPK container, whose hash differs from this extracted base. |
| 14.8.9 base | [681b4f975d40b9d0f1dfa9d5d6b79d59cbd3ca46746a6f9f013ef1e1bf7bcfd4](https://www.virustotal.com/gui/file/681b4f975d40b9d0f1dfa9d5d6b79d59cbd3ca46746a6f9f013ef1e1bf7bcfd4) | Command exists; reviewed `notification/pull` route absent. VT first submitted 6 February 2026. |
| 14.8.10 base | [947c4a9412ef577b29c87d87764b4e9e0e3ddfd1966bff2cbab83adb3f2f8115](https://www.virustotal.com/gui/file/947c4a9412ef577b29c87d87764b4e9e0e3ddfd1966bff2cbab83adb3f2f8115) | App-open pull joins FCM dispatcher; archive upload listed 18 February, exact hash first submitted to VT 19 February. |
| 14.10.2.3 base | [90499f420b9288d8574e9bf9ae01ee90b2dc1dabb3005877b8655468c204a698](https://www.virustotal.com/gui/file/90499f420b9288d8574e9bf9ae01ee90b2dc1dabb3005877b8655468c204a698) | First sampled `Impulse` JNI bridge/native HTTPS path; VT first submitted 6 June. |
| 14.12.0.2 | [73ce0ecf024edda270aefd8c1daa5a0e16e6c0a8cc6c757ebc648a6029c14e8f](https://www.virustotal.com/gui/file/73ce0ecf024edda270aefd8c1daa5a0e16e6c0a8cc6c757ebc648a6029c14e8f) | First sampled recurring pull worker; VT first submitted 11 August. |
| 14.13.0.6 base | [24e8c96780668a13d7d3fb9780a0c52ccd1012f4ba06515d2f523506a98e5a0a](https://www.virustotal.com/gui/file/24e8c96780668a13d7d3fb9780a0c52ccd1012f4ba06515d2f523506a98e5a0a) | Later native method accepts observation JSON; exact base first submitted to VT 2 September. |

## Command and upload anchors

- The 14.8.9 JADX `pushNotification/FcmService.java:189–207` has a guarded `PUSH_LOGGER` case: `data.sendInfo` selects a device-info bundle; `data.fileList` selects files. This command predates the 2026 war.
- In 14.8.10, `sync/service/FcmService.java:34–50` passes FCM `metadata`, `data` and `intentData` to the shared dispatcher with source `1`. Retrofit `rn0/a.java:8–10` declares `GET notification/pull`; `ProcessPullMessageUseCase.java:55–60` passes each response to that dispatcher with source `3`. `MainActivity.java:5143–5147,5608–5615` anchors the app-attachment pull. Metadata/app-state checks still apply.
- `do0/o.java:278–282` takes the guarded `PUSH_LOGGER` branch before ordinary notification posting. `a80/d.java:23–42` constructs paths from command-supplied components below the app files directory; the inspected Java path lacks a canonical containment check. A `..` component could select another **app-readable** file, subject to the Android sandbox. `a80/d.java:56–75,101–105` queues ZIPs through WorkManager. `UploadFileWorker.java:27–50` performs multipart upload through Retrofit `ci0/c.java:16–18`, route `POST logger/uploadLogFile` on `https://app.neshanmap.ir/`.
- In 14.13.0.6, `sync/data/worker/SyncWorker.java:68–72,133–142` passes pulled responses with source `4` and reschedules after success or a caught exception. `t81/a.java:27–33` uses a configurable interval; `s61/a0.java:11–12` supplies an eight-hour compiled default. This does not establish that a historical server supplied `PUSH_LOGGER`.

## Native `Impulse` anchors

The arm64 `libnative-lib.so` from 14.10.2.3 has SHA-256 `09d0dfa13eb070cedd546cc0cd521e9518ad76021a0fab14e2cffd82410c8c17`; the 14.13.0.6 library has SHA-256 `6c181216638d08b7660730c7033130974273b57493714c00463a4f9fd438c543`. Native offsets below apply only to those hashes.

- In the June library, JNI `nativeGetAll(long)` at `0x3c5ec8` reaches helper `0x3ab274`, which serializes native object state and reaches an HTTPS helper at `0x36889c`. It has **no Java observation String argument**. `nativeCreate` receives Android `Context` and `TelephonyManager`, so the source of every native-state field remains unresolved.
- In the later library, JNI `nativeGetAll(long,String)` at `0x3c9cdc` consumes Java observation JSON; helper `0x3ad7e4` incorporates input-derived data, transforms it and passes a body to HTTP helper `0x36ad70`. Request builder `0x36d234` constructs a `POST` with an `application/json` body. The Java-side observation can include a recent GPS fix. This is a code-level data path, not a captured request or proof that every input field survives transformation.
- Native configuration uses encoded `tth` (host) and `pat` (path) fields; a static XOR/base64/AES-GCM recovery attempt did not authenticate plaintext. No exact host/path IOC is established. The reviewed later Java online-config model exposes `navigatorConfig.impulseConfig.enabled`, default false when absent. Its historical values and actual native traffic were unavailable.

**Limits.** The selected-file concern is not an Android sandbox escape. No command payload, upload receipt, native wire body, plaintext native destination or common operator with Divar was recovered. The February location-validation libraries are separate from the June `Impulse` expansion; neither is a demonstrated executable-stage loader.
