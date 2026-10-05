# Historical APK acquisition inventory

**Prepared 5 October 2026.** This is the worklist for extending the [Balad, Neshan, Snapp and Tapsi companion report](../Iran_mobile_apps_companion.pdf) back to the first *observed* Divar 11.8.1 sample. That [exact Divar APK](https://www.virustotal.com/gui/file/ee36859f872cf5cf3723f0cfde50adf5c61409a273ff268d6d0660f83c326a81) reached VirusTotal on 14 May 2023 and [APKPure lists it on 15 May](https://apkpure.net/divar/ir.divar/download/11.8.1). Its version code is not evidence of a February public release.

The current report audited [103 exact APK hashes](../Iran_mobile_apps_sample_inventory_v2.0.csv) across seven package tracks. Those hashes represent 70 distinct package/version/build-code identities. The new [candidate inventory](candidate_apk_inventory.csv) contains **132 additional named version/build targets** for the **15 May 2023–30 September 2026** expansion window: 128 have a dated catalog observation and four Snapp driver leads are undated but bracketed by neighboring versions. At one representative APK per target, that is an acquisition and audit worklist of 132 files if the leads resolve to distinct APKs. Four named earlier checkpoints raise the optional boundary worklist to 136.

| Product / package track | Exact APKs already audited | Additional named targets, May 2023–Sep 2026 | Named earlier checkpoints |
|---|---:|---:|---:|
| Balad Bazaar `ir.balad` | 26 | 14 | 0 |
| Balad Play `com.baladmaps` | 6 | 4 | 1 |
| Neshan `org.rajman.neshan.traffic.tehran.navigator` | 21 | 52 | 1 |
| Snapp passenger `cab.snapp.passenger` | 12 | 22 | 0 |
| Snapp driver `cab.snapp.driver` | 5 | 15 | 2 |
| Tapsi passenger `taxi.tap30.passenger` | 20 | 13 | 0 |
| Tapsi driver `taxi.tap30.driver` | 13 | 12 | 0 |
| **Total** | **103** | **132** | **4** |

The [coverage summary](coverage_summary.csv) is machine-readable. The candidate inventory has 144 rows: 132 in the report expansion window, four earlier checkpoint leads, two October 2026 updates, five distinct-package identity checks, and one undated Tapsi driver lead. Only the 132 rows marked `core` enter the main count.

## What the count means

- A row is a **version/build lead**, not an acquired or audited APK. The `catalog_date` is a store, archive or post observation; it is not a proven first release date. A Telegram caption alone does not establish the embedded Android package, signer, version code or exact bytes.
- The figure **132 is a documented floor, not the number of all released APKs**. Archives omit releases; one version may have several channel or architecture variants and different SHA-256 hashes. Balad Bazaar alone has three version labels with two dated Uptodown entries each. Acquiring those entries may reveal additional distinct files.
- The 103 previously audited hashes are a **file count**, whereas 132 is a **candidate version/build count**. Adding them gives a minimum *representative-sample workload* of 235 if each lead yields one new file, not a complete release corpus.
- No candidate is classified as clean or malicious here. A valid signing certificate would establish continuity of a key, not the absence of inserted code.

## Coverage holes to resolve before claiming a complete timeline

- **Balad:** the visible Bazaar history jumps from July 2023 to December 2024; the Play history jumps from February 2023 to March 2025. The Bazaar track lacks a named pre-May checkpoint.
- **Neshan:** the closest earlier checkpoint is 11.6.1, catalogued 5 April 2023. The first named post-boundary target is 11.8.0, catalogued 10 June 2023. Three 2023 version names have distinct known version codes and therefore separate targets.
- **Snapp:** early passenger records and several later version spans are missing from the visible archives. The passenger `.gp` and `.play` packages are separate identity checks, not silently substituted for `cab.snapp.passenger`. The current-package passenger track lacks a named pre-May checkpoint.
- **Tapsi:** the current-package passenger trail begins with a weak December 2023 metadata lead; the driver trail begins with a June 2024 archive entry. Both need older exact-package files and pre-May checkpoints. The `taxi.tapsi.passengers` entries may represent a separate legitimate lineage; confirm package history before merging them. The PGYER 5.16.5 page reports a 13.9 KB item and an update date that conflicts with a higher version posted earlier, so its chronology is unreliable.

## Use in a future audit

1. Retrieve each candidate and record SHA-256, package ID, version name/code, signing certificate, acquisition URL and first independent observation. If a listing has multiple files, retain each distinct hash.
2. Reconcile package migrations and variants before comparing code. Prioritize the 2023 boundary, the long archive holes, and January–June 2026 before the war-period interpretation is expanded.
3. Diff manifest permissions, push handlers, dynamic loading, update channels, native libraries, location collection and network destinations between adjacent exact files. Preserve ordinary feature explanations and unresolved changes separately from evidence of malicious insertion.
4. Update this ledger as files are acquired; an empty archive search or inaccessible old download does not prove a release never existed.

Sources are recorded on each row of `candidate_apk_inventory.csv`. The main catalogs used were [APKPure Balad Bazaar](https://apkpure.net/%D8%A8%D9%84%D8%AF-%E2%80%93-%D9%86%D9%82%D8%B4%D9%87-%D9%88-%D9%85%D8%B3%DB%8C%D8%B1%DB%8C%D8%A7%D8%A8-%D9%81%D8%A7%D8%B1%D8%B3%DB%8C/ir.balad/versions), [APKPure Balad Play](https://apkpure.net/%D8%A8%D9%84%D8%AF-%D9%85%D8%B3%DB%8C%D8%B1%DB%8C%D8%A7%D8%A8%D8%8C-%D9%86%D9%82%D8%B4%D9%87-balad/com.baladmaps/versions), [APKCombo Neshan](https://apkcombo.com/neshan-map-navigation-app/org.rajman.neshan.traffic.tehran.navigator/old-versions/), [Uptodown Snapp](https://snapp.en.uptodown.com/android/versions), [the Snapp version posts](https://t.me/s/skymitie/35062?q=%23snapp), [the Tapsi version posts](https://t.me/s/skymitie/33377?q=%23tap30), and [PGYER's Tapsi driver listing](https://www.pgyer.com/apk/apk/taxi.tap30.driver/download).
