# Mobility app version inventory — 5 October 2026

The companion CSV is an **observed archive and exact-file inventory**, not a complete publisher release ledger. It covers Snapp passenger, Neshan, and the two Balad Android package tracks. The audit window is **1 January 2023–5 October 2026**. Directly observed older entries are marked `pre_2023_baseline`.

| Package | In-window rows | Distinct observed version/build identities | Identities with audited APK hash | Catalog-only identities |
|---|---:|---:|---:|---:|
| `cab.snapp.passenger` | 35 | 31 | 8 | 23 |
| `cab.snapp.passenger.gp` | 2 | 2 | 0 | 2 |
| `cab.snapp.passenger.play` | 0 | 0 | 0 | 0 |
| `ir.balad` (Bazaar) | 44 | 33 | 18 | 15 |
| `com.baladmaps` (Play) | 16 | 16 | 6 | 10 |
| `org.rajman.neshan.traffic.tehran.navigator` | 75 | 64 | 10 | 54 |
| **Total** | **172** | **146** | **42** | **104** |

The full CSV has **199 rows**, including **27 pre-2023 baseline rows**. Its 66 in-window SHA-256 rows include **65 audited exact APKs** across 42 package/version/build identities and **one APKMirror-published hash** for Snapp 8.33.0 that has not been acquired or audited. Several labels have more than one exact APK. A catalog-only row is an acquisition lead, **not** an audited or confirmed clean APK.

## Provenance

- Exact-file records come from the [previous 103-file audited sample ledger](../../divar-push-lab/research/Iran_mobile_apps_sample_inventory_v2.0.csv), which preserves per-file VT or archive URLs, package IDs, version codes and SHA-256 values. Only the three named apps and their passenger/navigation tracks were imported; the Snapp driver package was excluded from this top-ten app inventory.
- Catalog-only records come from the [previous candidate worklist](../../divar-push-lab/research/future_audit_2023_2026/candidate_apk_inventory.csv). Each original source URL and date basis is retained. Where one row held two Uptodown archive dates, it is split into two observations; identical labels at two dates are **not** presumed to be distinct APK bytes.
- Newly appended public listings include [Snapp on Uptodown](https://snapp.en.uptodown.com/android/versions), [Balad Bazaar on APKPure](https://apkpure.net/%D8%A8%D9%84%D8%AF-%E2%80%93-%D9%86%D9%82%D8%B4%D9%87-%D9%88-%D9%85%D8%B3%DB%8C%D8%B1%DB%8C%D8%A7%D8%A8-%D9%81%D8%A7%D8%B1%D8%B3%DB%8C/ir.balad/versions), [Balad Play on APKPure](https://apkpure.net/%D8%A8%D9%84%D8%AF-%D9%85%D8%B3%DB%8C%D8%B1%DB%8C%D8%A7%D8%A8%D8%8C-%D9%86%D9%82%D8%B4%D9%87-balad/com.baladmaps/versions), [Balad Play on Uptodown](https://balad.en.uptodown.com/android/versions), [Neshan on APKCombo](https://apkcombo.com/neshan-map-navigation-app/org.rajman.neshan.traffic.tehran.navigator/old-versions/), and a [Neshan 14.14.0.4 third-party lead](https://www.yekmod.com/neshan/). These appended entries have no verified file hashes.

## Interpretation and gaps

- `observed_date` is the stated **archive listing/upload date** or **VT first-submission date**. Neither proves when a developer published a build, when users received it, or when any code first appeared.
- Package IDs remain distinct. Balad `ir.balad` and `com.baladmaps` are different distribution tracks. Snapp `cab.snapp.passenger`, `.gp`, and `.play` must not be collapsed into a common signing or byte lineage.
- The catalogue is sparse in parts: Balad Bazaar has only one named 2023 and one 2024 entry; Balad Play has no named 2024 entry; Snapp's main passenger package begins with a July 2023 listing and has a long 2017–2023 archive gap. These are **coverage gaps**, not evidence that intervening builds did not exist.
- Some old Balad Play version labels have 2025–2026 Uptodown dates. Those dates may reflect later archive ingestion or file modification; they are retained as observations, not interpreted as new releases.
- `14.14.0.4` for Neshan is a lower-confidence third-party XAPK listing with no checked version code or SHA-256. It should be resolved against a publisher/store copy before audit.
- A future exact-file audit should retrieve the 104 catalog-only identities first, then identify architecture, channel and same-version build variants. The number of remaining **APKs** can exceed 104.
