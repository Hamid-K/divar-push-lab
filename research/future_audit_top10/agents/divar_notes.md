# Divar source and coverage notes

- Package track: `ir.divar`.
- Source: the existing signed-APK [release ledger](/Users/hamid/Documents/DFIR/Divar/vt-research-2026-10-03/deep_analysis_2026-10-04/release_ledger.csv), which records exact SHA-256 hashes, VirusTotal links and observation dates, archive dates, package IDs, signer hashes, and local file paths. Every one of its 282 recorded APK paths exists locally as of 5 October 2026.
- Export: 282 distinct APK-hash rows, representing 225 displayed version names and 228 version-name/version-code pairs. Of these, 118 APK rows have an observation dated 2023 or later.
- Dates are the ledger's observation dates, usually VirusTotal first submission or an archive listing. They are **not** proven release dates. The embedded version code must not be decoded into a release date.
- Different hashes sharing a displayed version and code remain separate rows. They may be channel, packaging, or content variants and require individual comparison.
- The ledger's 203-entry Uptodown archive extract contributes no version names missing from the signed-APK ledger; this is a statement about that extract, not proof that every Divar release was recovered.
- The inventory includes pre-2023 rows because the user requested all available historical versions. The intended cross-app audit window is 1 January 2023 through 5 October 2026.
