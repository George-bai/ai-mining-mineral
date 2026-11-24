"""The prototype end to end, in-process: mock contract, read-only connector, crawl counts, search, MCP tools."""
import base64, json, os, sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("MOCK_SITES", "4")
import catalog, connector, crawler, generator, mock_api  # noqa: E402

AUTH = {"authorization": "Basic " + base64.b64encode(b"demo:demo-password").decode()}


@pytest.fixture(scope="module")
def http():
    return TestClient(mock_api.app)


@pytest.fixture(scope="module")
def built(tmp_path_factory, http):
    c = connector.Client("http://testserver/piwebapi", "basic", "demo", "demo-password")
    c.http = http
    out = tmp_path_factory.mktemp("cat")
    return crawler.run(c, mock_api.DB_PATH, out), catalog.connect(out / "catalog.sqlite")


def test_mock_contract(http):
    assert http.get("/piwebapi").status_code == 401
    db = http.get("/piwebapi/assetdatabases", params={"path": mock_api.DB_PATH}, headers=AUTH).json()
    page = http.get(f"/piwebapi/assetdatabases/{db['WebId']}/elements",
                    params={"searchFullHierarchy": "true", "maxCount": 10, "startIndex": 5,
                            "selectedFields": "Items.Name;Items.Path"}, headers=AUTH).json()
    assert len(page["Items"]) == 10 and set(page["Items"][0]) == {"Name", "Path"}
    assert http.delete("/piwebapi/points/x", headers=AUTH).status_code == 405
    assert http.post("/piwebapi/batch", json={"a": {"Method": "PUT", "Resource": "x"}}, headers=AUTH).status_code == 400


def test_connector_read_only():
    c = connector.Client("http://127.0.0.1:1/piwebapi", auth="none", retries=0)
    with pytest.raises(connector.ReadOnlyError):
        c._send("POST", "/points")
    with pytest.raises(connector.ReadOnlyError):
        c.batch({"a": {"Method": "DELETE", "Resource": "x"}})


def test_connector_retries(http, monkeypatch):
    monkeypatch.setenv("MOCK_FAULT_RATE", "0.5")
    c = connector.Client("http://testserver/piwebapi", "basic", "demo", "demo-password", retries=8)
    c.http = http
    monkeypatch.setattr(connector.time, "sleep", lambda s: None)
    assert c.get("")["Links"]


def expected_health() -> dict:
    """Each catalogue tag's health as the mock makes it: the injected faults, plus tags whose real source has no
    value in the last day (a blank in the backbone at the mock's now)."""
    out = {}
    for a in mock_api.P["attributes"]:
        if a["broken"]:
            out[a["path"]] = "broken_ref"
            continue
        out[a["path"]] = health_of_point(a["point"])
    linked = {a["point"] for a in mock_api.P["attributes"]}
    for name, p in mock_api.POINTS.items():
        if name not in linked:
            out[name] = health_of_point(name)
    return out


def health_of_point(name: str) -> str:
    p = mock_api.POINTS[name]
    if p["health"] in ("no_data", "bad_quality", "stale"):
        return p["health"]
    lg = mock_api.last_good(mock_api.stream_tag(mock_api.webid("F1DP", name)))
    if lg is None:
        return "no_data"
    return "stale" if mock_api.values.now() - lg > 24 * 3600 else "ok"


def test_crawl_matches_generator(built):
    """Every injected fault and variant is found, and every tag the real source leaves without data: none more,
    none fewer."""
    report, _ = built
    truth = generator.counts(generator.build(4, 1))
    assert report["tags"] == truth["tags"] and report["unlinked_points"] == truth["unlinked_points"]
    expected = expected_health()
    for h in ("broken_ref", "stale", "no_data", "bad_quality"):
        n = sum(v == h for v in expected.values())
        assert report["by_health"].get(h, 0) == n, h
        assert n >= truth[h], h  # the injected ones are among them
    assert report["by_variant"]["qc"] == truth["variants_qc"]
    assert report["by_variant"]["calc"] == truth["variants_calc"]
    assert report["by_variant"]["alarm"] == truth["alarm_points"]


def test_search(built):
    _, con = built
    top = catalog.search(con, "SAG mill power at Site A")[0]
    assert top["path"].endswith("Site A\\Concentrator 1\\Grinding\\SAG Mill|Motor Power")
    assert catalog.search(con, "sbc1_bm2_pwr")[0]["point"] == "SBC1_BM2_PWR"
    assert catalog.find_assets(con, "Site A Plant 1")[0]["path"].endswith("Site A\\Concentrator 1")
    # nothing about recovery anywhere in the catalogue (series.md: No. 5 tests this)
    assert con.execute("SELECT count(*) FROM tags WHERE search_text LIKE '%recover%'").fetchone()[0] == 0
