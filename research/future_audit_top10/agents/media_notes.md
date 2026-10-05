# Media and messenger Android version inventory

**Audit window:** 2023-01-01 through 2026-10-05 inclusive. The CSV also records directly observed earlier builds as `pre_2023_baseline` and undated versions as `undated_unknown`. This is an inventory of **observed archive/store records**, not a claim that every release was captured or that any APK was audited.

## Coverage at handoff

| App and exact package | CSV records | Distinct version names | Dated in window | Pre-2023 records | Undated |
|---|---:|---:|---:|---:|---:|
| Rubika `app.rbmain.a` | 9 | 8 | 6 | 0 | 3 |
| Eitaa `ir.eitaa.messenger` | 10 | 10 | 9 | 0 | 1 |
| Telewebion `net.telewebion` | 101 | 60 | 38 | 63 | 0 |
| **Total** | **120** | **78 app/version pairs** | **53** | **63** | **4** |

The 101 Telewebion records include architecture variants, different build codes under one version name, and source-specific records for the same version. They are **not** 101 release events. No APK bytes were downloaded or locally hashed in this pass. The `sha256` field contains only **APK file hashes printed by an archive page**; it never contains a signing-certificate hash. For example, [APKMirror's 5.2.3 page](https://www.apkmirror.com/apk/simraco/telewebion/telewebion-5-2-3-release/telewebion-5-2-3-android-apk-download/) separately lists the signer certificate SHA-256 and an APK file SHA-256. APKMirror's page also says it cannot currently offer a direct download for this app, so its hashes are useful lookup targets, not locally verified bytes.

## Source handling and date meaning

- **Package gate:** a main CSV row needs a source page or a same-post store link explicitly tying the version to `app.rbmain.a`, `ir.eitaa.messenger`, or `net.telewebion`. A brand-only result is recorded below as a lead, not silently assigned a package. A stated package on an archive page is **metadata** until an acquired file's manifest and signature are checked.
- **Date fields:** `store_last_update_date` is the store's displayed field; `third_party_reported_store_last_update_date` is Certfa's displayed "last app update" field; `archive_upload_date` and `archive_file_date` are archive dates; and `third_party_reported_update_date` is a repost's claim. None is independently proven to be the developer's first publication date. Jalali dates were converted to ISO/Gregorian in the CSV, with the original date retained in notes for key rows.
- **Artifact types:** "listing" and "page hash" mean no bytes were acquired. APK/XAPK/APKS format was retained when shown. Version codes from archive metadata or filenames are unverified until compared with an Android manifest. Architecture/rounded size in `variant` distinguishes otherwise indistinguishable archive entries without claiming their SHA-256 differs.
- **Scope:** older Telewebion entries are preserved because [APKCafe's package-labelled product page](https://telewebion.apkcafe.in/) exposes build codes/variants back to 2017. The main audit window remains 2023 onward; many of those older records are context baselines only.

## Per-app findings and gaps

### Rubika

The [Café Bazaar listing](https://cafebazaar.ir/app/app.rbmain.a) currently identifies `app.rbmain.a` version **4.1.1**, last updated 29 Shahrivar 1405 (2026-09-20). [Myket](https://myket.ir/app/app.rbmain.a) displays **3.9.8**, last updated 1404/08/07 (2025-10-29); this is a different/stale store view, not proof of a rollback. [Certfa's sample report](https://certfa.com/lab/android-app/sha1/60efafb94adcdb16f7a7ea80b760c80827669e88/) ties **3.7.3** to the exact package and shows an app last-update field of 31 Tir 1403 (2024-07-21). Certfa does not show a report publication/analysis timestamp, and its displayed 32-character checksum is not a SHA-256.

[Certfa also has a 3.6.4 sample report](https://certfa.com/lab/android-app/sha1/dc70156038e32e2941d0a00442659ec0df3dd3d1/) with the exact package, a **75.4 MB** sample, and a source-reported app last-update field of 1 Bahman 1402 (2024-01-21). This is a separate source record from [PGYER's package-specific archive](https://www.pgyer.com/apk/apk/app.rbmain.a/download), which lists **3.6.4, 3.3.2, 3.1.1, 3.0.7**. The [PGYER 3.6.4 build page](https://www.pgyer.com/app/build/ykb0w7viss) claims build code **364** and 2024-07-12, but the displayed file is only about 9.8 KB; it may be a stub or bad record. Older PGYER entries expose no usable dates (some show 1970 placeholders). The large gaps between 2023 and 2026 remain unfilled.

The **4.0.5** row is lower confidence: a search-indexed snapshot of [Yekmod's page](https://www.yekmod.com/rubika/) explicitly paired `app.rbmain.a` with 4.0.5 and 1 Shahrivar 1405 (2026-08-23), but the live page has since been overwritten with 4.1.1. Acquire a dated snapshot or the exact APK before treating it as a byte-level target.

**Excluded identity leads:** [P30Plus's old-version page](https://www.p30plus.org/old-version-rubika/) names 3.6.4, 3.5.2, 3.4.3, 3.3.8, 3.3.7, 3.3.3, 3.2.9, 2.9.7, 2.1.2, 1.4.9, 1.1.2, and 1.0.8, but does not state a package for those APK files and some download paths are odd. Its 3.6.4 overlaps the package-labelled PGYER record; the others are not in the main CSV. [Uptodown's Rubika-branded listing](https://rubika.en.uptodown.com/android) is a different PSKY package, `ir.resaneh1.iptv`, and must **not** be merged with `app.rbmain.a`. The brand-only 3.8.1/3.8.2/3.9.4 results from general download blogs remain unresolved until package/signature inspection.

### Eitaa

[Myket](https://myket.ir/app/ir.eitaa.messenger) shows the exact package at **7.1.2**, last updated 1405/06/22 (2026-09-13). Certfa has package-labelled sample reports for [6.3.4](https://certfa.com/lab/android-app/sha1/237643bada0063c05b94e307c43fe0292758cd14/) and [6.3.7](https://certfa.com/lab/android-app/sha1/f0d84fc1b8c9b3fc8afb658ce27a0fa4340f741c/), whose source-reported app last-update fields are 11 Shahrivar 1402 (2023-09-02) and 11 Aban 1402 (2023-11-02). These dates are not Certfa report publication dates.

[SalehiApps' archived posts](https://t.me/s/SalehiApps?before=1091&q=%23%D9%86%D8%B3%D8%AE%D9%87_%D8%AC%D8%AF%DB%8C%D8%AF_%D8%A7%DB%8C%D8%AA%D8%A7) list **6.3.1, 6.4.14, 6.6.2** and link the exact `ir.eitaa.messenger` Bazaar/Myket path in the same post; the [later archive](https://telegram.me/s/SalehiApps?after=1170) similarly links the exact store path for **6.7.10** and **7.1**. The [6.2 post](https://t.me/s/SalehiApps?before=756) links the exact Myket path. These posts claim official-source APK attachments, but no attachment manifest, signer, or hash was verified here. The **2451** and **24401** build numbers were parsed from reposted filenames only; `24401` may be a filename convention or typo (another repost says `2440`).

**Excluded identity leads:** [Gooyatech 6.5.12](https://gooyatech.com/download-eitaa-messenger/) and [IranApp 6.4.22](https://iranapp.me/eitaa/) describe the Eitaa brand but do not visibly pair the advertised version with `ir.eitaa.messenger`; their files need inspection before joining the official-package inventory. An [APKPure "Eitaa" result](https://apkpure.com/search?q=Eitaa) associates a 2018 `20.0.10` item with a different StartAd app; do not treat it as Eitaa's release line. Official Eitaa direct-download URLs were inaccessible to this reader during collection.

[PGYER's package-specific page](https://www.pgyer.com/apk/apk/ir.eitaa.messenger/download) lists an undated **4.2** under `ir.eitaa.messenger`. It labels the publisher “StartAd App,” which conflicts with Myket/Certfa's developer attribution, so this is a low-confidence metadata lead. A [community post](https://t.me/s/eitaafans?after=460) names an `eitaa_4.2(1656).apk` attachment, but 1656 is only a filename number and was not imported into the CSV `version_code` field.

### Telewebion

[Myket](https://myket.ir/app/net.telewebion) lists exact package **5.3.7** last updated 1405/07/04 (2026-09-26). [Uptodown's package-labelled product page](https://telewebion.en.uptodown.com/android) lists its own 5.3.7 APK dated 2026-09-21 with a page-published SHA-256 and an older 5.3.6. [Uptodown's archive](https://telewebion.en.uptodown.com/android/versions), its [older Arabic snapshot](https://telewebion.ar.uptodown.com/android/versions), [APKPure's version search result](https://apkpure.net/telewebion/net.telewebion/versions), [APKMirror](https://www.apkmirror.com/apk/simraco/telewebion/), and [APKCafe](https://telewebion.apkcafe.in/) broaden the history. Direct retrieval of the APKPure version page timed out; its version/code/date rows came from its indexed result rather than a successfully opened page.

Archive dates conflict frequently. Examples: APKMirror uploads **4.4.3** in September 2022 while Uptodown shows a later February 2024 copy; APKCafe uploads **4.3.5** in April 2022 while Uptodown later lists it in July 2025. This is why the CSV uses date types and does not read archive timestamps as original release dates. APKCafe's 4.3.2 entries even show **two version codes, 174 and 175**, under one version name; they are preserved separately.

The [Aptoide version list](https://telewebion.ar.aptoide.com/versions) was checked but does not display `net.telewebion` on that page, so its older **3.4, 2.6.4, 2.5.3** rows were excluded as an independent source. Those same version names are now package-lineage leads through APKCafe, which explicitly states `net.telewebion` on its product page. APKMirror's SHA-256 values in the CSV are **APK file hashes** under “APK file hashes,” not the shared signer certificate SHA-256 (`8039819a…`). APKMirror says direct APK downloads for this app are currently unavailable; Uptodown/APKCafe are potential acquisition paths, but their files still require manifest, signer, and SHA-256 verification.

## Next acquisition pass

1. Save the exact APK/XAPK/APKS bytes for each in-window version and at least one adjacent pre-window baseline. Record local SHA-256, Android `versionCode`, package ID, signer fingerprint, file size, split structure, and source URL. Keep source variants separate if hashes differ.
2. Prioritize Rubika and Eitaa historical gaps. Obtain a dated copy of the overwritten Rubika 4.0.5 page/APK, then inspect brand-only archive leads strictly by manifest package and signer. Do not equate a matching signer with a clean build.
3. For Telewebion, acquire the package-labelled archive variants around 2023–2026, reconcile archive republish dates against store history, then diff requested sensitive permissions and code paths on **exact bytes**.
