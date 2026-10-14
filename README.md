# Divar research and push-handler lab

Independent analysis of the inserted code found in signed Divar Android APKs, with a synthetic cloud-push lab for one observed handler path. The [original analysis by Ramin Farajpour Cami](https://gist.github.com/raminfp/a548a2af86108eb40b8bffc5c8f07aaa) and [Hamid Kashfi's follow-up](https://x.com/hkashfi/status/2106147963332633025) provide the starting context.

## Papers and data

- **Main CTI report** ([FA](research/Divar_backdoor_technical_analysis_fa.pdf) / [EN](research/Divar_backdoor_technical_analysis.pdf)) — signed-APK evidence, push and HTTP routes, code evolution, timeline, and IoCs.
- **Livestream whitepaper** ([FA](research/Divar_livestream_whitepaper_fa.pdf) / [EN](research/Divar_livestream_whitepaper_en.pdf)) — the [Farsi presentation's](https://youtube.com/live/uGGs-6wP0xE) technical findings, wartime context, and app-market accountability.
- **Iranian mobile-app comparison** ([FA](research/Iran_mobile_apps_companion_fa.pdf) / [EN](research/Iran_mobile_apps_companion.pdf)) — bounded code review of Balad, Neshan, Snapp, and Tapsi.
- **[IOC Hunt](research/IOC_Hunt/README.md)** — YARA rules, scanner, exact APK hashes, and retrohunt guidance. [APK inventory](research/Divar_release_marker_matrix.csv) · [checksums](research/SHA256SUMS).

## Lab

A synthetic Android app models the special-push handler in Divar `11.14.20-b`. Real OneSignal or FCM pushes can trigger its receiver **on receipt, without a tap**. The lab replaces the original worker with a fixed local marker and harmless sandbox check. It does not run the Divar app or an exploit. [Evidence and fidelity limits](docs/evidence.md).

### Demo

[![Cloud push demo: emulator, sender, server, and device log](docs/media/video_frame_simulated_lpe_2026-10-04.png)](docs/evidence/onesignal_cli_simulated_lpe_2026-10-04.mp4)

[Watch the 40-second video](docs/evidence/onesignal_cli_simulated_lpe_2026-10-04.mp4) · [Device log](docs/evidence/onesignal_cli_simulated_lpe_2026-10-04.txt)

<a href="docs/media/live_terminal_emulator_2026-10-04.png"><img src="docs/media/live_terminal_emulator_2026-10-04.png" width="300" alt="OneSignal sender, marker server, adb log, and emulator"></a>

### Run

Follow the [Firebase and OneSignal setup](docs/setup.md). With the emulator and marker server running, send the control before the matching push:

```sh
python3 tools/send_onesignal_sample.py title-mismatch
python3 tools/send_onesignal_sample.py accepted
```

The control should not contact the marker server. The matching push should produce one `GET /marker` and app `PASS`, with no privilege change. [Sample messages](docs/sample-events.md) also cover direct FCM and the handler's fields.

[License](LICENSE) · [OneSignal notice](THIRD_PARTY_NOTICES.md)
