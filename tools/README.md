# Local marker endpoint

The lab app makes one request to the emulator's host alias, `http://10.0.2.2:18765/marker`. This Python standard-library server binds only to `127.0.0.1:18765` on the host and returns the same harmless JSON every time:

```json
{"kind":"lab-marker","nonce":"divar-lab","message":"benign"}
```

It accepts only `GET /marker`. Other paths return 404, and uploads are rejected. It serves no APK, executable, script, or caller-selected content. The Android emulator maps `10.0.2.2` to the host loopback interface; the endpoint is for a local emulator, not a physical phone.

From the repository root, start the server in one terminal:

```sh
python3 tools/marker_server.py
```

Check it from the host:

```sh
curl --fail --silent http://127.0.0.1:18765/marker
```

Run its regression tests:

```sh
python3 -m unittest discover -s tools -p 'test_*.py'
```

Stop the server with Ctrl-C when the lab is finished.
