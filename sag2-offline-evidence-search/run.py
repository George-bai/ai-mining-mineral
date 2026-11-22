"""One offline search run: a fresh SAG-Wiki index of one folder, every question in fast and/or deep mode.

Meant to run inside a network namespace that has only loopback (see offline.sh); it refuses to start otherwise.
For deep search it starts decide.py with the given scorer and points SAG-Wiki at it. Results go to
<out>/<question id>.<mode>.json: the passages in the order SAG-Wiki returns them, the time taken and, for deep
search, the decision requests SAG-Wiki made for that question.

python run.py --sag <sag binary> --corpus <folder> --questions questions.json --out <dir> --modes fast,deep \
              --scorer ce:<model dir> --label tinybert --limit 10
"""
import argparse, json, os, socket, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent


def assert_offline():
    names = sorted(n for _, n in socket.if_nameindex())  # this namespace's interfaces (/sys shows the host's)
    if names != ["lo"]:
        sys.exit(f"refusing to run: network interfaces {names}, expected only lo")
    for host in ("1.1.1.1", "8.8.8.8"):
        try:
            socket.create_connection((host, 443), timeout=2).close()
            sys.exit(f"refusing to run: reached {host}")
        except OSError:
            pass
    return names


def sag(binary, *args, timeout=3600):
    r = subprocess.run([binary, *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"sag {' '.join(args[:2])}: exit {r.returncode}: {r.stderr.strip()[:500]}")
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sag", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--questions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--modes", default="fast,deep")
    ap.add_argument("--scorer")
    ap.add_argument("--label", default="none")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--port", type=int, default=8700)
    ap.add_argument("--sag-settings", help="JSON merged into SAG-Wiki's saved settings, for a model that cannot take the "
                    "defaults: a smaller decision batch on a small GPU, a longer wait and fewer parallel requests on a CPU")
    a = ap.parse_args()

    meta = {"interfaces": assert_offline(), "label": a.label, "scorer": a.scorer, "limit": a.limit, "modes": a.modes.split(","),
            "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="sagrun-", dir=out))
    os.environ.update(HOME=str(work / "home"), SAG_DATA_DIR=str(work / "data"))
    (work / "home").mkdir()
    corpus = str(Path(a.corpus).resolve())
    questions = json.loads(Path(a.questions).read_text())
    questions = questions["questions"] if isinstance(questions, dict) else questions
    modes = a.modes.split(",")
    log = out / "decisions.jsonl"
    proc = None
    try:
        if "deep" in modes:
            dlog = open(out / "decide.log", "w")
            proc = subprocess.Popen([sys.executable, "-I", str(HERE / "decide.py"), "--port", str(a.port),
                                     "--scorer", a.scorer, "--log", str(log)], stdout=dlog, stderr=subprocess.STDOUT)
            while "ready" not in (out / "decide.log").read_text():
                if proc.poll() is not None:
                    sys.exit("decide.py stopped: " + (out / "decide.log").read_text()[-2000:])
                time.sleep(1)
            sag(a.sag, "config", "--url", f"http://127.0.0.1:{a.port}/v1", "--model", a.label, "--auth", "none")
        t = time.time()
        meta["add"] = json.loads(sag(a.sag, "add", corpus, "--json", "--timeout", "3600"))
        meta["check"] = json.loads(subprocess.run([a.sag, "check", corpus, "--json"], capture_output=True, text=True).stdout)
        meta["index_seconds"] = round(time.time() - t, 2)
        files = list(Path(corpus).glob("*.md"))
        if not files or meta["check"].get("indexed_files") != len(files) or not meta["check"].get("index_ready"):
            sys.exit(f"index not ready or incomplete: {meta['check']}")
        meta["version"] = sag(a.sag, "--version").strip()
        if a.sag_settings:  # SAG-Wiki keeps its settings as JSON in sag.sqlite; change them with the service stopped
            import sqlite3
            sag(a.sag, "service", "stop")
            db = sqlite3.connect(work / "data" / "sag.sqlite")
            prefs = json.loads(db.execute("select value from preferences where id = 1").fetchone()[0])
            for k, v in json.loads(a.sag_settings).items():
                prefs[k] = {**prefs[k], **v} if isinstance(v, dict) else v
            db.execute("update preferences set value = ? where id = 1", (json.dumps(prefs),))
            db.commit(); db.close()
            meta["sag_settings"] = json.loads(a.sag_settings)
            sag(a.sag, "add", corpus, "--json", "--timeout", "3600")  # the restarted service re-checks the folder first
        key = None
        if "fast" in modes:
            sag(a.sag, "api", "start", "--host", "127.0.0.1", "--port", str(a.port + 1000))
            key = json.loads(sag(a.sag, "api", "key", "create", "--name", "run", "--all", "--json"))
            key = key.get("key") or key.get("api_key") or key.get("secret")
        for q in questions:
            for mode in modes:
                t = time.time()
                lines_before = sum(1 for _ in open(log)) if log.exists() else 0
                if mode == "fast":
                    body = json.dumps({"query": q["text"], "mode": "fast", "paths": [corpus], "limit": a.limit}).encode()
                    req = urllib.request.Request(f"http://127.0.0.1:{a.port + 1000}/v1/search", body,
                                                 {"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
                    res = json.load(urllib.request.urlopen(req, timeout=120))
                else:
                    res = json.loads(sag(a.sag, q["text"], corpus, "-m", str(a.limit), "--json", "-c", "--timeout", "3600"))
                rec = {"question": q["id"], "text": q["text"], "mode": mode, "label": a.label,
                       "seconds": round(time.time() - t, 2), "results": res.get("results", []), "raw": res}
                if mode == "deep":
                    with open(log) as f:
                        rec["decisions"] = [json.loads(x) for i, x in enumerate(f) if i >= lines_before]
                (out / f"{q['id']}.{mode}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1))
                print(f"{a.label} {q['id']} {mode}: {len(rec['results'])} passages, {rec['seconds']} s", flush=True)
        meta["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        (out / "run.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    finally:
        subprocess.run([a.sag, "service", "stop"], capture_output=True)
        if proc:
            proc.terminate()


if __name__ == "__main__":
    main()
