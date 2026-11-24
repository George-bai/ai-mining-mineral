"""The MCP server an agent uses: search the tag catalogue, then read only the tags it chose.

    uv run python mcp_server.py                      # stdio, for a local agent
    uv run python mcp_server.py --http --port 8712   # streamable HTTP, needs MCP_API_KEY

Every answer is short and says where its numbers came from (tags, units, window, basis). Full data goes to a
dataset file (CSV plus a metadata file); the agent gets its path and a summary. Every call is logged.
"""
import argparse, csv, json, os, time, uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import logging

import yaml
from mcp.server import MCPServer

import catalog
from connector import Client, HistorianError

logging.getLogger("httpx").setLevel(logging.WARNING)
HERE = Path(__file__).parent
S = yaml.safe_load((HERE / "config" / "settings.yaml").read_text())
for k in list(S):
    if isinstance(S[k], str) and os.environ.get(k.upper()):
        S[k] = os.environ[k.upper()]
L = S["limits"]
TZ = ZoneInfo(S["timezone"])
path_of = lambda p: Path(p) if Path(p).is_absolute() else HERE / p
CATALOG, DATASETS, AUDIT = path_of(S["catalog"]), path_of(S["datasets"]), path_of(S["audit_log"])
CONVERT = {("MW", "kW"): 1000, ("kW", "MW"): 0.001, ("L/s", "m3/h"): 3.6, ("m3/h", "L/s"): 1 / 3.6,
           ("bar", "kPa"): 100, ("kPa", "bar"): 0.01}

mcp = MCPServer("historian", instructions=(
    "Find historian tags by searching the catalogue, never by listing them. Resolve the place with find_assets, "
    "check get_golden_tags, then search_tags within that scope. Read data with get_timeseries, summary mode first. "
    "Say which tags, units, window and basis your numbers come from."))
_client = None


def client() -> Client:
    global _client
    if _client is None:
        _client = Client(S["historian_url"], S["historian_auth"], S["historian_user"], S["historian_password"])
    return _client


def con():
    return catalog.connect(CATALOG)


def audit(tool: str, args: dict, result, started: float):
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    size = len(result) if isinstance(result, (list, dict)) else 1
    with AUDIT.open("a") as f:
        f.write(json.dumps({"time": datetime.now(TZ).isoformat(timespec="seconds"), "tool": tool, "args": args,
                            "result_items": size, "ms": round((time.time() - started) * 1000)}) + "\n")


def logged(fn):
    def wrapper(**kwargs):
        t = time.time()
        try:
            out = fn(**kwargs)
        except Exception as e:
            out = {"error": str(e)}
        audit(fn.__name__, kwargs, out, t)
        return out
    wrapper.__name__, wrapper.__doc__ = fn.__name__, fn.__doc__
    wrapper.__annotations__ = fn.__annotations__
    wrapper.__wrapped__ = fn
    return wrapper


def local_time(iso: str | None) -> str | None:
    if not iso:
        return iso
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TZ).isoformat(timespec="seconds")


@mcp.tool()
@logged
def catalog_status() -> dict:
    """When the catalogue was last built, the historian's own current time (relative times such as *-30d count from
    it) and its earliest record, how many tags the catalogue holds, and their health."""
    c = con()
    run = c.execute("SELECT run_id, finished, report FROM crawl_runs ORDER BY finished DESC LIMIT 1").fetchone()
    rep = json.loads(run["report"]) if run else {}
    return {"last_crawl": local_time(run["finished"]) if run else None,
            "historian_now": local_time(rep.get("historian_time")),
            "historian_earliest": local_time(rep.get("historian_earliest")), "tags": rep.get("tags"),
            "health": rep.get("by_health"), "variants": rep.get("by_variant"),
            "unlinked_points": rep.get("unlinked_points"), "timezone": S["timezone"]}


@mcp.tool()
@logged
def find_assets(text: str) -> list:
    """Resolve a place named in words ("Site A concentrator 1", "ball mill 2 at site c") to asset-tree paths."""
    return [{"path": r["path"], "level": r["level"], "template": r["template"]} for r in catalog.find_assets(con(), text)]


@mcp.tool()
@logged
def browse_asset(path: str, depth: int = 1) -> dict:
    """The children of an asset and the attribute names under it, for drilling down by hand (depth 1 or 2)."""
    c = con()
    depth = max(1, min(depth, 2))
    out = {"path": path, "children": [], "attributes": []}
    frontier = [path]
    for _ in range(depth):
        nxt = []
        for p in frontier:
            for r in c.execute("SELECT path, template FROM elements WHERE parent=? ORDER BY path", (p,)):
                out["children"].append({"path": r["path"], "template": r["template"]})
                nxt.append(r["path"])
        frontier = nxt
    for r in c.execute("SELECT path, unit, health FROM tags WHERE element=? ORDER BY path", (path,)):
        out["attributes"].append({"path": r["path"], "unit": r["unit"], "health": r["health"]})
    out["children"] = out["children"][:200]
    return out


@mcp.tool()
@logged
def search_tags(query: str, scope: str | None = None, quantity: str | None = None, limit: int = 10) -> list:
    """Ranked candidate tags for a question, each with its path, point name, unit, health, last value and why it
    matched. scope: an asset path from find_assets. quantity: power, energy, flow, rate, pressure, density, level,
    composition, current, speed, status or duration."""
    rows = catalog.search(con(), query, scope, quantity, min(limit, L["search_results"]))
    for r in rows:
        r["last_time"] = local_time(r["last_time"])
        r.pop("score")
    return rows


@mcp.tool()
@logged
def get_golden_tags(scope: str | None = None, kpi: str | None = None) -> list:
    """Curated, known-good tags for common measures (throughput, power, energy, raw water) in a part of the plant."""
    return catalog.golden_tags(con(), scope, kpi)


@mcp.tool()
@logged
def get_tag_details(ids: list[str]) -> list:
    """Everything the catalogue knows about the given tags (catalogue ids, asset paths or point names)."""
    rows = catalog.details(con(), ids[:L["tags_per_call"]])
    for r in rows:
        r["last_time"] = local_time(r["last_time"])
    return rows


def resolve(ids: list[str]) -> list[dict]:
    if len(ids) > L["tags_per_call"]:
        raise ValueError(f"At most {L['tags_per_call']} tags per call; got {len(ids)}.")
    rows = catalog.details(con(), ids)
    found = {str(r["id"]) for r in rows} | {r["path"] for r in rows} | {r["point"].lower() for r in rows}
    missing = [i for i in ids if str(i) not in found and str(i).lower() not in found]
    if missing:
        raise ValueError(f"Not in the catalogue: {', '.join(map(str, missing))}. Use search_tags first.")
    return rows


@mcp.tool()
@logged
def get_current_values(ids: list[str]) -> list:
    """The latest value of each tag, with its time and whether the historian marks it good."""
    rows = resolve(ids)
    items = {i["WebId"]: i for i in client().streamset("end", [r["webid"] for r in rows])}
    out = []
    for r in rows:
        it = items.get(r["webid"], {})
        v = it.get("Value", {})
        val = v.get("Value")
        out.append({"id": r["id"], "path": r["path"], "unit": r["unit"],
                    "value": val.get("Name") if isinstance(val, dict) else val, "time": local_time(v.get("Timestamp")),
                    "good": v.get("Good"), "error": (it.get("Errors") or [None])[0]})
    return out


@mcp.tool()
@logged
def get_timeseries(ids: list[str], start: str = "*-1d", end: str = "*", mode: str = "summary",
                   interval: str = "1h", summaries: list[str] | None = None, units: str | None = None) -> dict:
    """Read data for chosen tags and save it as a dataset file. Returns a short summary per tag, the dataset id and
    its file path. Times: ISO or relative (*-30d, t, y). mode: summary (time-weighted, per interval; the default),
    interpolated (a value every interval) or recorded (raw records, short windows only). summaries: Average,
    Minimum, Maximum, StdDev, Count, Total. units: convert to this unit where possible (kW, MW, m3/h, L/s, kPa, bar)."""
    rows = resolve(ids)
    summaries = summaries or ["Average"]
    c, webids = client(), [r["webid"] for r in rows]
    if mode == "summary":
        items = c.streamset("summary", webids, startTime=start, endTime=end, summaryType=summaries,
                            summaryDuration=interval, calculationBasis="TimeWeighted")
        get = lambda it: [(x["Type"], x["Value"]) for x in it.get("Items", [])]
    elif mode == "interpolated":
        items = c.streamset("interpolated", webids, startTime=start, endTime=end, interval=interval)
        get = lambda it: [("Value", x) for x in it.get("Items", [])]
    elif mode == "recorded":
        items = c.streamset("recorded", webids, startTime=start, endTime=end, maxCount=L["recorded_values"])
        get = lambda it: [("Value", x) for x in it.get("Items", [])]
    else:
        raise ValueError("mode must be summary, interpolated or recorded.")
    by_web = {it["WebId"]: it for it in items}
    table, stats, notes = {}, [], []
    for r in rows:
        it = by_web.get(r["webid"], {})
        if it.get("Errors"):
            notes.append(f"{r['path']}: {it['Errors'][0]}")
            continue
        factor = CONVERT.get((r["unit"], units), 1) if units else 1
        unit = units if units and factor != 1 or units == r["unit"] else r["unit"]
        vals = []
        for typ, v in get(it):
            val = v.get("Value")
            if isinstance(val, dict):          # a digital state or a system value such as No Data
                val = val.get("Value") if not val.get("IsSystem") else None
            t = local_time(v["Timestamp"])
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                val = val * factor
                vals.append(val)
            table.setdefault(t, {})[f"{r['id']}|{typ}"] = val
        n_limit = L["summary_intervals"] if mode == "summary" else L["interpolated_values"]
        if mode != "recorded" and len(vals) > n_limit:
            raise ValueError(f"Too many values for {r['path']}: use a longer interval.")
        stats.append({"id": r["id"], "path": r["path"], "unit": unit, "values": len(vals),
                      "mean": round(sum(vals) / len(vals), 4) if vals else None,
                      "min": min(vals) if vals else None, "max": max(vals) if vals else None})
    DATASETS.mkdir(parents=True, exist_ok=True)
    ds = datetime.now(TZ).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    cols = sorted({k for v in table.values() for k in v})
    with (DATASETS / f"{ds}.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time"] + cols)
        for t in sorted(table):
            w.writerow([t] + [table[t].get(k, "") for k in cols])
    times = sorted(table)
    provenance = {"tags": [{"id": r["id"], "path": r["path"], "point": r["point"], "unit": r["unit"]} for r in rows],
                  "window": {"requested": [start, end], "first": times[0] if times else None,
                             "last": times[-1] if times else None, "timezone": S["timezone"]},
                  "mode": mode, "interval": interval if mode != "recorded" else None,
                  "basis": "time-weighted" if mode == "summary" else ("interpolated" if mode == "interpolated" else "raw records"),
                  "summaries": summaries if mode == "summary" else None, "units_requested": units,
                  "columns": "time, then one column per tag and summary: <catalogue id>|<summary>",
                  "queried": datetime.now(TZ).isoformat(timespec="seconds")}
    (DATASETS / f"{ds}.json").write_text(json.dumps(provenance, indent=1))
    return {"dataset_id": ds, "file": str(DATASETS / f"{ds}.csv"), "rows": len(times), "tags": stats,
            "notes": notes, "provenance": provenance}


@mcp.resource("pi://datasets/{dataset_id}")
def dataset(dataset_id: str) -> str:
    """A dataset written by get_timeseries: its metadata and its CSV."""
    meta = (DATASETS / f"{dataset_id}.json").read_text()
    return meta + "\n\n" + (DATASETS / f"{dataset_id}.csv").read_text()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--http", action="store_true")
    ap.add_argument("--port", type=int, default=8712)
    a = ap.parse_args()
    if not a.http:
        mcp.run("stdio")
        return
    key = os.environ.get("MCP_API_KEY")
    if not key:
        raise SystemExit("Set MCP_API_KEY to serve over HTTP.")
    import uvicorn
    inner = mcp.streamable_http_app()

    async def app(scope, receive, send):  # the API key in front of the HTTP transport
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            if headers.get(b"x-api-key", b"").decode() != key and headers.get(b"authorization", b"").decode() != f"Bearer {key}":
                await send({"type": "http.response.start", "status": 401, "headers": [(b"content-type", b"text/plain")]})
                await send({"type": "http.response.body", "body": b"API key required"})
                return
        await inner(scope, receive, send)

    uvicorn.run(app, host="127.0.0.1", port=a.port)


if __name__ == "__main__":
    main()
