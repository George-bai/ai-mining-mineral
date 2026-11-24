"""get_timeseries keeps each summary column apart, never converts Count, and leaves bad-quality values out
(found by the external review of 24 Nov 2026: Count and a bad value had been averaged into a tag's mean)."""
import csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import mcp_server as M  # noqa: E402


def test_summaries_kept_apart(tmp_path, monkeypatch):
    item = {"WebId": "w1", "Items": [
        {"Type": "Average", "Value": {"Timestamp": "2026-11-20T00:00:00Z", "Value": 1000.0, "Good": True}},
        {"Type": "Count", "Value": {"Timestamp": "2026-11-20T00:00:00Z", "Value": 60, "Good": True}},
        {"Type": "Average", "Value": {"Timestamp": "2026-11-20T01:00:00Z", "Value": 99999.0, "Good": False}}]}
    fake = type("C", (), {"streamset": lambda self, *a, **k: [item]})()
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
    fake = type("C", (), {"streamset": lambda self, *a, **k: [item]})()
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
