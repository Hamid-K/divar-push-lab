# Balad: radio observations from location updates

The Café Bazaar package `ir.balad` and Google Play package `com.baladmaps` have different signers and must be compared as separate tracks. The decisive Bazaar boundary is a sampled **4.79.0 without** the reviewed uploader and a sampled **4.81.1 with** it. The interval includes APKs that were not acquired; it is not an exact introduction date.

| Exact `ir.balad` APK | SHA-256 | Reviewed state |
| --- | --- | --- |
| 4.79.0 / code 7071 | [4c015bc86454142d7d5e4318e02454d0e1c7c2c9c602f3227fbde5a631c31784](https://www.virustotal.com/gui/file/4c015bc86454142d7d5e4318e02454d0e1c7c2c9c602f3227fbde5a631c31784) | No `RadioObservationUploader` call or `v2/geosubmit` literal in the inspected DEX. |
| 4.81.1 / code 7101 | [da7e348ba2fd161e0a0d05b7ad7a216f95389f9e69219144d5cc72bf7454370b](https://www.virustotal.com/gui/file/da7e348ba2fd161e0a0d05b7ad7a216f95389f9e69219144d5cc72bf7454370b) | Location callback reaches a remotely gated uploader. VT first submission: 10 June 2026. |
| 4.83.0 / code 7130 | [d5b38a482e9bcc62b942e993b4539d10a3385f06787411dced83f80ad66d0541](https://www.virustotal.com/gui/file/d5b38a482e9bcc62b942e993b4539d10a3385f06787411dced83f80ad66d0541) | Adds a GNSS-spoofing verdict check before upload. |
| 4.84.0 / code 7160 | [d76c77633224e48760b60226722a50146b8d7245ceb1a96ac0a0ece3b98008d7](https://www.virustotal.com/gui/file/d76c77633224e48760b60226722a50146b8d7245ceb1a96ac0a0ece3b98008d7) | Adds a second location-source switch and batching up to ten observations. |

## Reproducible code anchors

- In 4.81.1, JADX `LocationLogger.kt` (`M4/e.java`) calls `RadioObservationUploader.p(location, appMode)` on map/navigation location updates. `RadioObservationUploader.kt` (`O4/i.java`, gate in the decompiled `p` method) exits when `AppConfigEntity.baladNetworkProvider.isGeoSubmitEnabled` is absent or false. It then requires a non-mock GPS/fused fix with reported accuracy 1–50 m and limits the reviewed path to roughly one observation per 30 seconds.
- The Retrofit datasource declares `POST("v2/geosubmit")` on the embedded `https://location.raah.ir/` base. The model contains location, time, nearby cell and Wi-Fi observations, map/navigation context and SHA-256 of a persisted generated app UUID. Some model fields are `transient`; this is a model inventory, not a captured wire body.
- In 4.83.0, JADX `RadioObservationUploader.kt` (`p248u5/i.java`) checks `GNSSIntegrityState.Enabled.getSpoofingVerdict()` before the trusted-fix gate. In 4.84.0, `RadioObservationUploader.kt` (`p260v5/c.java`) honors `useBaladLocations`, may use Balad's network-location source, and can flush a batch of ten. `isGeoSubmitEnabled` remains the master switch.
- The switches are mapped from an AppMeta gRPC version-check response through `api.balad.ir:443`; an absent client config defaults them false. The inspected FCM service does not call this uploader. Coarse/fine location and Wi-Fi permissions predate the new route.

**Limits.** Missing Bazaar-track 4.78.0/4.78.1 (archive entries dated 24 February), 4.80.0 and 4.81.0 were not cleared by the surrounding files. Historical AppMeta values, exact serialized fields, upload receipts and endpoint ownership were not recovered. The code is compatible with a positioning or signal-quality function; it does not establish malicious collection.
