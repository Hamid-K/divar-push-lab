# Internal release-marker audit: 282 exact Divar APKs

**Scope and date:** 11 October 2026. I read all 282 acquired APK files listed in the local `release_ledger.csv`, recomputed each file's SHA-256, and matched each hash to its ledger row. The ledger records all 282 as signature verified under the same Divar signer; this pass did not independently rerun APK signature verification. These are 282 distinct hashes and 225 displayed version names. Per-hash evidence is in [`Divar_release_marker_matrix.csv`](Divar_release_marker_matrix.csv); the local extractor reproduces it from the acquired APK files. A timestamp *inside* an APK is not, by itself, its source commit time, signing time, Bazaar/Divar publication time, or installation time.

## What the APKs actually contain

| Internal marker | Coverage | Useful reading | Limit |
|---|---:|---|---|
| Real ZIP entry times | 7/282 | Earliest seven APKs, `3.3` through both `8.2` hashes, have coherent DEX, manifest and v1 signature-entry clock values. | ZIP DOS time has **no timezone or trusted signature-time semantics**. Some asset entries in the second `8.2` APK retain times from the earlier build. |
| Generated Crashlytics build property | 81/282 | Its comment carries a local clock and zone (`IRST`, `IRDT`, or `UTC`), and the file supplies `version_name`, `version_code`, and a `build_id`; 65 distinct IDs. It covers late 2015 through `11.2.5` in October 2020. | Generation time of an embedded property, which can survive later assembly or redistribution. A build ID is not a publication date or unique final APK hash. |
| Sentry debug-meta property | 186/282 present; **67/282 dated** | Date comment starts at `11.12.4` in September 2024. All 186 include a ProGuard UUID; 153 UUIDs across the corpus. | The 119 earlier Sentry files contain a UUID but **no date**. The dated property can be carried through another packaging pass. |
| Android Gradle VCS metadata | 67/282 | `META-INF/version-control-info.textproto` carries a 40-hex-character Git revision; 53 distinct revisions. It appears alongside the dated Sentry format. | The SHA has no embedded date. Access to the source/CI records is needed to tie it to a commit, build and final APK hash. |
| `versionCode` date-like value | 281/282 interpretable under the era-specific schemes below | It supplies an internal *candidate calendar day* even in the 2020–2024 gap. | It is an app-controlled identifier, not a release attestation. The value can label a planned release train and can predate assembly by weeks. |

There are **150 APKs with some embedded calendar clock**: 2 ZIP-only, 81 Crashlytics-dated (five also have real ZIP times), and 67 Sentry-dated. The remaining 132 APKs have no embedded calendar timestamp identified here. `11.2.5` is a transition: two APKs carry both a dated Crashlytics asset and an undated Sentry asset. After the last dated Crashlytics sample and before `11.12.4`, the version code is the only identified internal calendar candidate. This is an evidence gap, not evidence that the APKs were not built during that period.

## Version-code regimes

The same nine-digit field changes format. A naive `YYMMDD` parse of the 2023 early backdoor is wrong.

| APK range in this corpus | Inferred encoding | Example | Gregorian candidate |
|---|---|---|---|
| `6.7`–`8.2` | Leading digit plus `MMDDHHmm` on the builder's local clock | `111071638` → 7 Nov, 16:38; the `7.0.2` Crashlytics property says 7 Nov 2015, 16:38:39 IRST | 7 Nov 2015 |
| `8.8.1`–`11.9.1` | `2` + `(Persian year − 1100)` as three digits + Persian `MMDD` + sequence | `230202172` → 1402/02/17, **not** 2 Feb 2023 | **7 May 2023** for `11.8.1` |
| `11.9.2`–`11.15.0-b` | Gregorian `YYMMDD` + sequence | `230819010` → 19 Aug 2023 | 19 Aug 2023 for `11.9.2` |
| `3.3` | `3030`; no date interpretation supported | — | — |

The observed format switch is between **`11.9.1` and `11.9.2` in August 2023**. The Persian dates were converted using Node/ICU's Persian calendar in the reproducible script. The scheme is supported by independent local clocks in early builds: the Crashlytics date and version-code candidate have the same *local* calendar day in **79/81** APKs. The exceptions are `9.1.0`, whose property is one day earlier, and `10.0.1`, whose property is three days later. In the 67 recent Sentry-dated APKs, the Sentry day follows the code candidate by 0–28 days (median seven). Thus the recent `versionCode` should not be described as a build timestamp.

## ZIP time test on the seven earliest APKs

Times in this table are **local time with unknown timezone**. All 7 have real dates in every ZIP entry; the later 275 APKs use normalized values (96 use invalid DOS `1980-00-00 00:00:00`; 179 use `1981-01-01 01:01:02`).

| Version; SHA prefix | `classes.dex` | Manifest | v1 signature entry | Span of all ZIP times | Interpretation |
|---|---|---|---|---|---|
| `3.3`; `98337c91` | 2013-02-28 18:05:42 | 18:05:42 | 18:05:42 | 18:05:12–18:05:42 | Coherent packaging clock; no independent zone. |
| `6.7`; `7cb32944` | 2015-03-14 14:07:18 | 14:07:18 | 14:07:20 | 14:06:34–14:07:20 | Coherent packaging clock; VT first saw it ten days later. |
| `7.0.2`; `0f816a2a` | 2015-11-07 16:39:48 | 16:40:28 | 16:40:28 | 16:38:30–16:40:28 | Crashlytics says 16:38:39 IRST. |
| `8.0.0`; `b28e05df` | 2016-01-21 12:03:26 | 12:03:28 | 12:03:28 | 12:01:42–12:03:28 | Crashlytics says 12:01:41 IRST. |
| `8.1.1`; `3193c165` | 2016-06-20 18:14:24 | 18:14:26 | 18:14:26 | 18:04:10–18:14:26 | Crashlytics says 18:12:14 IRDT. |
| `8.2`; `13307212` | 2016-08-20 12:56:56 | 12:56:58 | 12:57:00 | 12:54:26–12:57:00 | Crashlytics says 12:54:24 IRDT. |
| `8.2`; `a42f1cc6` | 2016-08-22 12:01:30 | 12:01:32 | 12:01:34 | **20 Aug** 12:54:26–22 Aug 12:01:34 | Old asset timestamps were reused. DEX/manifest/signature and Crashlytics 22 Aug 11:58:55 IRDT identify the later assembly pass. |

The last row is a concrete reason **not** to take the earliest ZIP timestamp as an APK build time.

For the generated properties, the matrix preserves the original comment and also converts its named zone to UTC: `IRST` = UTC+03:30, `IRDT` = UTC+04:30, `SGT` = UTC+08:00, and `UTC`/`GMT` = UTC. The conversion records what the embedded text says; the build host's clock accuracy is not attested. ZIP entry times have no timezone field and are deliberately left as local/unknown rather than assigned a UTC instant.

## Incident-boundary cross-check

These are exact-hash observations, **not official release dates**. The VT column is first submission of that hash. `11.14.11` retains the push route but lacks the inspected HTTP header route; the ledger's coarse `chain_status=present` must not be read as meaning both routes were present.

| Version; SHA prefix | Route status | `versionCode` candidate | Sentry UTC | VT first submission UTC | VT − Sentry |
|---|---|---|---|---|---:|
| `11.8.1`; `ee36859f` | Early backdoor present | **7 May 2023** (Persian 1402/02/17) | None | 14 May 2023 | — |
| `11.13.11`; `9f232774` | Push route present | 20 Apr 2025 | 30 Apr 2025 14:36 | 3 May 2025 16:42 | 3.1 d |
| `11.13.12`; `8c8e7406` | Inspected route absent | 4 May 2025 | 11 May 2025 12:57 | 12 May 2025 08:30 | 0.8 d |
| `11.14.10`; `9e6a9955` | Push route present | 8 Feb 2026 | **16 Feb 2026 13:50** | 24 Feb 2026 09:24 | 7.8 d |
| `11.14.11`; `c0b20748` | Push route present; HTTP route absent | 3 Mar 2026 | 3 Mar 2026 17:42 | 20 Mar 2026 09:53 | 16.7 d |
| `11.14.12`; `85b3a282` | Push and HTTP routes present | 28 Apr 2026 | **17 May 2026 13:32** | 24 May 2026 21:50 | 7.3 d |
| `11.14.12.1`; `152c788f` | Push and HTTP routes present | 28 Apr 2026 | 26 May 2026 03:33 | 28 May 2026 11:28 | 2.3 d |

The oldest **observed positive** APK is still `11.8.1` on 14 May 2023. Its version-code candidate of 7 May is not a proven infection or distribution date. Likewise, the HTTP-positive `11.14.12` package contains a 17 May Sentry property, but that does not prove when the HTTP code was written, first signed, or served to a device. The `11.14.11` same-code control has 3 March and 18 March Sentry dates for two signed APKs with identical DEX; its alternate hash reached VT only on 29 May, **71 days** after its Sentry marker. That makes a VT upload a poor release clock and shows the embedded property can differ across packaging passes of one code state.

## Gap and provenance checks

- Of 282 hashes, 277 have an exact-hash VT first-submission time. The other five retain the ledger's archive-listing date and basis; the matrix leaves their VT field blank.
- The ledger links 139 hashes to Uptodown, 73 to KernApk, 51 to APKPure, three to other archives, and 16 to no archive URL. A link records source/provenance for a matching hash; it does not prove which transport delivered the local bytes. Archive `lastUpdate` and catalog dates can be later than the file's original availability.
- For the 79 Crashlytics-dated APKs with a VT first-submission time, median VT lag is **0.907 day**; 75/79 are within eight days and none are negative. For 67 Sentry-dated APKs, median lag is **2.994 days**; 53/67 are within eight days and none are negative. The long tail is real: an `11.14.11` alternate has 71.207 days and an `11.14.12.1` alternate 49.422 days.
- A literal date-like value in an APK can be a dependency's own build marker. `build-data.properties` is bundled Google GMSCore metadata; `firebase-crashlytics.properties` is a library-version file; `version.txt` and `builddef.lst` belong to bundled isoparser material. `META-INF/com/android/build/gradle/app-metadata.properties` and `kotlin-tooling-metadata.json` give build-tool versions/settings but no Divar build date. The sampled Mapbox SDK-version asset also supplies only a dependency identifier. They are intentionally excluded as release clocks.
- All 282 v1 signature containers were checked for the PKCS#9 `signingTime` OID: none contain it. APK Signing Blocks were structurally parsed in 268 APKs and none contain either Android SourceStamp block ID (`0x2b09189e` or `0x6dff800d`); the remaining 14 have no APK Signing Block. No `stamp-cert-sha256` ZIP marker is present. Certificate validity dates are certificate lifetime, not signing or publication time.

**Next decisive evidence:** resolve each embedded Git SHA against Divar's source/CI history and match the CI-produced, signed SHA-256 to a Bazaar or Divar upload/rollout record. The matrix supplies independent handles and bounds, but the public APKs alone do not supply those distribution records.
