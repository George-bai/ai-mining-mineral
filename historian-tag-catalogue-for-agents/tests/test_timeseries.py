"""get_timeseries keeps each summary column apart, never converts Count, and leaves bad-quality values out
(found by the external review of 24 Nov 2026: Count and a bad value had been averaged into a tag's mean)."""
import csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import connector, crawler  # noqa: E402
import mcp_server as M  # noqa: E402

NOW = M.when("2026-11-23T00:00:00+10:00", 0)   # the stand-in's fixed clock


def test_summaries_kept_apart(tmp_path, monkeypatch):
    item = {"WebId": "w1", "Items": [
        {"Type": "Average", "Value": {"Timestamp": "2026-11-20T00:00:00Z", "Value": 1000.0, "Good": True}},
        {"Type": "Count", "Value": {"Timestamp": "2026-11-20T00:00:00Z", "Value": 60, "Good": True}},
        {"Type": "Average", "Value": {"Timestamp": "2026-11-20T01:00:00Z", "Value": 99999.0, "Good": False}}]}
    fake = type("C", (), {"streamset": lambda self, *a, **k: [item], "server_time": lambda self: NOW})()
    monkeypatch.setattr(M, "client", lambda: fake)
    monkeypatch.setattr(M, "resolve", lambda ids: [{"id": 7, "webid": "w1", "path": "P", "point": "X", "unit": "kW"}])
    monkeypatch.setattr(M, "DATASETS", tmp_path)
    out = M.get_timeseries.__wrapped__(["7"], summaries=["Average", "Count"], units="MW")
    t = out["tags"][0]
    assert (t["unit"], t["summary"], t["values"], t["mean"]) == ("MW", "Average", 1, 1.0)
    assert t["other_summaries"]["Count"] == {"unit": "count", "values": 1, "mean": 60.0, "min": 60, "max": 60}
    assert out["provenance"]["column_units"] == {"7|Average": "MW", "7|Count": "count"}
    assert out["provenance"]["tags"][0]["unit_in_file"] == "MW"
    assert any("1 bad-quality" in n for n in out["notes"])
    rows = list(csv.DictReader(open(out["file"])))
    assert [r["7|Average"] for r in rows] == ["1.0", ""] and rows[0]["7|Count"] == "60"


def test_total_and_incompatible_units(tmp_path, monkeypatch):
    item = {"WebId": "w1", "Items": [
        {"Type": "Total", "Value": {"Timestamp": "2026-11-20T00:00:00Z", "Value": 18.6, "Good": True}}]}
    fake = type("C", (), {"streamset": lambda self, *a, **k: [item], "server_time": lambda self: NOW})()
    monkeypatch.setattr(M, "client", lambda: fake)
    monkeypatch.setattr(M, "resolve", lambda ids: [{"id": 7, "webid": "w1", "path": "P", "point": "X", "unit": "kWh"}])
    monkeypatch.setattr(M, "DATASETS", tmp_path)
    out = M.get_timeseries.__wrapped__(["7"], summaries=["Total"], units="MW")
    assert out["tags"][0]["unit"] == "kWh x days" and out["tags"][0]["mean"] == 18.6      # not scaled, not called MW
    assert any("cannot convert kWh to MW" in n for n in out["notes"])


def test_calls_per_minute(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "AUDIT", tmp_path / "audit.jsonl")
    monkeypatch.setattr(M, "CALLS", [])
    monkeypatch.setitem(M.L, "calls_per_minute", 2)
    monkeypatch.setattr(M, "resolve", lambda ids: (_ for _ in ()).throw(ValueError("stop here")))
    outs = [M.get_current_values(ids=["1"]) for _ in range(3)]
    assert [("Too many calls" in o["error"]) for o in outs] == [False, False, True]


def test_oversized_reads_never_reach_the_historian(monkeypatch):
    calls = []
    fake = type("C", (), {"streamset": lambda self, *a, **k: calls.append(k) or [], "get": lambda self, *a, **k: calls.append(a) or {},
                          "server_time": lambda self: NOW})()
    monkeypatch.setattr(M, "client", lambda: fake)
    monkeypatch.setattr(M, "resolve", lambda ids: [{"id": 7, "webid": "w1", "path": "P", "point": "X", "unit": "kW"}])
    read = M.get_timeseries.__wrapped__
    for kwargs, said in [
        (dict(start="2016-01-01", end="2026-01-01", mode="summary", interval="1s"), "over the limit"),     # ten years of seconds
        (dict(start="2016-01-01", end="2026-01-01", mode="interpolated", interval="1m"), "over the limit"),
        (dict(start="*-10y", end="*", mode="recorded"), "at most 7 days"),                                  # recorded_days was unused
        (dict(start="*", end="*-1d"), "ends before it starts"),
        (dict(start="last tuesday", end="*"), "Cannot read the time"),
        (dict(start="*-1d", end="*", interval="hourly"), "Cannot read the interval"),
        (dict(start="*-1d", end="*", mode="raw"), "mode must be"),
    ]:
        try:
            read(["7"], **kwargs)
            raise AssertionError(f"{kwargs} was let through")
        except ValueError as e:
            assert said in str(e), (kwargs, str(e))
    assert calls == []                                    # nothing was asked of the historian
    read(["7"], start="*-7d", end="*", mode="recorded")   # the limit itself is allowed
    assert len(calls) == 1


def test_staleness_is_measured_on_the_servers_clock():
    week_old = {"Value": {"Timestamp": "2026-11-16T00:00:00Z", "Value": 1.0, "Good": True}}
    # the old rule took the newest sample as "now": with every tag stopped a week ago, each looked fresh
    assert crawler.health_of(week_old, 24 * 3600, crawler.iso_to_epoch("2026-11-16T00:00:00Z"))["health"] == "ok"
    assert crawler.health_of(week_old, 24 * 3600, crawler.iso_to_epoch("2026-11-23T00:00:00Z"))["health"] == "stale"
    c = connector.Client("http://x/piwebapi", "none", None, None)
    assert c.server_time() is None
    c.clock = "2026-11-22T14:00:00+00:00"                 # the stand-in's X-Historian-Time
    assert c.server_time() == crawler.iso_to_epoch("2026-11-22T14:00:00Z")
    c.clock = "Sun, 22 Nov 2026 14:00:00 GMT"             # any server's Date header
    assert c.server_time() == crawler.iso_to_epoch("2026-11-22T14:00:00Z")
