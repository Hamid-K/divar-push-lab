# Prior VT Retrohunt runs

Three jobs were run on the then-available **90-day** corpus on 3 October 2026. Their original rules are preserved verbatim in [`rules/historical_retrohunts.yar`](../rules/historical_retrohunts.yar). The selective jobs' DEX-to-compressed-parent mapping is exported in [`retrohunt_resolved.json`](retrohunt_resolved.json); VT job pages may be visible only to their owner. These counts are completed job outputs, not a population estimate for older releases.

| Rule / job | Finished result | Interpretation |
| --- | --- | --- |
| `android_xor_payload_schema_triage` / `malshare_hk-1790992037` | 5,777 DEX matches | Broad and noisy; unsuitable as a stand-alone APK verdict. |
| `android_xor_payload_schema_strict` / [`malshare_hk-1790992481`](https://www.virustotal.com/gui/hunting/retrohunt/matches/malshare_hk-1790992481) | 12 DEX matches | Eleven mapped to Divar parent APKs. One mapped to `com.swisscom.myswisscom`; its Divar-like control flow was **not** established. |
| `divar_push_relay_triage` / [`malshare_hk-1790993123`](https://www.virustotal.com/gui/hunting/retrohunt/matches/malshare_hk-1790993123) | 10 DEX matches | All mapped to Divar parent APKs. |

The two selective outputs combined to 14 unique DEX hashes and 17 parent file hashes in the preserved mapping. The match count measures rule hits in the accessible VT window, not the number of infected app installations or attacked users. The [new calibrated rules](../rules/divar_dex_hunt.yar) add 2023 plain/XOR-63 and 2026 header coverage, but have **not** been submitted as new VT jobs in this bundle. [VT Retrohunt documentation](https://docs.virustotal.com/docs/retrohunt).
