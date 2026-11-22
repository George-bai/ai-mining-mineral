"""The only way out of the Hermes fence: one port per model server. It changes one thing, as image-limit.ts does inside
Pi: at most two images in each request (the first, which is the drawing, and the newest), since both servers accept no
more. Every other request byte, and every response byte, passes through unchanged. One JSON line per request goes to the
log: what Hermes sent besides the messages (sampling, output length, reasoning), how many images, how long, and the usage
the server reported.
Usage: python3 proxy.py <log.jsonl> <port>=<host:port> [<port>=<host:port> ...]      Stdlib only.
       DUMP=<folder> also writes each request, images cut out, for the smoke tests."""
import http.client, json, os, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_IMAGES = 2
NOTE = (f"[Image removed: only {MAX_IMAGES} images fit in one request. The first image and the newest are kept. "
        "Look at the file again to see this one.]")
LOG, DUMP = open(sys.argv[1], "a", buffering=1), os.environ.get("DUMP")
lock, seq = threading.Lock(), [0]


def cap(body):
    """Replace all but the first and the newest image with NOTE. Returns the number of images found."""
    found = [(m["content"], i) for m in body.get("messages", []) if isinstance(m.get("content"), list)
             for i, p in enumerate(m["content"]) if isinstance(p, dict) and p.get("type") == "image_url"]
    for content, i in found[1:len(found) - (MAX_IMAGES - 1)] if len(found) > MAX_IMAGES else []:
        content[i] = {"type": "text", "text": NOTE}
    return len(found)


def handler(upstream):
    host, port = upstream.rsplit(":", 1)

    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def go(self):
            t0, raw = time.time(), self.rfile.read(int(self.headers.get("Content-Length") or 0))
            with lock:
                seq[0] += 1; n = seq[0]
            rec = {"n": n, "t": round(t0, 3), "up": upstream, "method": self.command, "path": self.path, "bytes": len(raw)}
            if self.command == "POST" and raw:
                try:
                    body = json.loads(raw)
                    rec.update(model=body.get("model"), stream=body.get("stream"), messages=len(body.get("messages", [])),
                               tools=len(body.get("tools") or []),
                               sent={k: v for k, v in body.items() if k not in ("messages", "tools", "model", "stream")})
                    rec["images"] = cap(body)
                    if rec["images"] > MAX_IMAGES:
                        raw = json.dumps(body).encode()
                    if DUMP:
                        cut = json.loads(json.dumps(body))
                        for m in cut.get("messages", []):
                            if isinstance(m.get("content"), list):
                                m["content"] = [p if p.get("type") != "image_url" else {"type": "image_url", "image_url": "<cut>"} for p in m["content"]]
                        with open(os.path.join(DUMP, f"{n:05d}.json"), "w") as f:
                            json.dump(cut, f, indent=1)
                except ValueError:
                    pass
            fwd = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "content-length", "connection")}
            fwd["Content-Length"] = str(len(raw))
            conn = http.client.HTTPConnection(host, int(port), timeout=7200)
            tail, first = b"", None
            try:
                conn.request(self.command, self.path, body=raw or None, headers=fwd)
                r = conn.getresponse()
                self.send_response_only(r.status, r.reason)
                for k, v in r.getheaders():
                    if k.lower() not in ("transfer-encoding", "connection", "content-length"):
                        self.send_header(k, v)
                self.send_header("Connection", "close")
                self.end_headers()
                self.close_connection = True
                rec["status"] = r.status
                while chunk := r.read1(65536):
                    first = first or time.time()
                    self.wfile.write(chunk); self.wfile.flush()
                    tail = (tail + chunk)[-16384:]
            except Exception as e:  # the client sees the cut connection; the log says why
                rec["error"] = repr(e)
            finally:
                conn.close()
            rec["seconds"] = round(time.time() - t0, 3)
            rec["first_byte"] = round(first - t0, 3) if first else None
            for line in reversed(tail.decode("utf-8", "replace").splitlines()):
                j = line[5:].strip() if line.startswith("data:") else line.strip()
                if '"usage"' in j:
                    try:
                        rec["usage"] = json.loads(j).get("usage"); break
                    except ValueError:
                        pass
            LOG.write(json.dumps(rec) + "\n")

        do_GET = do_POST = do_PUT = do_DELETE = go

    return H


for spec in sys.argv[2:]:
    port, upstream = spec.split("=", 1)
    threading.Thread(target=ThreadingHTTPServer(("0.0.0.0", int(port)), handler(upstream)).serve_forever, daemon=True).start()
threading.Event().wait()
