"""The scheduled, read-only crawler that builds the tag catalogue.

Steps: discover, elements, attributes, points, health, then enrich, index and publish (catalog.build), then report.
Each reading step saves its output in the run's folder, so a run that stops can resume where it stopped.

    uv run python crawler.py run --base-url http://127.0.0.1:8711/piwebapi
    uv run python crawler.py run --resume <run id>
    uv run python crawler.py run --watch 24h
"""
import argparse, json, os, shutil, sqlite3, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import catalog
from connector import Client, HistorianError

HERE = Path(__file__).parent
DEFAULT_DIR = HERE / "local" / "catalog"
KEEP_RUNS = 3
FIELDS = {
    "elements": "Items.WebId;Items.Name;Items.Path;Items.TemplateName;Items.Description",
    "attributes": "Items.WebId;Items.Name;Items.Path;Items.Type;Items.DefaultUnitsNameAbbreviation;Items.ConfigString",
    "points": "Items.WebId;Items.Name;Items.Path;Items.Descriptor;Items.PointType;Items.EngineeringUnits",
}


def iso_to_epoch(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def health_of(item: dict, stale_after: float, ref: float) -> dict:
    """ref: the historian's own clock (Client.server_time), so staleness is measured against the time it is there, not
    against the newest sample: if every tag stopped a week ago, every tag is stale."""
    if item.get("Errors"):
        return {"health": "broken_ref", "error": item["Errors"][0]}
    v = item.get("Value", {})
    val = v.get("Value")
    if isinstance(val, dict) and val.get("IsSystem"):
        return {"health": "no_data" if val.get("Name") == "No Data" else "bad_quality",
                "value": val.get("Name"), "time": v.get("Timestamp")}
    if not v.get("Good", True):
        return {"health": "bad_quality", "value": val, "time": v.get("Timestamp")}
    age = ref - iso_to_epoch(v["Timestamp"])
    return {"health": "stale" if age > stale_after else "ok",
            "value": val["Name"] if isinstance(val, dict) else val, "time": v.get("Timestamp")}


def run(client: Client, database_path: str, out_dir: Path, resume: str | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = resume or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rdir = out_dir / "runs" / run_id
    rdir.mkdir(parents=True, exist_ok=True)
    started, requests0 = time.time(), client.requests
    rules = catalog.rules()
    timings = {}

    def step(name, fn):
        f = rdir / f"{name}.json"
        if f.exists():
            return json.loads(f.read_text())
        t = time.time()
        data = fn()
        timings[name] = round(time.time() - t, 2)
        f.write_text(json.dumps(data))
        return data

    db = step("discover", lambda: {"database": client.database(database_path), "data_server": client.data_server()})
    dbw, dsw = db["database"]["WebId"], db["data_server"]["WebId"]
    elements = step("elements", lambda: list(client.pages(f"/assetdatabases/{dbw}/elements", searchFullHierarchy="true",
                                                          selectedFields=FIELDS["elements"])))
    attributes = step("attributes", lambda: list(client.pages(f"/assetdatabases/{dbw}/elementattributes",
                                                              searchFullHierarchy="true", selectedFields=FIELDS["attributes"])))
    points = step("points", lambda: list(client.pages(f"/dataservers/{dsw}/points", nameFilter="*",
                                                      selectedFields=FIELDS["points"])))

    def read_health():
        linked = {a["ConfigString"].rsplit("\\", 1)[-1] for a in attributes}
        webids = [a["WebId"] for a in attributes] + [p["WebId"] for p in points if p["Name"] not in linked]
        stale_after = rules["stale_after_hours"] * 3600
        items = client.streamset("end", webids, selectedFields="Items.WebId;Items.Errors;Items.Value")
        stamps = [iso_to_epoch(i["Value"]["Timestamp"]) for i in items if i.get("Value", {}).get("Timestamp")]
        ref = client.server_time() or time.time()
        out = {item["WebId"]: health_of(item, stale_after, ref) for item in items}
        out["_historian_time"] = datetime.fromtimestamp(ref, timezone.utc).isoformat()
        out["_newest_sample"] = datetime.fromtimestamp(max(stamps), timezone.utc).isoformat() if stamps else None
        return out

    health = step("health", read_health)

    def read_earliest():  # the oldest record of the first healthy attribute, taken as where the archive starts (one tag, not all)
        for a in attributes:
            if health.get(a["WebId"], {}).get("health") == "ok":
                items = client.get(f"/streams/{a['WebId']}/recorded", startTime="*-30y", endTime="*", maxCount=1).get("Items", [])
                if items:
                    return items[0]["Timestamp"]
        return None

    earliest = step("earliest", read_earliest)
    t = time.time()
    tmp = rdir / "catalog.sqlite"
    counts = catalog.build(tmp, {"database_path": database_path, "elements": elements, "attributes": attributes,
                                 "points": points, "health": health}, rules)
    timings["enrich_index"] = round(time.time() - t, 2)

    # report: counts, health, and the difference from the catalogue now in use
    live = out_dir / "catalog.sqlite"
    diff = None
    if live.exists():
        old = {r[0] for r in sqlite3.connect(live).execute("SELECT path FROM tags")}
        new = {r[0] for r in sqlite3.connect(tmp).execute("SELECT path FROM tags")}
        diff = {"added": len(new - old), "removed": len(old - new),
                "added_examples": sorted(new - old)[:5], "removed_examples": sorted(old - new)[:5]}
    report = {"run_id": run_id, "historian_time": health.get("_historian_time"), "newest_sample": health.get("_newest_sample"), "historian_earliest": earliest, "elements": len(elements), "attributes": len(attributes), "points": len(points),
              **counts, "diff": diff, "requests": client.requests - requests0, "seconds": round(time.time() - started, 1),
              "step_seconds": timings}
    con = sqlite3.connect(tmp)
    con.execute("INSERT INTO crawl_runs VALUES (?,?,?,?)",
                (run_id, datetime.fromtimestamp(started, timezone.utc).isoformat(),
                 datetime.now(timezone.utc).isoformat(), json.dumps(report)))
    con.commit(); con.close()

    # publish: swap the new catalogue in atomically; keep the last few runs
    shutil.copy2(tmp, out_dir / "catalog.sqlite.new")
    os.replace(out_dir / "catalog.sqlite.new", live)
    (rdir / "report.json").write_text(json.dumps(report, indent=1))
    for old in sorted((out_dir / "runs").iterdir())[:-KEEP_RUNS]:
        shutil.rmtree(old)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["run"])
    ap.add_argument("--base-url", default=os.environ.get("HISTORIAN_URL", "http://127.0.0.1:8711/piwebapi"))
    ap.add_argument("--database", default="\\\\EXAMPLE-AF\\Operations")
    ap.add_argument("--auth", default=os.environ.get("HISTORIAN_AUTH", "basic"))
    ap.add_argument("--user", default=os.environ.get("HISTORIAN_USER", "demo"))
    ap.add_argument("--password", default=os.environ.get("HISTORIAN_PASSWORD", "demo-password"))
    ap.add_argument("--out", type=Path, default=DEFAULT_DIR)
    ap.add_argument("--resume")
    ap.add_argument("--watch", help="run again every interval, e.g. 24h")
    a = ap.parse_args()
    client = Client(a.base_url, a.auth, a.user, a.password)
    while True:
        try:
            print(json.dumps(run(client, a.database, a.out, a.resume), indent=1))
        except HistorianError as e:
            print(f"crawl failed: {e}")
        if not a.watch:
            return
        a.resume = None
        n, unit = float(a.watch[:-1]), a.watch[-1]
        time.sleep(n * {"m": 60, "h": 3600, "d": 86400}[unit])


if __name__ == "__main__":
    main()
