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
    assert t["other_summaries"]["Count"]["mean"] == 60
    assert out["provenance"]["tags"][0]["unit_in_file"] == "MW"
    assert any("1 bad-quality" in n for n in out["notes"])
    rows = list(csv.DictReader(open(out["file"])))
    assert [r["7|Average"] for r in rows] == ["1.0", ""] and rows[0]["7|Count"] == "60"
