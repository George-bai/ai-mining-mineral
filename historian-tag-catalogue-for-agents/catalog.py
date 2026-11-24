"""The tag catalogue: a SQLite file the agent's tools search instead of loading the whole tag list.

enrich() turns what the crawler read into words a person would use; build() writes the catalogue;
search() ranks tags for a question, with the reason each one matched; baseline() is plain keyword search on the
raw names, to measure what enrichment adds.
"""
import json, re, sqlite3
from pathlib import Path

import yaml

RULES = Path(__file__).parent / "config" / "enrichment.yaml"

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE elements (path TEXT PRIMARY KEY, name TEXT, template TEXT, parent TEXT, level TEXT, depth INT);
CREATE TABLE tags (
  id INTEGER PRIMARY KEY, source TEXT, path TEXT UNIQUE, name TEXT, element TEXT,
  site TEXT, concentrator TEXT, area TEXT, equipment TEXT, template TEXT,
  point TEXT, descriptor TEXT, unit TEXT, quantity TEXT, variant TEXT,
  health TEXT, last_value TEXT, last_time TEXT, webid TEXT, digital INT,
  search_text TEXT, raw_text TEXT);
CREATE INDEX tags_point ON tags(lower(point));
CREATE INDEX tags_element ON tags(element);
CREATE VIRTUAL TABLE tags_fts USING fts5(search_text, content='tags', content_rowid='id', tokenize='unicode61');
CREATE VIRTUAL TABLE tags_raw_fts USING fts5(raw_text, content='tags', content_rowid='id', tokenize='unicode61');
CREATE TABLE golden_tags (tag_id INT, kpi TEXT, concentrator_path TEXT);
CREATE TABLE crawl_runs (run_id TEXT PRIMARY KEY, started TEXT, finished TEXT, report TEXT);
"""


def rules(path: Path = RULES) -> dict:
    return yaml.safe_load(path.read_text())


# ---------- enrichment ----------
def decode_name(text: str, r: dict) -> str:
    """Point names and descriptors written in a site's codes, as words."""
    text = text or ""
    for pattern, repl in r["aliases"]:
        text = re.sub(pattern, repl, text)
    words = []
    for tok in re.split(r"[^A-Za-z0-9]+", text):
        if not tok:
            continue
        up = tok.upper()
        legacy = re.fullmatch(r"(\d)([A-Z]{2})(\d{3})", up)  # an old DCS name: area digit, code, loop (3FT104)
        if legacy and legacy.group(1) in r["area_number"]:
            words.append(f"{r['area_number'][legacy.group(1)]} {r['instrument_codes'].get(legacy.group(2), '')} loop {up}")
            continue
        m = re.fullmatch(r"([A-Z]+?)(\d+)", up)
        if m and m.group(1) in r["equipment_abbrev"]:
            words.append(f"{r['equipment_abbrev'][m.group(1)]} {m.group(2)}")
        elif up in r["attribute_abbrev"]:
            words.append(r["attribute_abbrev"][up])
        elif up in r["area_abbrev"]:
            words.append(r["area_abbrev"][up])
        elif up in r["instrument_codes"]:
            words.append(r["instrument_codes"][up])
        elif re.fullmatch(r"\d{4}", up) and up[0] in r["area_number"]:
            words.append(f"{r['area_number'][up[0]]} loop {up}")
        else:
            words.append(tok.lower())
    return " ".join(words)


def quantity_of(unit: str, code: str, r: dict) -> str:
    return r["units"].get(unit) or r["instrument_codes"].get(code) or ""


def variant_of(name: str, digital: bool) -> str:
    n = name.upper()
    if n.endswith(".ALM") or n.endswith(" ALARM"):
        return "alarm"
    if n.endswith(".QC") or n.endswith(" QC"):
        return "qc"
    if n.endswith(".CALC") or n.endswith(" CALC"):
        return "calc"
    return "status" if digital else "primary"


def code_of(point: str) -> str:
    m = re.search(r"(?:^|[-:\d])([A-Z]{2})-?\d{3}", point or "")
    return m.group(1) if m else ""


# ---------- build ----------
def build(db_path: Path, crawl: dict, r: dict | None = None) -> dict:
    """Write a catalogue from the crawler's outputs (elements, attributes, points, health). Returns counts."""
    r = r or rules()
    db_path.unlink(missing_ok=True)
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    root = crawl["database_path"]
    levels = r["levels"]
    for e in crawl["elements"]:
        parts = e["Path"][len(root) + 1:].split("\\")
        con.execute("INSERT INTO elements VALUES (?,?,?,?,?,?)",
                    (e["Path"], e["Name"], e.get("TemplateName", ""), e["Path"].rsplit("\\", 1)[0],
                     levels[min(len(parts), len(levels)) - 1], len(parts)))
    template = {e["Path"]: e.get("TemplateName", "") for e in crawl["elements"]}
    points = {p["Name"]: p for p in crawl["points"]}
    health = crawl["health"]
    linked = set()
    rows = []
    for a in crawl["attributes"]:
        point = a["ConfigString"].rsplit("\\", 1)[-1]
        p = points.get(point)
        if p:
            linked.add(point)
        rows.append(dict(source="attribute", path=a["Path"], name=a["Name"], element=a["Path"].split("|")[0],
                         point=point, descriptor=p["Descriptor"] if p else "", unit=a.get("DefaultUnitsNameAbbreviation", ""),
                         digital=a.get("Type") == "EnumerationValue", webid=a["WebId"],
                         health=health.get(a["WebId"], {})))
    for name, p in points.items():
        if name not in linked:
            rows.append(dict(source="point", path=p["Path"], name=name, element="", point=name,
                             descriptor=p["Descriptor"], unit=p["EngineeringUnits"], digital=p["PointType"] == "Digital",
                             webid=p["WebId"], health=health.get(p["WebId"], {})))
    for row in rows:
        parts = row["element"][len(root) + 1:].split("\\") if row["element"] else []
        loc = dict(zip(levels, parts + [""] * len(levels)))
        code = code_of(row["point"])
        quantity = quantity_of(row["unit"], code, r)
        if row["digital"]:
            quantity = "status"
        variant = variant_of(row["name"] if row["source"] == "attribute" else row["point"], row["digital"])
        decoded = decode_name(row["point"], r) + " " + decode_name(row["descriptor"], r)
        location = " ".join(x for x in (loc["site"], loc["concentrator"], loc["area"], loc["equipment"]) if x)
        if not location:  # an unlinked point: the location comes from its name only
            location = decoded
            m = re.search(r"site ([a-z]{1,2}) concentrator (\d)", decoded)
            if m:
                loc["site"], loc["concentrator"] = f"Site {m.group(1).upper()}", f"Concentrator {m.group(2)}"
        search_text = " ".join([row["name"].split("|")[-1], location, decoded, row["point"], row["unit"], quantity, variant,
                                template.get(row["element"], "")]).lower()
        raw_text = " ".join([row["path"], row["point"], row["descriptor"]])
        h = row["health"]
        con.execute("INSERT INTO tags (source,path,name,element,site,concentrator,area,equipment,template,point,"
                    "descriptor,unit,quantity,variant,health,last_value,last_time,webid,digital,search_text,raw_text) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (row["source"], row["path"], row["name"], row["element"], loc["site"], loc["concentrator"],
                     loc["area"], loc["equipment"], template.get(row["element"], ""), row["point"], row["descriptor"], row["unit"], quantity, variant,
                     h.get("health", "unknown"), json.dumps(h.get("value")), h.get("time"), row["webid"],
                     int(row["digital"]), search_text, raw_text))
    con.execute("INSERT INTO tags_fts(tags_fts) VALUES ('rebuild')")
    con.execute("INSERT INTO tags_raw_fts(tags_raw_fts) VALUES ('rebuild')")
    conc_paths = [x[0] for x in con.execute("SELECT path FROM elements WHERE level='concentrator'")]
    for g in r["golden_tags"]:
        for c in conc_paths:
            row = con.execute("SELECT id FROM tags WHERE path=? AND health='ok'", (f"{c}\\{g['path']}",)).fetchone()
            if row:
                con.execute("INSERT INTO golden_tags VALUES (?,?,?)", (row[0], g["kpi"], c))
    con.execute("INSERT INTO meta VALUES ('rules', ?)", (json.dumps(r),))
    con.execute("INSERT INTO meta VALUES ('database_path', ?)", (root,))
    con.commit()
    out = {"tags": con.execute("SELECT count(*) FROM tags").fetchone()[0],
           "by_health": dict(con.execute("SELECT health, count(*) FROM tags GROUP BY health").fetchall()),
           "by_variant": dict(con.execute("SELECT variant, count(*) FROM tags GROUP BY variant").fetchall()),
           "unlinked_points": con.execute("SELECT count(*) FROM tags WHERE source='point'").fetchone()[0],
           "golden_tags": con.execute("SELECT count(*) FROM golden_tags").fetchone()[0]}
    con.close()
    return out


# ---------- search ----------
def connect(db_path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _rules(con) -> dict:
    return json.loads(con.execute("SELECT value FROM meta WHERE key='rules'").fetchone()[0])


WORD = re.compile(r"[a-z0-9]+")
STOP = {"the", "a", "an", "of", "for", "at", "in", "on", "what", "is", "show", "me", "and", "to", "how", "much",
        "which", "was", "are", "s", "past", "last", "week", "month", "day", "yesterday", "today", "over", "by",
        "trend", "plot", "value", "values", "current", "currently", "now", "get", "give", "with", "from", "all"}


LOC_WORDS = {"site", "concentrator", "plant", "conc", "con"}


def forms(w: str) -> list[str]:
    """A word and its plain base forms ("drawing" -> "draw", "dosing" -> "dos", "dose"), for looking up rules."""
    out = [w]
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            out += [w[:-len(suf)], w[:-len(suf)] + "e"]
    return out


def parse_location(text: str) -> dict:
    t = text.lower()
    loc = {}
    m = re.search(r"\bsite\s+([a-z]{1,2})\b", t) or re.search(r"\bs([a-z])[-_ ]?c\d", t)
    if m:
        loc["site"] = f"Site {m.group(1).upper()}"
    m = re.search(r"\b(?:concentrator|conc|con|plant)\.?\s*(\d)\b", t) or re.search(r"\bs[a-z]{1,2}[-_]?c(\d)\b", t)
    if m:
        loc["concentrator"] = f"Concentrator {m.group(1)}"
    return loc


def find_assets(con, text: str, limit: int = 10) -> list[dict]:
    """Asset-tree paths for a place named in words ("Site A Plant 1", "ball mill 2 at site c")."""
    loc = parse_location(text)
    loc_tokens = LOC_WORDS | {v.split()[-1].lower() for v in loc.values()}
    words = [w for w in WORD.findall(text.lower()) if w not in STOP and w not in loc_tokens]
    if not words:  # only a place: the place itself
        want = "\\".join(loc[k] for k in ("site", "concentrator") if k in loc).lower()
        rows = con.execute("SELECT path, name, template, level, depth FROM elements").fetchall()
        return [dict(r) for r in rows if want and r["path"].lower().endswith("\\" + want)][:limit]
    rows = con.execute("SELECT path, name, template, level, depth FROM elements").fetchall()
    out = []
    for r in rows:
        p = r["path"].lower()
        if "site" in loc and f"\\{loc['site'].lower()}" not in p:
            continue
        if "concentrator" in loc and f"\\{loc['concentrator'].lower()}" not in p:
            continue
        own = r["name"].lower()
        hits = sum(w in own.split() or w == own for w in words)
        if words and not hits:
            continue
        out.append((-hits, -r["depth"] if words else r["depth"], r["path"], dict(r)))
    out.sort(key=lambda x: (x[0], x[1], x[2]))
    return [x[3] for x in out[:limit]]


def search(con, query: str, scope: str | None = None, quantity: str | None = None, limit: int = 10) -> list[dict]:
    """Ranked tags for a question. Keyword BM25 over the enriched text, then boosts and penalties."""
    r = _rules(con)
    q = query.lower()
    # an exact point name in the question wins outright
    exact = [row for tok in re.findall(r"[a-z0-9][a-z0-9_.:\-]{4,}", q)
             for row in con.execute("SELECT * FROM tags WHERE lower(point)=?", (tok.strip('.'),)).fetchall()]
    loc = parse_location(q)
    words = [w for w in WORD.findall(q) if w not in STOP]
    expanded = set(words)
    for w in words:
        for f in forms(w):
            expanded.update(r["synonyms"].get(f, []))
    loc_words = LOC_WORDS | {v.split()[-1].lower() for v in loc.values()}
    terms = sorted(t for t in expanded if t not in loc_words and len(t) > 1)
    if not terms and not exact:
        return []
    word_forms = {f for w in words for f in forms(w)}
    named = [k for k, ws in r["quantity_words"].items()
             if any(w in q for w in ws if " " in w) or any(w in word_forms for w in ws)]
    # "what dose are we running": a measured quantity in the question outranks a run-status reading of "running"
    measured = [k for k in named if k != "status"]
    asked_q = quantity or (measured[0] if measured else (named[0] if named else None))
    asked_variant = {v for v, ws in {"qc": ["qc"], "calc": ["calc", "calculated"], "alarm": ["alarm", "alm"],
                                     "status": ["status", "running", "stopped", "online"]}.items()
                     if any(w in words for w in ws)}
    if measured and not quantity:
        asked_variant.discard("status")
    # "ball mill 2", "tank 3", "cv-101": a word and its number belong together
    phrases = sorted({f"{a} {b}" for a, b in re.findall(r"([a-z]+)[\s-]+(\d{1,3})\b", q)
                      if a not in loc_words and a not in STOP})
    fts = " OR ".join([f'"{t}"' for t in terms] + [f'"{p}"' for p in phrases]) or '""'
    where, args = "", [fts]
    if scope:
        where = " AND (t.element = ? OR t.element LIKE ? OR t.path LIKE ?)"
        args += [scope, scope + "\\%", scope + "%"]
    for k in ("site", "concentrator"):  # a place named in the question narrows the search to it
        if loc.get(k):
            where += f" AND lower(t.{k}) = ?"
            args.append(loc[k].lower())
    sql = ("SELECT t.*, bm25(tags_fts) AS bm FROM tags_fts JOIN tags t ON t.id = tags_fts.rowid "
           "WHERE tags_fts MATCH ?{} ORDER BY bm LIMIT 400")
    cands = con.execute(sql.format(where), args).fetchall() if terms else []
    golden = {row[0]: row[1] for row in con.execute("SELECT tag_id, kpi FROM golden_tags")}
    scored = {}
    for row in cands:
        text = set(WORD.findall(row["search_text"]))
        matched = sorted(t for t in terms if t in text)
        own = [w for w in words if w not in loc_words and len(w) > 1]
        hit_own = sum(w in text or any(x in text for x in r["synonyms"].get(w, [])) for w in own)
        # the words the user typed count most; a synonym only stands in for its word
        score = -row["bm"] + 8 * hit_own / max(len(own), 1) + 2 * sum(w in text for w in own) / max(len(own), 1)
        why = [f"matched: {', '.join(matched)}"] if matched else []
        for p in phrases:
            if re.search(rf"\b{re.escape(p)}\b", row["search_text"]):
                score += 4; why.append(f'"{p}"')
        if loc.get("site"):
            if row["site"].lower() == loc["site"].lower():
                score += 3; why.append(loc["site"])
            else:
                score -= 6
        if loc.get("concentrator"):
            if row["concentrator"].lower() == loc["concentrator"].lower():
                score += 2; why.append(loc["concentrator"])
            else:
                score -= 4
        if asked_q:
            if row["quantity"] == asked_q:
                score += 3; why.append(f"quantity {asked_q}")
            elif row["quantity"]:
                score -= 2
        if row["variant"] in ("qc", "calc", "alarm") and row["variant"] not in asked_variant:
            score -= 4; why.append(f"{row['variant']} variant, ranked down")
        if row["variant"] == "status" and "status" not in asked_variant:
            score -= 2
        if row["health"] != "ok":  # a tie-breaker only: the right tag with bad health should still show, flagged
            score -= 2; why.append(f"health: {row['health']}")
        if row["id"] in golden:
            score += 3; why.append(f"golden tag: {golden[row['id']]}")
        if row["source"] == "point":
            score -= 1; why.append("not in the asset tree")
        scored[row["id"]] = (score, row, why)
    for row in exact:
        scored[row["id"]] = (1e6, row, ["exact point name"])
    ranked = sorted(scored.values(), key=lambda x: -x[0])[:limit]
    return [dict(id=row["id"], path=row["path"], point=row["point"], unit=row["unit"], quantity=row["quantity"],
                 variant=row["variant"], health=row["health"], last_value=json.loads(row["last_value"] or "null"),
                 last_time=row["last_time"], why="; ".join(why), score=round(s, 2)) for s, row, why in ranked]


def baseline(con, query: str, limit: int = 10) -> list[dict]:
    """Plain keyword search: the question's words against raw names, descriptors and paths. No enrichment."""
    words = [w for w in WORD.findall(query.lower()) if w not in STOP]
    if not words:
        return []
    fts = " OR ".join(f'"{w}"' for w in words)
    rows = con.execute("SELECT t.id, t.path, t.point FROM tags_raw_fts JOIN tags t ON t.id = tags_raw_fts.rowid "
                       "WHERE tags_raw_fts MATCH ? ORDER BY bm25(tags_raw_fts) LIMIT ?", (fts, limit)).fetchall()
    return [dict(id=r["id"], path=r["path"], point=r["point"]) for r in rows]


def golden_tags(con, scope: str | None = None, kpi: str | None = None) -> list[dict]:
    sql = "SELECT g.kpi, t.path, t.point, t.unit, t.health FROM golden_tags g JOIN tags t ON t.id=g.tag_id WHERE 1=1"
    args = []
    if scope:
        sql += " AND (g.concentrator_path = ? OR g.concentrator_path LIKE ? OR ? LIKE g.concentrator_path || '%')"
        args += [scope, scope + "\\%", scope]
    if kpi:
        sql += " AND g.kpi LIKE ?"
        args.append(f"%{kpi}%")
    return [dict(r) for r in con.execute(sql + " LIMIT 50", args)]


def details(con, ids: list) -> list[dict]:
    rows = []
    for i in ids:
        row = con.execute("SELECT * FROM tags WHERE id=? OR path=? OR lower(point)=lower(?)", (i, str(i), str(i))).fetchone()
        if row:
            d = dict(row)
            d.pop("search_text"); d.pop("raw_text")
            d["last_value"] = json.loads(d["last_value"] or "null")
            rows.append(d)
    return rows
