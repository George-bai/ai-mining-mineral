"""The only code that talks to the historian: a read-only client for its web API.

Read-only by design: requests other than GET never leave this module, except the batch call (checked to carry
only GET sub-requests) and the mock's token call. Retries 429 and 5xx with backoff; keeps per-item errors
instead of raising them; splits long lists of web ids so URLs stay short; runs at most `workers` requests at once.
"""
import base64, time
from concurrent.futures import ThreadPoolExecutor

import httpx

MAX_URL = 2000  # characters; web ids are long, so streamset calls are split to stay under this


class ReadOnlyError(Exception):
    pass


class HistorianError(Exception):
    def __init__(self, status: int, errors: list):
        super().__init__(f"{status}: {'; '.join(map(str, errors))}")
        self.status, self.errors = status, errors


class Client:
    def __init__(self, base_url: str, auth: str = "basic", user: str = "", password: str = "",
                 timeout: float = 30, retries: int = 4, workers: int = 4, verify: bool = True):
        """auth: none | basic | bearer (the mock's token call). A real server would add Kerberos here."""
        self.base = base_url.rstrip("/")
        self.auth, self.user, self.password = auth, user, password
        self.retries, self.workers = retries, workers
        self.http = httpx.Client(timeout=timeout, verify=verify)
        self.token = None
        self.requests = 0  # every request sent, for the crawler's report

    # ----- the one place requests are sent -----
    def _headers(self) -> dict:
        if self.auth == "basic":
            return {"authorization": "Basic " + base64.b64encode(f"{self.user}:{self.password}".encode()).decode()}
        if self.auth == "bearer":
            if not self.token:
                self._get_token()
            return {"authorization": f"Bearer {self.token}"}
        return {}

    def _get_token(self):
        root = self.base.rsplit("/piwebapi", 1)[0]
        basic = "Basic " + base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
        r = self.http.post(f"{root}/mock/token", headers={"authorization": basic})
        self.requests += 1
        if r.status_code != 200:
            raise HistorianError(r.status_code, r.json().get("Errors", [r.text]))
        self.token = r.json()["access_token"]

    def _send(self, method: str, path: str, params=None, json=None) -> dict:
        if method != "GET" and not (method == "POST" and path == "/batch"):
            raise ReadOnlyError(f"{method} {path}: this client only reads.")
        url = path if path.startswith("http") else self.base + path
        delay, refreshed = 0.5, False
        for attempt in range(self.retries + 1):
            try:
                r = self.http.request(method, url, params=params, json=json, headers=self._headers())
            except httpx.TransportError:
                if attempt == self.retries:
                    raise
                time.sleep(delay); delay *= 2
                continue
            finally:
                self.requests += 1
            if r.status_code == 401 and self.auth == "bearer" and not refreshed:
                self.token, refreshed = None, True   # token expired: get a new one once
                continue
            if r.status_code == 429 or r.status_code >= 500:
                if attempt == self.retries:
                    break
                time.sleep(float(r.headers.get("retry-after", delay))); delay *= 2
                continue
            body = r.json() if r.content else {}
            if r.status_code >= 400:
                raise HistorianError(r.status_code, body.get("Errors", [r.text]) if isinstance(body, dict) else [r.text])
            return body
        raise HistorianError(r.status_code, ["Gave up after retries."])

    # ----- reading -----
    def get(self, resource: str, **params) -> dict:
        return self._send("GET", resource, params={k: v for k, v in params.items() if v is not None})

    def pages(self, resource: str, page_size: int = 1000, **params):
        """Every item of a paged collection, page by page (startIndex, maxCount)."""
        start = 0
        while True:
            items = self.get(resource, startIndex=start, maxCount=page_size, **params).get("Items", [])
            yield from items
            if len(items) < page_size:
                return
            start += page_size

    def streamset(self, kind: str, webids: list[str], **params) -> list[dict]:
        """streamsets/<kind> for many web ids, split into URL-sized chunks, at most `workers` at a time.
        Items keep their own Errors; one bad tag does not fail the rest."""
        chunks, cur, size = [], [], 0
        for w in webids:
            if cur and size + len(w) + 7 > MAX_URL:
                chunks.append(cur); cur, size = [], 0
            cur.append(w); size += len(w) + 7
        if cur:
            chunks.append(cur)
        call = lambda ch: self.get(f"/streamsets/{kind}", webId=ch, **params).get("Items", [])
        with ThreadPoolExecutor(self.workers) as pool:
            return [item for items in pool.map(call, chunks) for item in items]

    def batch(self, requests: dict) -> dict:
        """POST /batch, allowed only when every sub-request is a GET."""
        bad = [k for k, r in requests.items() if str(r.get("Method", "GET")).upper() != "GET"]
        if bad:
            raise ReadOnlyError(f"Batch sub-requests must be GET: {', '.join(bad)}.")
        return self._send("POST", "/batch", json=requests)

    # ----- the historian's own objects -----
    def database(self, path: str) -> dict:
        return self.get("/assetdatabases", path=path)

    def data_server(self) -> dict:
        return self.get("/dataservers")["Items"][0]


def demo():
    c = Client("http://127.0.0.1:1/piwebapi", auth="none", retries=0)
    for call in (lambda: c._send("PUT", "/points/x"), lambda: c.batch({"1": {"Method": "DELETE", "Resource": "x"}})):
        try:
            call()
            raise AssertionError("a write got through")
        except ReadOnlyError:
            pass
    print("connector ok: writes refused before the network")


if __name__ == "__main__":
    demo()
