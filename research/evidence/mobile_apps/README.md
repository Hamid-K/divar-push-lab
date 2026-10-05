# Mobile-app evidence notes

These notes support the [cross-app companion report](../../Iran_mobile_apps_companion.pdf). They identify the exact Balad, Neshan, Snapp and Tapsi APKs behind its principal code findings. The [103-file inventory](../../Iran_mobile_apps_sample_inventory_v2.0.csv) records the full acquired corpus, package tracks, signer fingerprints and date basis.

| App | Selected evidence |
| --- | --- |
| Balad | [Location and radio-observation upload](balad.md) |
| Neshan | [Silent command pull, diagnostic upload and native HTTPS](neshan.md) |
| Snapp | [Driver radio collection, notification polling and updater](snapp.md) |
| Tapsi | [Geolocation request and landing-flavor patch updater](tapsi.md) |

**Reading rule.** An APK hash identifies bytes; a VirusTotal first-submission time dates that hash's appearance in VT. An archive date may describe a listing or upload, not installation of the extracted APK. The Java paths and line numbers below are analyst JADX 1.5.x output from the named files, not developer source. Obfuscated names can change between builds. Native offsets refer to the specified ELF hash. Static reachability does not prove a server enabled the feature, a device made the request, or an actor controlled the route. A matching signing certificate establishes lineage, not release authorization.

This is a compact set of decisive anchors, not a copy of the full decompilation. The route-negative findings concern the reviewed code and acquired files; missing versions and alternate implementations remain outside that boundary.
