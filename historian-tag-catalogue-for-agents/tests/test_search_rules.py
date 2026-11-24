"""Round 2 fixes to the search rules, one test per class of defect (development.md, 23 Nov 2026)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import catalog  # noqa: E402


def test_concentrator_abbreviations():
    for text in ("con 2", "con2", "con. 2", "Concentrator 2", "conc 2", "plant 2"):
        assert catalog.parse_location(f"SAG power at site D {text}") == {"site": "Site D", "concentrator": "Concentrator 2"}, text


def test_word_forms_reach_their_rules():
    assert "draw" in catalog.forms("drawing") and "dose" in catalog.forms("dosing")
    assert catalog.forms("gold") == ["gold"]


def test_search_uses_them(tmp_path):
    # built from the 4-site mock in test_system's fixture would be slow to share; build a 1-site catalogue here
    import os
    os.environ.setdefault("MOCK_SITES", "4")
    from fastapi.testclient import TestClient
    import connector, crawler, mock_api
    c = connector.Client("http://testserver/piwebapi", "basic", "demo", "demo-password")
    c.http = TestClient(mock_api.app)
    crawler.run(c, mock_api.DB_PATH, tmp_path)
    con = catalog.connect(tmp_path / "catalog.sqlite")
    top = catalog.search(con, "What frother dosage are we running at Site B con 1?")[0]
    assert top["path"].endswith("Site B\\Concentrator 1\\Flotation\\Frother|Dose Rate"), top["path"]
    top = catalog.search(con, "What's the SAG drawing at Site C con 1, in megawatts?")[0]
    assert top["path"].endswith("Site C\\Concentrator 1\\Grinding\\SAG Mill|Motor Power"), top["path"]
