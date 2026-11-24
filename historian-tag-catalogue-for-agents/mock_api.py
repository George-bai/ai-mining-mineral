"""A mock of the historian's web API (the PI Web API's request and response shapes), read-only, serving the
plant from generator.py with values from values.py. Ours, not the vendor's.

    MOCK_SITES=3 MOCK_CONCENTRATORS=1 MOCK_AUTH=basic uv run uvicorn mock_api:app --port 8711

Environment: MOCK_SITES, MOCK_CONCENTRATORS, MOCK_AUTH (none | basic | bearer), MOCK_FAULT_RATE (share of
requests answered 429 or 503), MOCK_LATENCY_MS, MOCK_EXTRA_SEED (changes which tags exist, for the crawler's
diff demo).
"""
import asyncio, base64, fnmatch, hashlib, os, random, re, secrets, time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
from fastapi import APIRouter, FastAPI, Query, Request
from fastapi.responses import JSONResponse

import generator, values

USER, PASSWORD = "demo", "demo-password"  # the mock's fixed demo account
TOKEN_TTL = 900


def load():
    plant = generator.build(int(os.environ.get("MOCK_SITES", 3)), int(os.environ.get("MOCK_CONCENTRATORS", 1)))
    extra = os.environ.get("MOCK_EXTRA_SEED")
    if extra:  # drop about 1 % of attributes and points, for the crawler's diff demo
        keep = lambda key: random.Random(f"{extra}|{key}").random() > 0.01
        plant["attributes"] = [a for a in plant["attributes"] if keep(a["path"])]
        plant["points"] = {k: p for k, p in plant["points"].items() if keep(k)}
    return plant


P = load()
CFG = P["config"]
TZ = ZoneInfo(CFG["timezone"])
DS_PATH = f"\\\\{CFG['data_server']}"
DB_PATH = P["root"]
ELEMENTS = {e["path"]: e for e in P["elements"]}
CHILDREN: dict = {}
for e in P["elements"]:
    CHILDREN.setdefault(e["parent"], []).append(e)
ATTRS = {a["path"]: a for a in P["attributes"]}
ATTRS_BY_ELEMENT: dict = {}
for a in P["attributes"]:
    ATTRS_BY_ELEMENT.setdefault(a["element"], []).append(a)
POINTS = P["points"]
TOKENS: dict = {}


def tag_of_point(name: str) -> dict:
    p = POINTS[name]
    a = ATTRS.get(p["linked"] or "")
    element = a["element"] if a else p["name"]
    return {**p, "point": p["name"], "element": element, "template": ELEMENTS.get(element, {}).get("template"),
            "attr": a["name"] if a else None}


def wire_meters():
    """Each supply meter measures the power tags of its area; the main incomer measures all of them."""
    loads = {}
    for a in P["attributes"]:
        if a["kind"] == "power" and a["variant"] == "primary" and a["point"] in POINTS:
            loc = values.location(a["element"])
            if loc and ELEMENTS[a["element"]]["template"] != "Power Meter":
                loads.setdefault((loc[0], loc[1]), {}).setdefault(loc[2], []).append(tag_of_point(a["point"]))
    for a in P["attributes"]:
        if a["name"] != "Active Power" or a["point"] not in POINTS:
            continue
        loc = values.location(a["element"])
        if not loc or (loc[0], loc[1]) not in loads:
            continue
        areas = loads[(loc[0], loc[1])]
        meter = loc[3]
        if meter == "Main Incomer":
            members = [t for ts in areas.values() for t in ts]
        else:
            members = areas.get(meter.removesuffix(" Supply"), [])
        if members:
            values.METERS[a["point"]] = members
            energy = next((e for e in P["attributes"] if e["element"] == a["element"] and e["name"] == "Energy"
                           and e["point"] in POINTS), None)
            if energy:
                values.ENERGY[energy["point"]] = tag_of_point(a["point"])


wire_meters()


# ---------- web ids: a prefix for the object type and the path, base64url-encoded ----------
def webid(kind: str, path: str) -> str:
    return kind + base64.urlsafe_b64encode(path.encode()).decode().rstrip("=")


def unweb(w: str) -> tuple[str, str]:
    kind, b = w[:4], w[4:]
    try:
        return kind, base64.urlsafe_b64decode(b + "=" * (-len(b) % 4)).decode()
    except Exception:
        return kind, ""


def uid(path: str) -> str:
    h = hashlib.md5(path.encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


class NotFound(Exception):
    pass


def err(status: int, *messages: str):
    return JSONResponse({"Errors": list(messages)}, status_code=status)


# ---------- time strings: *, t, y, ISO, with offsets such as *-30d or t+6h ----------
UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "mo": 30 * 86400, "y": 365 * 86400}


def duration(s: str) -> float:
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(mo|[smhdwy])\s*", s or "")
    if not m:
        raise ValueError(f"Cannot parse the duration '{s}'.")
    return float(m.group(1)) * UNITS[m.group(2)]


def parse_time(s: str | None, default: str = "*") -> float:
    s = (s or default).strip()
    now = values.now()
    m = re.fullmatch(r"(\*|t|today|y|yesterday)?\s*(([+-])\s*(\d+(?:\.\d+)?)\s*(mo|[smhdwy]))?", s, re.I)
    if m and (m.group(1) or m.group(2)):
        base = (m.group(1) or "*").lower()
        local_midnight = datetime.fromtimestamp(now, TZ).replace(hour=0, minute=0, second=0, microsecond=0)
        t = {"*": now, "t": local_midnight.timestamp(), "today": local_midnight.timestamp(),
             "y": (local_midnight - timedelta(days=1)).timestamp(),
             "yesterday": (local_midnight - timedelta(days=1)).timestamp()}[base]
        if m.group(2):
            t += (1 if m.group(3) == "+" else -1) * float(m.group(4)) * UNITS[m.group(5).lower()]
        return t
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"Cannot parse the time '{s}'.")
    return (d if d.tzinfo else d.replace(tzinfo=TZ)).timestamp()


def iso(t: float) -> str:
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z"


# ---------- objects in the API's shapes ----------
def base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/") + "/piwebapi"


def element_json(e: dict, b: str) -> dict:
    w = webid("F1Em", e["path"])
    return {"WebId": w, "Id": uid(e["path"]), "Name": e["name"], "Description": e["description"],
            "Path": e["path"], "TemplateName": e["template"], "HasChildren": bool(CHILDREN.get(e["path"])),
            "CategoryNames": [], "ExtendedProperties": {},
            "Links": {"Self": f"{b}/elements/{w}", "Elements": f"{b}/elements/{w}/elements",
                      "Attributes": f"{b}/elements/{w}/attributes",
                      **({"Parent": f"{b}/elements/{webid('F1Em', e['parent'])}"} if e["parent"] in ELEMENTS else {})}}


def attribute_json(a: dict, b: str) -> dict:
    w = webid("F1Ab", a["path"])
    links = {"Self": f"{b}/attributes/{w}", "Element": f"{b}/elements/{webid('F1Em', a['element'])}",
             "Value": f"{b}/streams/{w}/value", "RecordedData": f"{b}/streams/{w}/recorded"}
    if a["point"] in POINTS:
        links["Point"] = f"{b}/points/{webid('F1DP', a['point'])}"
    digital = a["kind"] == "status"
    return {"WebId": w, "Id": uid(a["path"]), "Name": a["name"], "Description": "", "Path": a["path"],
            "Type": "EnumerationValue" if digital else "Double", "TypeQualifier": "Run Status" if digital else "",
            "DefaultUnitsName": a["unit"], "DefaultUnitsNameAbbreviation": a["unit"], "DataReferencePlugIn": "PI Point",
            "ConfigString": f"{DS_PATH}\\{a['point']}", "IsConfigurationItem": False, "HasChildren": False,
            "CategoryNames": [], "Links": links}


def point_json(p: dict, b: str) -> dict:
    w = webid("F1DP", p["name"])
    return {"WebId": w, "Id": int(uid(p["name"])[:6], 16), "Name": p["name"], "Path": f"{DS_PATH}\\{p['name']}",
            "Descriptor": p["descriptor"], "PointClass": "classic", "PointType": "Digital" if p["digital"] else "Float32",
            "DigitalSetName": ("Alarm" if p["kind"] == "alarm" else "Run Status") if p["digital"] else "",
            "EngineeringUnits": p["unit"], "Span": 100.0, "Zero": 0.0, "Step": p["digital"], "Future": False,
            "Links": {"Self": f"{b}/points/{w}", "DataServer": f"{b}/dataservers/{webid('F1DS', DS_PATH)}",
                      "Value": f"{b}/streams/{w}/value", "RecordedData": f"{b}/streams/{w}/recorded"}}


def stream_tag(w: str) -> dict:
    """The point behind a stream web id (an attribute's or a point's), as values.py needs it."""
    kind, path = unweb(w)
    if kind == "F1Ab":
        if path not in ATTRS:
            raise NotFound(f"Unknown or invalid WebID '{w}'.")
        a = ATTRS[path]
        if a["point"] not in POINTS:
            raise NotFound(f"PI Point not found '{DS_PATH}\\{a['point']}'.")
        p = POINTS[a["point"]]
    elif kind == "F1DP" and path in POINTS:
        p = POINTS[path]
    else:
        raise NotFound(f"Unknown or invalid WebID '{w}'.")
    return tag_of_point(p["name"])


def last_good(tag: dict) -> float | None:
    """The time of the newest value: the mock's now (or the end of the source's last hour with a value), days
    earlier for a stale tag; None if the tag never had data."""
    if tag["health"] == "no_data":
        return None
    lv = values.last_valid(tag)
    if lv is None:
        return None
    if tag["health"] == "stale":
        return lv - random.Random(tag["point"]).uniform(3, 30) * 86400
    return lv


DIGITAL = {"status": {0: "Stopped", 1: "Running"}, "alarm": {0: "Normal", 1: "Alarm"}}


def value_json(tag: dict, t: float, v: float, good: bool = True) -> dict:
    if tag["digital"]:
        val = {"Name": DIGITAL[tag["kind"]][int(round(v))], "Value": int(round(v)), "IsSystem": False}
    else:
        val = round(float(v), 4)
    return {"Timestamp": iso(t), "Value": val, "UnitsAbbreviation": tag["unit"], "Good": good,
            "Questionable": False, "Substituted": False, "Annotated": False}


def system_value(t: float, name: str, code: int) -> dict:
    return {"Timestamp": iso(t), "Value": {"Name": name, "Value": code, "IsSystem": True}, "UnitsAbbreviation": "",
            "Good": False, "Questionable": False, "Substituted": False, "Annotated": False}


def end_value(tag: dict) -> dict:
    lt = last_good(tag)
    if lt is None:
        return system_value(values.EARLIEST, "No Data", 248)
    if tag["health"] == "bad_quality":
        return system_value(lt, "Bad Input", 307)
    t = np.array([np.floor(lt / values.SCAN) * values.SCAN - values.SCAN])
    v = float(values.scans(tag, t)[0])
    return system_value(float(t[0]), "No Data", 248) if v != v else value_json(tag, float(t[0]), v)


def recorded_json(tag: dict, start: float, end: float, max_count: int) -> list:
    lt = last_good(tag)
    if lt is None or start > lt:
        return []
    ts, vs = values.recorded(tag, start, min(end, lt), max_count)
    items = [value_json(tag, t, v) for t, v in zip(ts.tolist(), vs.tolist())]
    if tag["health"] == "bad_quality" and items and end >= lt - 7200:
        items = [i for i in items if i["Timestamp"] < iso(lt - 7200)] + [system_value(lt - 7200, "Bad Input", 307)]
    return items


def interpolated_json(tag: dict, start: float, end: float, step: float) -> list:
    lt = last_good(tag)
    t = start + step * np.arange(int((end - start) // step) + 1)
    if lt is None:
        return [system_value(x, "No Data", 248) for x in t.tolist()]
    v = values.scans(tag, np.minimum(t, lt - values.SCAN))
    return [value_json(tag, a, b) if b == b else system_value(a, "No Data", 248) for a, b in zip(t.tolist(), v.tolist())]


def summary_json(tag: dict, start: float, end: float, types: list[str], step: float | None) -> list:
    lt = last_good(tag)
    out = []
    edges = [start] if not step else (start + step * np.arange(int(np.ceil((end - start) / step)))).tolist()
    for a in edges:
        b = min(end, a + step) if step else end
        s = values.summary(tag, a, min(b, lt)) if lt and a < lt else {}
        for typ in types:
            if typ not in s:
                out.append({"Type": typ, "Value": system_value(a, "No Data", 248)})
            else:
                out.append({"Type": typ, "Value": {"Timestamp": iso(a), "Value": round(s[typ], 4) if typ != "Count" else s[typ],
                                                    "UnitsAbbreviation": tag["unit"] if typ != "Count" else "",
                                                    "Good": True, "Questionable": False, "Substituted": False,
                                                    "Annotated": False}})
    return out


# ---------- selectedFields and paging ----------
def select(obj, fields: str | None):
    if not fields:
        return obj
    paths = [f.split(".") for f in fields.split(";") if f]

    def prune(o, prefixes):
        if any(len(p) == 0 for p in prefixes):
            return o
        if isinstance(o, list):
            return [prune(x, prefixes) for x in o]
        if not isinstance(o, dict):
            return o
        out = {}
        for k, v in o.items():
            sub = [p[1:] for p in prefixes if p[0] == k]
            if sub:
                out[k] = prune(v, sub)
        return out

    return prune(obj, paths)


def page(items: list, start_index: int, max_count: int) -> list:
    return items[start_index:start_index + max_count]


# ---------- the app ----------
app = FastAPI(title="Mock historian web API", docs_url=None, redoc_url=None, openapi_url=None)
api = APIRouter(prefix="/piwebapi")
WRITE_OK = {"/piwebapi/batch", "/mock/token"}


@app.middleware("http")
async def guard(request: Request, call_next):
    if request.method not in ("GET", "HEAD") and request.url.path not in WRITE_OK:
        return err(405, "The mock is read-only: only GET requests are served.")
    latency = float(os.environ.get("MOCK_LATENCY_MS", 0))
    if latency:
        await asyncio.sleep(latency / 1000)
    rate = float(os.environ.get("MOCK_FAULT_RATE", 0))
    if rate and request.url.path != "/mock/token" and random.random() < rate:
        return err(random.choice([429, 503]), "Injected fault.")
    if request.url.path != "/mock/token" and not authorised(request.headers.get("authorization", "")):
        return JSONResponse({"Errors": ["Authentication required."]}, status_code=401,
                            headers={"WWW-Authenticate": 'Basic realm="mock"'})
    response = await call_next(request)
    # the stand-in's clock is fixed (MOCK_NOW), so it says what time it is; a real server's Date header does the same job
    response.headers["X-Historian-Time"] = datetime.fromtimestamp(values.now(), timezone.utc).isoformat()
    return response


def authorised(header: str) -> bool:
    mode = os.environ.get("MOCK_AUTH", "basic")
    if mode == "none":
        return True
    if mode == "basic" and header.startswith("Basic "):
        try:
            return base64.b64decode(header[6:]).decode() == f"{USER}:{PASSWORD}"
        except Exception:
            return False
    if mode == "bearer" and header.startswith("Bearer "):
        return TOKENS.get(header[7:], 0) > time.time()
    return False


@app.post("/mock/token")
async def token(request: Request):
    h = request.headers.get("authorization", "")
    if not (h.startswith("Basic ") and base64.b64decode(h[6:]).decode(errors="ignore") == f"{USER}:{PASSWORD}"):
        return err(401, "Give the demo user's Basic credentials to get a token.")
    t = secrets.token_urlsafe(24)
    TOKENS[t] = time.time() + TOKEN_TTL
    return {"access_token": t, "token_type": "Bearer", "expires_in": TOKEN_TTL}


@api.get("")
async def home(request: Request):
    b = base_url(request)
    return {"Links": {"Self": b, "AssetServers": f"{b}/assetservers", "DataServers": f"{b}/dataservers"}}


@api.get("/assetservers")
async def asset_servers(request: Request):
    b, path = base_url(request), f"\\\\{CFG['asset_server']}"
    w = webid("F1RS", path)
    return {"Links": {}, "Items": [{"WebId": w, "Id": uid(path), "Name": CFG["asset_server"], "Path": path,
                                    "Links": {"Self": f"{b}/assetservers/{w}", "Databases": f"{b}/assetservers/{w}/assetdatabases"}}]}


def database_json(b: str) -> dict:
    w = webid("F1RD", DB_PATH)
    return {"WebId": w, "Id": uid(DB_PATH), "Name": CFG["asset_database"], "Description": "", "Path": DB_PATH,
            "Links": {"Self": f"{b}/assetdatabases/{w}", "Elements": f"{b}/assetdatabases/{w}/elements",
                      "ElementAttributes": f"{b}/assetdatabases/{w}/elementattributes"}}


@api.get("/assetservers/{w}/assetdatabases")
async def databases(w: str, request: Request):
    return {"Links": {}, "Items": [database_json(base_url(request))]}


@api.get("/assetdatabases")
async def database_by_path(request: Request, path: str = ""):
    if path.lower() != DB_PATH.lower():
        return err(404, f"The specified path '{path}' was not found.")
    return select(database_json(base_url(request)), request.query_params.get("selectedFields"))


def check_db(w: str):
    if unweb(w) != ("F1RD", DB_PATH):
        raise NotFound(f"Unknown or invalid WebID '{w}'.")


@api.get("/assetdatabases/{w}/elements")
async def db_elements(w: str, request: Request, searchFullHierarchy: bool = False, startIndex: int = 0,
                      maxCount: int = Query(1000, le=150000), nameFilter: str = "*", templateName: str = ""):
    check_db(w)
    b = base_url(request)
    pool = P["elements"] if searchFullHierarchy else CHILDREN.get(DB_PATH, []) + [e for e in P["elements"] if e["parent"] is None]
    pool = [e for e in pool if fnmatch.fnmatch(e["name"].lower(), nameFilter.lower())
            and (not templateName or e["template"] == templateName)]
    items = [element_json(e, b) for e in page(pool, startIndex, maxCount)]
    return select({"Links": {}, "Items": items}, request.query_params.get("selectedFields"))


@api.get("/assetdatabases/{w}/elementattributes")
async def db_attributes(w: str, request: Request, startIndex: int = 0, maxCount: int = Query(1000, le=150000),
                        attributeNameFilter: str = "*", elementNameFilter: str = "*"):
    check_db(w)
    b = base_url(request)
    pool = [a for a in P["attributes"] if fnmatch.fnmatch(a["name"].lower(), attributeNameFilter.lower())
            and fnmatch.fnmatch(ELEMENTS[a["element"]]["name"].lower(), elementNameFilter.lower())]
    items = [attribute_json(a, b) for a in page(pool, startIndex, maxCount)]
    return select({"Links": {}, "Items": items}, request.query_params.get("selectedFields"))


def get_element(w: str) -> dict:
    kind, path = unweb(w)
    if kind != "F1Em" or path not in ELEMENTS:
        raise NotFound(f"Unknown or invalid WebID '{w}'.")
    return ELEMENTS[path]


@api.get("/elements/{w}")
async def element(w: str, request: Request):
    return select(element_json(get_element(w), base_url(request)), request.query_params.get("selectedFields"))


@api.get("/elements/{w}/elements")
async def element_children(w: str, request: Request, startIndex: int = 0, maxCount: int = 1000):
    e, b = get_element(w), base_url(request)
    items = [element_json(c, b) for c in page(CHILDREN.get(e["path"], []), startIndex, maxCount)]
    return select({"Links": {}, "Items": items}, request.query_params.get("selectedFields"))


@api.get("/elements/{w}/attributes")
async def element_attributes(w: str, request: Request, startIndex: int = 0, maxCount: int = 1000):
    e, b = get_element(w), base_url(request)
    items = [attribute_json(a, b) for a in page(ATTRS_BY_ELEMENT.get(e["path"], []), startIndex, maxCount)]
    return select({"Links": {}, "Items": items}, request.query_params.get("selectedFields"))


@api.get("/attributes/{w}")
async def attribute(w: str, request: Request):
    kind, path = unweb(w)
    if kind != "F1Ab" or path not in ATTRS:
        raise NotFound(f"Unknown or invalid WebID '{w}'.")
    return select(attribute_json(ATTRS[path], base_url(request)), request.query_params.get("selectedFields"))


@api.get("/dataservers")
async def data_servers(request: Request):
    b, w = base_url(request), webid("F1DS", DS_PATH)
    return {"Links": {}, "Items": [{"WebId": w, "Id": uid(DS_PATH), "Name": CFG["data_server"], "Path": DS_PATH,
                                    "IsConnected": True, "Links": {"Self": f"{b}/dataservers/{w}", "Points": f"{b}/dataservers/{w}/points"}}]}


@api.get("/dataservers/{w}/points")
async def points(w: str, request: Request, nameFilter: str = "*", startIndex: int = 0,
                 maxCount: int = Query(1000, le=150000)):
    if unweb(w) != ("F1DS", DS_PATH):
        raise NotFound(f"Unknown or invalid WebID '{w}'.")
    b, f = base_url(request), nameFilter.lower()
    pool = [p for n, p in POINTS.items() if fnmatch.fnmatch(n.lower(), f)]
    items = [point_json(p, b) for p in page(pool, startIndex, maxCount)]
    return select({"Links": {}, "Items": items}, request.query_params.get("selectedFields"))


@api.get("/points/{w}")
async def point(w: str, request: Request):
    kind, name = unweb(w)
    if kind != "F1DP" or name not in POINTS:
        raise NotFound(f"Unknown or invalid WebID '{w}'.")
    return select(point_json(POINTS[name], base_url(request)), request.query_params.get("selectedFields"))


MAX_POINTS = 150000  # the mock's cap on values per stream per request, as a server's own limit would be


def stream_data(tag: dict, kind: str, q) -> dict:
    """One stream's data for value, end, recorded, interpolated, plot or summary."""
    if kind in ("value", "end"):
        return end_value(tag)
    start, end = parse_time(q.get("startTime"), "*-1d"), parse_time(q.get("endTime"), "*")
    if end < start:
        raise ValueError("The end time is before the start time.")
    if kind == "recorded":
        return {"Items": recorded_json(tag, start, end, min(int(q.get("maxCount", 1000)), MAX_POINTS)),
                "UnitsAbbreviation": tag["unit"]}
    if kind == "interpolated":
        step = duration(q.get("interval", "1h"))
        if (end - start) / step > MAX_POINTS:
            raise ValueError("Too many values requested.")
        return {"Items": interpolated_json(tag, start, end, step), "UnitsAbbreviation": tag["unit"]}
    if kind == "plot":
        n = int(q.get("intervals", 24))
        step = (end - start) / max(n, 1)
        items = []
        for i in range(n):
            ts, vs = values.recorded(tag, start + i * step, start + (i + 1) * step, 100000)
            if len(ts):
                for j in sorted({0, int(np.argmin(vs)), int(np.argmax(vs)), len(ts) - 1}):
                    items.append(value_json(tag, float(ts[j]), float(vs[j])))
        return {"Items": items, "UnitsAbbreviation": tag["unit"]}
    if kind == "summary":
        types = q.getlist("summaryType") if hasattr(q, "getlist") else q.get("summaryType", ["Total"])
        types = [t for x in (types or ["Total"]) for t in str(x).split(",")]
        step = duration(q["summaryDuration"]) if q.get("summaryDuration") else None
        if step and (end - start) / step > 10000:
            raise ValueError("Too many summary intervals requested.")
        return {"Items": summary_json(tag, start, end, types, step)}
    raise NotFound(f"Unknown stream method '{kind}'.")


@api.get("/streams/{w}/{kind}")
async def stream(w: str, kind: str, request: Request):
    tag = stream_tag(w)
    return stream_data(tag, kind, request.query_params)


@api.get("/streamsets/{kind}")
async def streamset(kind: str, request: Request):
    q = request.query_params
    items = []
    for w in q.getlist("webId"):
        item = {"WebId": w}
        try:
            tag = stream_tag(w)
            item.update({"Name": tag["name"], "Path": f"{DS_PATH}\\{tag['name']}"})
            data = stream_data(tag, kind, q)
            item.update({"Value": data} if kind in ("value", "end") else data)
        except (NotFound, ValueError) as e:
            item["Errors"] = [str(e)]
        items.append(item)
    return {"Links": {}, "Items": items}


@api.post("/batch")
async def batch(request: Request):
    body = await request.json()
    bad = [k for k, r in body.items() if str(r.get("Method", "GET")).upper() != "GET"]
    if bad:
        return err(400, f"The mock's batch takes only GET sub-requests; refused: {', '.join(bad)}.")
    import httpx
    out = {}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://mock") as c:
        for k, r in body.items():
            url = re.sub(r"^https?://[^/]+", "", r["Resource"])
            resp = await c.get(url, headers={"authorization": request.headers.get("authorization", "")})
            out[k] = {"Status": resp.status_code, "Headers": {}, "Content": resp.json()}
    return out


app.include_router(api)


@app.exception_handler(NotFound)
async def not_found(request, e):
    return err(404, str(e))


@app.exception_handler(ValueError)
async def bad_request(request, e):
    return err(400, str(e))
