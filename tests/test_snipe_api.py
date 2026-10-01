"""Contract tests for scripts/snipe_api.py using only fictitious data."""

import json
import importlib.util
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "snipe_api.py"
SPEC = importlib.util.spec_from_file_location("snipe_api_under_test", SCRIPT)
API = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(API)


class _Handler(BaseHTTPRequestHandler):
    requests = []
    response_status = 200
    response_body = b'{"status":"success","payload":{"fixture":true}}'
    response_headers = {}

    def _handle(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        type(self).requests.append(
            (self.command, self.path, dict(self.headers), body)
        )
        self.send_response(type(self).response_status)
        for key, value in type(self).response_headers.items():
            self.send_header(key, value)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(type(self).response_body)

    do_GET = _handle
    do_POST = _handle
    do_PATCH = _handle
    do_PUT = _handle
    do_DELETE = _handle

    def log_message(self, *_args):
        pass


class SnipeApiCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = "http://127.0.0.1:%d" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        _Handler.requests.clear()
        _Handler.response_status = 200
        _Handler.response_body = b'{"status":"success","payload":{"fixture":true}}'
        _Handler.response_headers = {}

    def run_cli(self, *args, env_updates=None):
        env = os.environ.copy()
        env.pop("SNIPE_IT_URL", None)
        env.pop("SNIPE_IT_TOKEN", None)
        env.update({"SNIPE_IT_URL": self.url, "SNIPE_IT_TOKEN": "fake-test-token"})
        if env_updates:
            env.update(env_updates)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=8,
        )

    def test_get_sends_path_query_and_auth(self):
        result = self.run_cli(
            "GET", "hardware", "--param", "limit=2", "--param", "search=demo asset"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(_Handler.requests), 1)
        method, path, headers, _ = _Handler.requests[0]
        self.assertEqual(method, "GET")
        self.assertTrue(path.startswith("/api/v1/hardware?"))
        self.assertIn("limit=2", path)
        self.assertIn("search=demo+asset", path)
        self.assertEqual(headers.get("Authorization"), "Bearer fake-test-token")
        self.assertNotIn("fake-test-token", result.stdout + result.stderr)

    def test_base_url_subpath_is_preserved(self):
        result = self.run_cli(
            "GET", "hardware", env_updates={"SNIPE_IT_URL": self.url + "/inventory"}
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(_Handler.requests[0][1].split("?", 1)[0],
                         "/inventory/api/v1/hardware")

    def test_mutation_is_plan_without_apply_and_apply_sends_json(self):
        data = '{"name":"Fixture Asset","asset_tag":"TEST-001"}'
        planned = self.run_cli("POST", "hardware", "--data", data)
        self.assertEqual(planned.returncode, 0, planned.stderr)
        self.assertEqual(_Handler.requests, [])
        self.assertIn("Fixture Asset", planned.stdout)

        applied = self.run_cli("POST", "hardware", "--data", data, "--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(len(_Handler.requests), 1)
        method, path, _headers, body = _Handler.requests[0]
        self.assertEqual((method, path), ("POST", "/api/v1/hardware"))
        self.assertEqual(json.loads(body), json.loads(data))

    def test_patch_put_delete_default_to_plan(self):
        for method in ("PATCH", "PUT", "DELETE"):
            with self.subTest(method=method):
                result = self.run_cli(method, "hardware/fixture-1", "--data", '{"name":"Demo"}')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('"mode": "plan"', result.stdout)
                self.assertIn('"method": "%s"' % method, result.stdout)
                self.assertEqual(_Handler.requests, [])

    def test_http_error_and_application_error_fail(self):
        _Handler.response_status = 422
        _Handler.response_body = b'{"status":"error","messages":"invalid fixture"}'
        result = self.run_cli("GET", "hardware")
        self.assertNotEqual(result.returncode, 0)

        _Handler.response_status = 200
        _Handler.response_body = b'{"status":"error","messages":"API rejected fixture"}'
        result = self.run_cli("GET", "hardware")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("API rejected fixture", result.stderr)

    def test_response_token_is_redacted_on_success_and_api_error(self):
        _Handler.response_body = b'{"status":"success","message":"fake-test-token"}'
        result = self.run_cli("GET", "hardware")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[REDACTED]", result.stdout)
        self.assertNotIn("fake-test-token", result.stdout + result.stderr)

        _Handler.response_body = b'{"status":"error","messages":"fake-test-token"}'
        result = self.run_cli("GET", "hardware")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("fake-test-token", result.stdout + result.stderr)

    def test_dotenv_quotes_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "SNIPE_IT_URL='https://dotenv.example/instance'\n"
                'SNIPE_IT_TOKEN="literal-$NO_EXPANSION"\n',
                encoding="utf-8",
            )
            with mock.patch.object(API, "ROOT", Path(tmp)), mock.patch.dict(
                    os.environ, {}, clear=True):
                config = API.configuration()
                self.assertEqual(config["SNIPE_IT_URL"], "https://dotenv.example/instance")
                self.assertEqual(config["SNIPE_IT_TOKEN"], "literal-$NO_EXPANSION")

                os.environ["SNIPE_IT_URL"] = "https://env.example/site"
                os.environ["SNIPE_IT_TOKEN"] = "env-token"
                self.assertEqual(API.configuration(), {
                    "SNIPE_IT_URL": "https://env.example/site", "SNIPE_IT_TOKEN": "env-token"
                })

                os.environ["SNIPE_IT_URL"] = ""
                os.environ["SNIPE_IT_TOKEN"] = ""
                self.assertEqual(API.configuration(), {"SNIPE_IT_URL": "", "SNIPE_IT_TOKEN": ""})

    def test_unsafe_endpoint_is_rejected(self):
        for endpoint in ("https://other.example/hardware", "../hardware"):
            with self.subTest(endpoint=endpoint):
                result = self.run_cli("GET", endpoint)
                self.assertNotEqual(result.returncode, 0)
        self.assertEqual(_Handler.requests, [])

    def test_redirect_is_refused(self):
        _Handler.response_status = 302
        _Handler.response_headers = {"Location": "/elsewhere"}
        result = self.run_cli("GET", "hardware")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(_Handler.requests), 1)

    def test_malformed_json_fails(self):
        _Handler.response_body = b"not json"
        result = self.run_cli("GET", "hardware")
        self.assertNotEqual(result.returncode, 0)

    def test_missing_config_fails_without_leaking_secret(self):
        result = self.run_cli(
            "GET", "hardware", env_updates={"SNIPE_IT_URL": "", "SNIPE_IT_TOKEN": ""}
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(_Handler.requests, [])
        self.assertNotIn("fake-test-token", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
