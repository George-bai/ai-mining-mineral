"""The mock's values on real hourly averages (plan.md): skipped when the backbone files are not there.
Set ZYFRA_CSV to the source file to also check recovery against the source's own recovery column."""
import csv, os, sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("MOCK_SITES", "4")
import mock_api, values as V  # noqa: E402

pytestmark = pytest.mark.skipif(not V.backbones(), reason="no backbone files in local/backbones")
A1 = "\\\\EXAMPLE-AF\\Operations\\Example Mining\\Site A\\Concentrator 1"


def tag(path):
    return mock_api.stream_tag(mock_api.webid("F1Ab", path))


def hour_means(tg, hours):
    lag = 60 * (V.rule_of(tg) or {}).get("lag_min", 0)
    t = V.NOW + hours[:, None] * 3600 + V.SCAN * np.arange(720)[None, :] + lag
    return np.nanmean(V.scans(tg, t.ravel()).reshape(t.shape), axis=1)


def test_hour_means_equal_the_source_and_no_new_negatives():
    H = np.arange(-300, 0)
    for a in mock_api.P["attributes"]:
        if a["point"] not in mock_api.POINTS:
            continue
        tg = tag(a["path"])
        if not V.rule_of(tg):
            continue
        conv = V.CONVERT.get((V.KINDS[tg["kind"]][0], tg["unit"]), 1)
        src = conv * V.hourly(tg, H)
        ok = ~np.isnan(src)
        with np.errstate(all="ignore"):
            got = hour_means(tg, H)
        assert np.allclose(got[ok], src[ok], rtol=1e-9, atol=1e-9), a["path"]
        if not (src[ok] < 0).any():
            t = V.NOW + H[ok][:, None] * 3600 + V.SCAN * np.arange(0, 720, 7)[None, :]
            assert not (V.scans(tg, t.ravel()) < 0).any(), a["path"]


def test_recovery_from_the_assay_tags_equals_the_source():
    src = os.environ.get("ZYFRA_CSV")
    if not src:
        pytest.skip("set ZYFRA_CSV to check against the source's recovery column")
    with open(src) as f:
        rows = list(csv.DictReader(f))
    n, H = len(rows), np.arange(-500, 0)
    F = hour_means(tag(A1 + "\\Flotation\\Rougher Feed|Au"), H)
    C = hour_means(tag(A1 + "\\Flotation\\Final Concentrate|Au"), H)
    T = hour_means(tag(A1 + "\\Flotation\\Final Tail|Au"), H)
    rec = 100 * C * (F - T) / (F * (C - T))
    want = np.array([float(rows[n + h]["final.output.recovery"] or "nan") for h in H])
    ok = ~np.isnan(rec) & ~np.isnan(want) & (want > 0)
    assert ok.sum() > 400
    assert np.allclose(rec[ok], want[ok], atol=1e-6)


def test_no_recovery_tag_anywhere():
    assert not any("recover" in a["path"].lower() for a in mock_api.P["attributes"])
    assert not any("recover" in (p["descriptor"] or "").lower() for p in mock_api.POINTS.values())


def test_dose_recovery_slope_low_above_high_survives_daily_averages():
    """No. 4's pattern, read the way an agent can within the tool caps: daily averages over the whole span."""
    days, start = 940, V.NOW - 940 * 86400

    def daily(p):
        t = tag(A1 + p)
        out = [mock_api.summary_json(t, start + i * 86400, start + (i + 1) * 86400, ["Average"], None)[0]["Value"]["Value"]
               for i in range(days)]
        return np.array([x if isinstance(x, (int, float)) else np.nan for x in out])

    F, C, T = (daily(f"\\Flotation\\{s}|Au") for s in ("Rougher Feed", "Rougher Concentrate", "Rougher Tail"))
    X = daily("\\Flotation\\Collector|Dose Rate")
    with np.errstate(all="ignore"):
        R = 100 * C * (F - T) / (F * (C - T))
    ok = ~np.isnan(R + X + F) & (R > 40) & (R <= 100) & (F > 0.5)
    F, R, X = F[ok], R[ok], X[ok]
    band = np.digitize(F, np.quantile(F, [1 / 3, 2 / 3]))
    slopes = [np.polyfit(X[band == b], R[band == b], 1)[0] for b in range(3)]
    assert slopes[0] > slopes[2] > 0, slopes  # low feed grade steeper than high (No. 4's brief: a two-way claim)
