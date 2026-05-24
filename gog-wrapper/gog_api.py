#!/usr/bin/env python3
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


MAX_BODY_BYTES = 64 * 1024
DEFAULT_TIMEOUT_SECONDS = 60


def read_json(handler):
    length = int(handler.headers.get("content-length", "0") or "0")
    if length > MAX_BODY_BYTES:
        raise ValueError("request body too large")
    if length == 0:
        return {}
    return json.loads(handler.rfile.read(length).decode("utf-8"))


def write_json(handler, status, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("content-type", "application/json; charset=utf-8")
    handler.send_header("content-length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def normalize_args(value):
    if not isinstance(value, list) or not value:
        raise ValueError('expected JSON field "args" as a non-empty string array')
    args = []
    for item in value:
        if not isinstance(item, str) or item == "":
            raise ValueError('expected JSON field "args" as a non-empty string array')
        args.append(item)
    return args


class GogHandler(BaseHTTPRequestHandler):
    server_version = "gog-api/1"

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

    def do_GET(self):
        if self.path in ("/", "/healthz"):
            write_json(self, 200, {"ok": True})
            return
        write_json(self, 404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        if self.path != "/gog":
            write_json(self, 404, {"ok": False, "error": "not_found"})
            return
        try:
            body = read_json(self)
            args = normalize_args(body.get("args"))
            timeout = int(body.get("timeoutSeconds", DEFAULT_TIMEOUT_SECONDS))
            completed = subprocess.run(
                ["gog", *args],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            write_json(
                self,
                200,
                {
                    "ok": completed.returncode == 0,
                    "code": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                },
            )
        except Exception as exc:
            write_json(self, 400, {"ok": False, "error": str(exc)})


def main():
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), GogHandler)
    print(f"gog API listening on 0.0.0.0:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
