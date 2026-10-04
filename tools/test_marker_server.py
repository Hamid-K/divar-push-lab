"""Regression tests for the intentionally narrow local marker endpoint."""

import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

from marker_server import HOST, make_server


class MarkerServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = make_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://{HOST}:{cls.server.server_port}"
        cls.opener = build_opener(ProxyHandler({}))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_fixed_marker_response(self) -> None:
        with self.opener.open(self.base_url + "/marker") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get_content_type(), "application/json")
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertEqual(json.load(response), {
                "kind": "lab-marker",
                "message": "benign",
                "stage": "simulated-lpe",
            })

    def test_other_paths_and_query_strings_are_rejected(self) -> None:
        for path in ("/", "/payload", "/marker?url=https://example.com"):
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as raised:
                    self.opener.open(self.base_url + path)
                self.assertEqual(raised.exception.code, 404)

    def test_upload_is_rejected(self) -> None:
        request = Request(
            self.base_url + "/marker", data=b"payload", method="POST"
        )
        with self.assertRaises(HTTPError) as raised:
            self.opener.open(request)
        self.assertEqual(raised.exception.code, 405)

    def test_bind_is_loopback_only(self) -> None:
        self.assertEqual(self.server.server_address[0], HOST)


if __name__ == "__main__":
    unittest.main()
