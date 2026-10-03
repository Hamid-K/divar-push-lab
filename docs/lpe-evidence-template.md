# Separate LPE evidence worksheet

Use this worksheet only for an independently authorized test in a disposable emulator or for analysis of a preserved device trace. The push-marker lab stops at the app's own UID. It supplies no exploit, does not invoke a downloaded binary, and does not claim that a Divar user experienced an Android privilege escalation.

## Record the environment

| Field | Value / evidence file |
| --- | --- |
| Emulator or device identifier | |
| System image source and exact build fingerprint | |
| Android version and security patch level | |
| Image checksum | |
| App APK checksum and package name | |
| App UID and SELinux context before the separate test | |
| Relevant published vulnerability advisory and affected-image evidence | |
| Test timestamp and time zone | |

## Record the result

| Question | Observation / evidence file |
| --- | --- |
| Was the marker delivered to the test app? | |
| Did any separate stage run? Identify its source and checksum. | |
| What process performed the action? UID, PID, parent, SELinux context. | |
| Was a boundary crossed? Show the identity and access change. | |
| Did the same test fail on a patched image? | |
| What logs, screen recording, and hashes were preserved? | |

Write the conclusion in the smallest terms supported by those records: *marker delivered*, *in-app action observed*, *privilege change observed on this image*, or *inconclusive*. The first two do not imply the third. A result on a deliberately vulnerable emulator would show the separate vulnerability's behavior in that lab image; it would not establish that historical Divar users received that stage.

Android normally isolates apps with distinct UIDs and SELinux contexts. A purported escape should be supported by identity and access evidence rather than a banner or command's claimed success. [Android's application sandbox documentation](https://source.android.com/docs/security/app-sandbox) explains the baseline.
