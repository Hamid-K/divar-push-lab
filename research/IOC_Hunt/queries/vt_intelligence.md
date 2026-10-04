# VirusTotal Intelligence queries

These are **candidate locators**, not verdicts. Paste one line at a time into VT Intelligence. `content:` is case-sensitive and VTGrep can search unpacked content; inspect the match context and the DEX file's **Relations → Compressed parents** before assigning a hit to an APK. A zero-result query does not clear an app or a historical period. [VTGrep syntax and unpacking](https://docs.virustotal.com/docs/vtgrep).

| Purpose | Query | Triage note |
| --- | --- | --- |
| Exact known Divar class descriptor | `tag:dex content:"Lir/divar/chat/util/ReportDeserializer;"` | High-value family lead; confirm class definition and connected route in the parent signed APK. |
| Divar APK inventory | `androguard_package:ir.divar type:apk` | Inventory query only; then compare exact hashes/versionCodes with `evidence/release_inventory_reference.csv`. Account history limits apply. |
| Worker schema without the class name | `tag:dex content:"objectify" content:"deserialize" content:"report" content:"local" content:"getMethod" content:"openConnection"` | Can find renamed/cross-app candidates, but `content:` also matches substrings such as `objectifyMap`. Verify exact strings and data flow. |
| Push-body constellation | `tag:dex content:"push_id" content:"callback_url" content:"campaign" content:"ChatPushNotificationOpenHandler"` | Can also match route-negative Divar builds; a sender branch must be decompiled. |
| HTTP response-header candidate | `tag:dex content:"X-CORRELATION-ID" content:"setClassName" content:"sendBroadcast"` | Header string may be legitimate; verify it is read from a **response**, decoded and relayed. |
| Header decoder byte lead | `tag:dex content:"X-CORRELATION-ID" content:{DF ?? ?? 64} content:"setClassName" content:"sendBroadcast"` | XOR-100 Dalvik opcode lead; register allocation and unrelated code can change the bytes. |

Do not combine `androguard_package:` with `content:` in the same query: the signed-in VT interface rejected that combination during this investigation. `type:apk content:...` searches can surface extracted DEX matches; treat the result type and parent relationship as evidence to inspect, not as an APK verdict. [VT search modifiers](https://docs.virustotal.com/docs/file-search-modifiers).

The [69 route-positive APK hashes](../indicators/route_positive_apk_sha256.txt) are exact pivots. The [public release reference](../evidence/release_inventory_reference.csv) keeps negative controls and source URLs separate from the IoC list. Exact hashes can be looked up even where a content query or current search window fails to return them.
