# Tapsi: geolocation and a landing-flavor patch updater

The current passenger package is `taxi.tap30.passenger`; the current driver package is `taxi.tap30.driver`. The 20 passenger and 13 driver APKs in this corpus were first submitted to VT from June through September 2026. No January–May bytes for these exact packages were acquired, so this review cannot settle pre-war behavior.

| Exact APK | SHA-256 | Evidence role |
| --- | --- | --- |
| Passenger 7.3.0 | [0339673d8d859cf58c1393d314427ddfecacefd4c9e9e732394629269b03e1b8](https://www.virustotal.com/gui/file/0339673d8d859cf58c1393d314427ddfecacefd4c9e9e732394629269b03e1b8) | Reviewed `v3/geolocation/geolocate` literal absent; VT first submitted 24 July. |
| Passenger 7.7.0 | [8361c7cf1c163edcac0afa7eaabb7d596c702ed8cb4385748b4d6b6f34941323](https://www.virustotal.com/gui/file/8361c7cf1c163edcac0afa7eaabb7d596c702ed8cb4385748b4d6b6f34941323) | Route literal present; VT first submitted 12 June. This lower-to-higher version boundary cannot be converted to a calendar introduction date. |
| Passenger 7.8.4 | [e7e7597fcc8e2dc93535bd8eebd862433da34c1c67a1c73120e3268a84ae2869](https://www.virustotal.com/gui/file/e7e7597fcc8e2dc93535bd8eebd862433da34c1c67a1c73120e3268a84ae2869) | Decompiled callable POST and seven-field request. |
| Passenger 7.10.0 | [b72744d23b6289908a9a58bcceaa3c1cdbfdee58a71ee2c30c906c81ceb574e1](https://www.virustotal.com/gui/file/b72744d23b6289908a9a58bcceaa3c1cdbfdee58a71ee2c30c906c81ceb574e1) | Same serialized request despite clearer class names. |
| Driver 8.8.0 / Myket | [4f26428e71051bcf116cc97d33670adf76f24cafe8b1e1a550e19eb42a94ee47](https://www.virustotal.com/gui/file/4f26428e71051bcf116cc97d33670adf76f24cafe8b1e1a550e19eb42a94ee47) | No reviewed Yadegar patch module; VT first submitted 5 September. |
| Driver 8.8.0 / landing | [1647b9af56b3923ac8a32c3ee9aeb9513563d73a86181f1db05a10f3bbed95a4](https://www.virustotal.com/gui/file/1647b9af56b3923ac8a32c3ee9aeb9513563d73a86181f1db05a10f3bbed95a4) | Callable geolocation request and Yadegar patch updater; VT first submitted 14 September. |

## Geolocation request anchors

- Passenger JADX 7.8.4 `yu0/a.java:14` and 7.10.0 `yv0/a.java:11` annotate `POST("v3/geolocation/geolocate")`. Their DTOs serialize the same fields: `cellTowers`, `wifiAccessPoints`, repeat counts for each, `isWifiEnabled`, `lastLocation` and `lastInHouseNetworkLocation`. Repository calls appear in 7.8.4 `fv0/b.java:384–443` and 7.10.0 `fw0/b.java:396–435`; they require at least one cell or Wi-Fi observation. The production default is `https://p1.tapsi.ir/api/` (`sf0/d.java:35`, `pf0/e.java:74`).
- Driver 8.8.0 landing `KP/a.java:16` declares the analogous POST. `QP/b.java:253–285,334–348` builds or deserializes an observation request and reads the returned location estimate. `p1125iU/a.java:109–133` reads enabled-feature flags; inspected fallback config in `p1052hI/GeoLocationSdkConfig.java:285` is disabled. The production base resolves to `https://d1.tapsi.ir/api/` (`p378Qg/b.java:14`, `p358Pi/a.java:80`). No actual request or live feature value was captured.

## Same-version updater difference

Both driver 8.8.0 files have package `taxi.tap30.driver`, versionCode `1080080000` and the same signer. Embedded build IDs are `myket_productionFinalRelease` versus `landing_productionFinalLanding`. Only the landing variant has Yadegar workers, native `libapkpatch.so`, install-result handling and package-install declarations. It is a distribution-flavor difference, not evidence of a timed insertion and retraction.

In the landing JADX path, `QG/k.java:370–372` initializes the updater with `https://d1.tapsi.ir/api/`; `Yz/b.java:72–89` requests `GET v3/yadegar/public/get-patch/{packageName}/{appVersion}`. The response supplies `patchUrl`, `patchName`, `hasNewUpdate`, `targetVersion` and `patchSize`. `p801dA/m.java:50–55` passes the selected URL to a worker; `p614aA/a.java:81–99` applies a native binary patch to the installed APK; `p740cA/o.java:38–76` streams the reconstructed APK into `PackageInstaller` and commits. The inspected Java/Kotlin path does not compare an independent expected hash or detached signature before commit; Android installer checks still apply. No patch bytes, attacker control or install result were recovered.

**Limits.** Driver 7.13.6 lacks the reviewed route/DTO, while higher-version 7.21.0 has them; the negative's VT submission came later than the positive's. Version order, not those submission dates, bounds that code delta. These are sensitive data and update capabilities, not proof of malicious collection or delivery.
