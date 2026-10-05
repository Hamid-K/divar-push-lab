# Snapp: driver radio collection and separate app services

Passenger (`cab.snapp.passenger`) and driver (`cab.snapp.driver`) are distinct packages and signers. Seventeen exact APKs were inspected: twelve passenger and five driver. The collector boundary is **driver 5.15.0 absent → sampled 5.17.0 present**; missing 5.16.0 prevents a precise introduction date.

| Exact APK | SHA-256 | Reviewed state |
| --- | --- | --- |
| Driver 5.15.0 | [74660538613dd5ccb077ed46a3124e9242258e1c139520642d5f1599613cbad4](https://www.virustotal.com/gui/file/74660538613dd5ccb077ed46a3124e9242258e1c139520642d5f1599613cbad4) | Collector gate/DTO/route absent in raw DEX; VT first submitted 13 April 2026. |
| Driver 5.17.0, install-capable flavor | [2c7bee97b304134c58aafc15d9935a55a9091488e2a200080353218932bfe671](https://www.virustotal.com/gui/file/2c7bee97b304134c58aafc15d9935a55a9091488e2a200080353218932bfe671) | Collector present; VT first submitted 26 July. |
| Driver 5.17.0, other flavor | [92c08213268642ee3e6818e872f94aeb81469987b4db3334d5f171c3b7134520](https://www.virustotal.com/gui/file/92c08213268642ee3e6818e872f94aeb81469987b4db3334d5f171c3b7134520) | Same relevant collector DEX; different install-permission variant; VT first submitted 4 August. |
| Passenger 8.38.0 | [3010c025224dd7291237c5f8ad6f783baf006d3b6b17e792e5e2fce571bed218](https://www.virustotal.com/gui/file/3010c025224dd7291237c5f8ad6f783baf006d3b6b17e792e5e2fce571bed218) | Reviewed `cab.snapp.fanoos` classes absent. |
| Passenger 8.39.0 | `d1d54f36650263dafce5e1c203b761e1bf32d238455c08536f571e43ef1b6003` | Fanoos polling classes present. Acquired from [APKPure's 2 March archive listing](https://apkpure.net/snapp-%D8%A7%D8%B3%D9%86%D9%BE/cab.snapp.passenger/versions); the listing is not an exact-hash VT timestamp. |

## Driver collector anchors

- JADX 5.17.0 `p007o/i06.java:332–340` reads the `isWifiCollectionEnabled` AB flag. `p007o/p06.java:831–873` requires that flag, a positive collection interval and a positive Wi-Fi or cell sample count before observation/publish work.
- `p007o/i06.java:444–460` builds `RadioSignalCollectionRequest` from fused/network/manual/suggested positions, Wi-Fi scans, connected cells, foreground state, ride status and device time. Serialized names appear in `p007o/RadioSignalCollectionRequest.java:15–37`; Wi-Fi `bssid_hash` and `ssid_hash` fields are in `p007o/WifiScan.java:17–45`. `p007o/jcd.java:36–49` and `p007o/osa.java:33–46` hash those identifiers with unsalted SHA-256. Coordinates and cell identifiers remain structurally available.
- The publish method is `p007o/i06.java:470–473`; the route suffix is in `p007o/ff.java:10–16`. The embedded location base is `https://locations.snapp.site/v1/driver/` (`p007o/j40.java:20–25`), yielding default `POST /collect`. The driver root applies a server-provided location base at `cab/snapp/driver/root/a.java:3480–3488`, so the effective historical destination is unknown.
- The relevant location and Wi-Fi manifest permissions already existed in the sampled 5.15.0 file. The route is separate from the earlier MQTT location publisher. Neither AB settings nor historical requests were recovered.

## Polling and update paths are different

Passenger 8.39.0 declares `GET v1/passenger/polling-notifications` in JADX `J8/b.java:102–107`; `J8/b.java:126–146` parses `notifications[].{id,data,type}` and `x-poll-interval`. The reviewed default renderer posts a visible notification and opens a link/action after a tap. No `Fanoos.ignite()` callsite was found in the decompiled 8.39.0 passenger app, so fresh-install activation is unverified. A separate driver Fanoos route is present by 5.15.0; the 5.17.0 root checks authorization/feature state around `ignite()` (`root/a.java:3490–3499`).

The driver also has a Behrooz in-app updater: `p007o/dj.java:287–296` reads `UpdateConfig.directUrl`, and `p007o/nh.java:74–83` carries that configured URL into download/install handling. One 5.17.0 flavor declares package-install permissions and the other does not. No hostile update URL, downloaded stage, successful install or edge from the reviewed push/poll handler to Behrooz was recovered.

**Limits.** [Uptodown lists](https://snapp.en.uptodown.com/android/versions) passenger 8.39.0 on 25 February, but that is a version-level listing, not a date for the acquired APKPure hash. The collector is compatible with positioning or signal checking; static code cannot establish malicious use or an enabled cohort.
