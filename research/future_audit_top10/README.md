# Version inventory for ten Iranian Android apps

**Compiled 5 October 2026.** This inventory covers the ten apps in the [28 September Tehran Index tracked-app ranking](https://tehranindex.com/analytics): Divar, Rubika, Eitaa, Snapp, Neshan, Telewebion, Balad, Digikala, Aparat, and Baam. That ranking is a **64-app Café Bazaar sample**, not a nationwide top ten. The version inventory uses an audit window of **1 January 2023 through 5 October 2026**, with older observed versions retained as baselines.

This is an inventory of **observable version records**, not a complete publisher release log. A missing year or version means it was not found in the checked sources; it does not mean the publisher shipped nothing. No new APKs were downloaded for this inventory pass. Existing exact Divar and mobility samples are indexed alongside catalog-only leads.

## Files

- [observed_versions.csv](observed_versions.csv) — 714 source-linked observations. Each row preserves its package, version, date type, URL, artifact type, and SHA-256 if recorded.
- [version_targets.csv](version_targets.csv) — 636 package/version-code/variant targets collapsed from those observations. A target can still have several distinct APK hashes or architecture splits.
- [in_window_acquisition_targets.csv](in_window_acquisition_targets.csv) — the 217 first-observed-in-window targets without a locally held exact APK sample.
- [coverage_summary.csv](coverage_summary.csv) and [observation_years.csv](observation_years.csv) — coverage by package track and observation year.
- [acquisition_queue.csv](acquisition_queue.csv) — 367 source observations without locally held exact bytes, including pre-2023 baselines and repeat listings. It is a retrieval worklist, **not** a count of distinct APK files.
- [agents](agents) — per-group source and gap notes, plus the source CSVs. [build_inventory.py](build_inventory.py) rebuilds the combined CSVs from those inputs.
- [SHA256SUMS](SHA256SUMS) — checksums for the inventory files.

## Coverage at a glance

“In window” below means the **first dated observation in this inventory** falls in 2023–2026. It does not establish the original release date. “Local samples” means the existing research holds exact APK bytes for at least one row of that target. Different packages and variants remain separate.

| App | Observed target identities, all dates | First observed in window | In-window targets with local APK | In-window targets needing APK |
|---|---:|---:|---:|---:|
| Divar | 228 | 103 | 103 | 0 |
| Rubika | 9 | 6 | 0 | 6 |
| Eitaa | 10 | 9 | 0 | 9 |
| Snapp | 54 | 33 | 8 | 25 |
| Neshan | 64 | 64 | 10 | 54 |
| Telewebion | 100 | 37 | 0 | 37 |
| Balad | 58 | 52 | 24 | 28 |
| Digikala | 66 | 21 | 0 | 21 |
| Aparat | 36 | 30 | 0 | 30 |
| Baam | 11 | 7 | 0 | 7 |
| **Total** | **636** | **362** | **145** | **217** |

The 714 observations comprise **401 dated within the audit window**, **305 earlier baselines**, and **8 undated leads**. The 636 targets comprise **362 first observed in window**, **266 first observed before 2023**, and **8 undated**. The 217 missing-local-sample targets are a **documented acquisition floor**, not the number of all APKs ever released. Some archive targets may prove unavailable, and some displayed versions have multiple legitimate files.

## What can and cannot be inferred

- `observed_date` is a source observation: VirusTotal first submission, store last-update field, archive upload/listing, sample-scanner field, or a dated announcement. `date_type` says which. **None alone proves developer publication, user delivery, or malicious use.** Version codes are kept as identifiers, never decoded into release dates.
- `source_url` supports the individual row. A third-party page's package/version claim remains metadata until an APK manifest is read. The `artifact_type` and source notes identify page-published hashes separately from locally verified bytes.
- A matching app name is insufficient. Balad has `ir.balad` and `com.baladmaps`; Digikala has `com.digikala` and `com.digikala.diagon`; Snapp has passenger `.gp` and `.play` identity leads separate from `cab.snapp.passenger`. These are not silently merged. Driver apps are outside this ten-app scope.
- A valid signer would establish continuity of a signing key, not a clean build. This inventory **does not classify** newly listed apps or versions as compromised or clean.
- The historical sources are uneven. Rubika and Eitaa have particularly sparse package-linked records. Baam has no dated 2025 package-matched observation here. Balad's Play package has no 2024 observation; Balad's Bazaar package has one in 2023 and one in 2024. These are **source coverage gaps**.
- A fresh VirusTotal package search could not be completed in this pass: the CLI could not resolve the VT host, and the browser security policy denied access to the signed-in VT tab. Existing VT-backed records from the earlier local ledgers remain included; no additional VT matches were inferred.

## Source notes and next audit pass

- [Divar](agents/divar_notes.md): an existing 282-file signed-APK ledger supplies 225 displayed versions from 2013 onward. Every indexed Divar hash refers to a locally present APK.
- [Snapp, Neshan, Balad](agents/mobility_notes.md): existing audited APKs were reconciled with the previous acquisition worklist and new package-specific archive leads. A published SHA-256 with no downloaded file is **not** counted as a local sample.
- [Rubika, Eitaa, Telewebion](agents/media_notes.md): package-linked store, sample-scanner, archive and announcement evidence; brand-only lookalikes are listed in the notes rather than assigned to an official package.
- [Digikala, Aparat, Baam](agents/commerce_notes.md): archive and current-store leads; no APK bytes acquired in this pass. Baam's press and fan-post version labels without package proof stay in the notes.

For a future audit, retrieve the 217 in-window targets without a local sample, starting with 2023 boundary coverage and the long gaps above. For each file, retain the exact APK/XAPK/APKS bytes, SHA-256, manifest package and version code, split set, signer fingerprint, retrieval URL and timestamp. Then compare adjacent exact files for permissions, push ingress, dynamic loading, native code, location collection, and off-band network destinations. Keep ordinary product changes and unresolved differences separate from evidence of malicious insertion.
