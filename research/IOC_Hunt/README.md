# Divar IOC and code hunt

**4 October 2026 · Hamid Kashfi · LLM-assisted research bundle**

Use these rules to find the known Divar `ReportDeserializer` lineage and to triage similar Android delivery code in other APKs. The reference set is **282 exact, signature-verified `ir.divar` APKs**: 69 contain a complete inspected route to the worker and 213 lack the inspected known routes. A rule hit identifies bytes to review. It does **not** prove that a device received a hostile push, an API response header, a second stage or an exploit.

## Start here

1. Use Python 3.11+ and install [YARA](https://virustotal.github.io/yara/) or `yara-python`: `python3 -m pip install yara-python`.
2. Scan a directory of APKs or raw DEX files:

   ```sh
   python3 tools/scan_apk_dex.py --output hits.csv /path/to/apks
   ```

3. Review `hits.csv` by **APK SHA-256**, then decompile every matching DEX and check the ingress, receiver, URL decoder and worker as one connected path. A direct `yara rules/divar_dex_hunt.yar app.apk` scan normally misses these rules: APKs compress their `classes*.dex` members, and every rule requires DEX magic. The helper scans decompressed DEX members. Extract the base APK from an XAPK before using this helper.

The primary [`divar_dex_hunt.yar`](rules/divar_dex_hunt.yar) contains four class-anchored Divar lineage rules and five class-neutral triage rules. [`historical_retrohunts.yar`](rules/historical_retrohunts.yar) preserves the three original VT job rules verbatim; its broad rule returned thousands of unrelated leads and is **not** recommended for a new full-corpus job. `yarac` compiled both files on YARA 4.5.8. The helper was tested with `yara-python` 4.5.2.

## Retrohunt and the 90-day boundary

Paste the selected YARA file into **VT Hunting → New Retrohunt job**, choose the `main` corpus, and run VT's hash test on the DEX hashes in [`test_vectors.csv`](validation/test_vectors.csv) before spending a full job. Resolve DEX matches through **Relations → Compressed parents** and verify the parent APK's package, versionCode and certificate. The prior selective jobs' exported matches are in [`retrohunt_resolved.json`](evidence/retrohunt_resolved.json); their owner-only job pages are not a substitute for this export. [VT Retrohunt guide](https://docs.virustotal.com/docs/retrohunt); [compressed-parent relationship](https://docs.virustotal.com/reference/file-object-compressed-parents).

**The rules do not remove VT's account limit.** VT documents a three-month Retrohunt range for standard access and up to 12 months for Hunting Pro. Even the documented Pro range will not reach the 2023 Divar samples from October 2026. To reach older releases, peers need their own historical APK/DEX corpus or an appropriately entitled source; scan archived APKs locally with the helper. Use Livehunt for future submissions. VT also excludes files over 100 MB from Retrohunt and caps each job's matches at 10,000. [VT limits](https://docs.virustotal.com/docs/retrohunt). Exact known hashes and archive-source URLs in this bundle help reacquire old files without depending on a current content-search window.

## Rule calibration

Counts below are **APK-level** matches after scanning each decompressed DEX. They describe this acquired reference set, not detection rates in VT or all Android apps. No primary rule matched the 213 known-route-negative Divar APKs. A separate local check of 59 unrelated Balad, Neshan, Snapp and Tapsi APK containers (779 DEX members) produced no primary-rule hits. The exact procedure and rule-file digest are in [`local_calibration.json`](validation/local_calibration.json).

| Rule | Matching route-positive APKs | What it locates |
| --- | ---: | --- |
| `DIVAR_Dex_ReportDeserializer_Exact` | 69 / 69 | Exact class plus instruction-schema strings; best known-family starting point. |
| `DIVAR_Dex_Worker_PlainURL_Candidate` | 6 / 6 sampled plain-URL builds | Known worker schema without either sampled XOR loop; confirm URL handling in code. |
| `DIVAR_Dex_Worker_XOR63_Candidate` | 38 / 38 sampled XOR-63 builds | 2023–25 worker opcode candidate. |
| `DIVAR_Dex_Worker_XOR104_Candidate` | 25 / 25 sampled XOR-104 builds | 2026 worker opcode candidate. |
| `ANDROID_Dex_ReflectiveStageSchema_Triage` | 69 / 69 | Class-neutral network/reflection/instruction-schema lead; inspect method-level flow. |
| `ANDROID_Dex_PushRelay_Opcode_Triage` | 62 / 68 push-route builds | Sender/receiver Dalvik instruction layout; misses six earlier plain-URL builds. |
| `ANDROID_Dex_XOR63_Schema_Triage` | 38 / 38 XOR-63 builds | Class-neutral schema and exact XOR opcode; possible cross-app lead. |
| `ANDROID_Dex_XOR104_Schema_Triage` | 25 / 25 XOR-104 builds | Class-neutral schema and exact XOR opcode; possible cross-app lead. |
| `ANDROID_Dex_HTTP_ResponseHeader_Triage` | 22 / 22 header-route builds | `X-CORRELATION-ID`, Base64 and explicit broadcast co-occurrence; confirm response interception and XOR-100 in code. |

Compiler register allocation, obfuscation, string changes and split DEX layouts can defeat a rule. A match in one DEX does not prove the strings or opcodes are connected in one method. A miss does not clear a release or a different implementation. Use the [code-flow checklist](evidence/code_flow_checklist.md) and [`release_inventory_reference.csv`](evidence/release_inventory_reference.csv) to verify candidates in exact signed APKs.

OneSignal and Firebase SDK presence alone are not discriminating indicators; the rules target the unusual relay, decoder and worker path. The HTTP header name by itself can also be legitimate.

## Files and triage order

- [`indicators/focused_iocs.csv`](indicators/focused_iocs.csv): 69 route-positive signed APK hashes and three clearly labeled behavioral pivots. Its `date_basis` field distinguishes VT first-submission time from two Uptodown archive `lastUpdate` dates; neither is an infection or release date. [`route_positive_apk_sha256.txt`](indicators/route_positive_apk_sha256.txt) is the hash-only form. Negative-control hashes are kept out of this IoC list.
- [`evidence/release_inventory_reference.csv`](evidence/release_inventory_reference.csv): 282-row source and status reference without local filesystem paths. A route-negative entry means the **inspected known routes** are absent, not that the entire app is benign.
- [`queries/vt_intelligence.md`](queries/vt_intelligence.md): copyable VTGrep and inventory queries with selectivity notes.
- [`evidence/prior_retrohunt_results.md`](evidence/prior_retrohunt_results.md): completed historical job counts, including a noisy rule and one non-Divar candidate requiring code review.
- [`evidence/code_flow_checklist.md`](evidence/code_flow_checklist.md): the push, response-header, receiver and worker conditions that a candidate must satisfy.
- [`validation/test_vectors.csv`](validation/test_vectors.csv): exact APK/DEX hashes for local or VT hash tests, including split-DEX and negative controls.

For every new hit: preserve the exact file and SHA-256; establish package, versionCode, signature and acquisition date basis; map all DEX to the same APK; follow the push or response-header branch through the receiver into the worker; distinguish static capability from a recovered delivery event. Add an indicator to a case only after that review. This folder contains no APK binaries, API keys or local absolute paths.
