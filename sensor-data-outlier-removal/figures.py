#!/usr/bin/env python3
"""Draw the article's four figures as SVG, each in a wide and a narrow (phone) layout.

Standard library only; presentation attributes only (no style blocks), so the files pass a strict
content security policy when placed inline in a page.
Run:  python3 figures.py <dataset folder> <output folder>
"""
import sys
from pathlib import Path
import demo

INK, MUTED, GRID, PAPER = "#1A1816", "#55504A", "#E6E1D9", "#FAF9F7"
RUST, GREY, BAND = "#B84F33", "#8F8981", "#EFE7DA"
FONT = "'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
num = lambda v: f"{v:,.0f}".replace("-", "−")


class Fig:
    def __init__(self, w, h, title, desc):
        self.w, self.h = w, h
        self.out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
                    f'font-family="{FONT}" font-size="13" fill="{INK}"><title>{title}</title><desc>{desc}</desc>']
        self.clips = 0

    def text(self, x, y, s, anchor="start", fill=INK, size=13, weight=400):
        self.out.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="{fill}" font-size="{size}" font-weight="{weight}">{s}</text>')

    def line(self, x1, y1, x2, y2, stroke=GRID, width=1, cap="butt"):
        self.out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="{cap}"/>')

    def legend(self, x, y, items, stacked=False):
        """items: (kind, colour, label); kind is line, thin, swatch or tick."""
        for kind, colour, label in items:
            if kind == "swatch":
                self.out.append(f'<rect x="{x}" y="{y - 9}" width="14" height="10" rx="2" fill="{colour}"/>')
            else:
                self.line(x, y - 4, x + 14, y - 4, colour, {"line": 2.5, "thin": 1.2, "tick": 2.5}[kind], "round")
            self.text(x + 20, y, label, fill=MUTED)
            if stacked:
                y += 18
            else:
                x += 20 + 6.4 * len(label) + 22
        return y

    def save(self, path):
        Path(path).write_text("".join(self.out) + "</svg>\n")


class Panel:
    """One plotting area with linear scales."""
    def __init__(self, fig, x, y, w, h, xdom, ydom):
        self.f, self.x, self.y, self.w, self.h, self.xd, self.yd = fig, x, y, w, h, xdom, ydom
        fig.clips += 1
        self.clip = f"c{id(fig) % 10000}-{fig.clips}"
        fig.out.append(f'<clipPath id="{self.clip}"><rect x="{x}" y="{y - 1}" width="{w}" height="{h + 2}"/></clipPath>')

    def X(self, v): return self.x + (v - self.xd[0]) / (self.xd[1] - self.xd[0]) * self.w
    def Y(self, v): return self.y + self.h - (v - self.yd[0]) / (self.yd[1] - self.yd[0]) * self.h

    def axes(self, yticks, xticks, yfmt=num, xfmt=num, xlabel=None, title=None):
        f = self.f
        if title:
            f.text(self.x, self.y - 12, title, size=14, weight=600)
        for v in yticks:
            f.line(self.x, self.Y(v), self.x + self.w, self.Y(v), INK if v == 0 and self.yd[0] <= 0 else GRID)
            f.text(self.x - 8, self.Y(v) + 4, yfmt(v), "end", MUTED)
        for v in xticks:
            f.text(self.X(v), self.y + self.h + 17, xfmt(v), "middle", MUTED)
        if xlabel:
            f.text(self.x + self.w / 2, self.y + self.h + 36, xlabel, "middle", MUTED)

    def path(self, ts, xs, stroke, width=1.2, envelope=True, gaps=None):
        """A line; with envelope, each pixel column keeps only its minimum and maximum so dense records stay light."""
        pts, col, lo, hi, first = [], None, None, None, True
        d = []

        def flush():
            if col is not None:
                d.append(f'{"M" if not d or d[-1] == "" else "L"}{col:.0f},{lo:.1f}')
                if hi != lo:
                    d.append(f'L{col:.0f},{hi:.1f}')
        for i, (t, v) in enumerate(zip(ts, xs)):
            if not self.xd[0] <= t <= self.xd[1]:
                continue
            px, py = self.X(t), self.Y(v)
            if not envelope:
                d.append(f'{"M" if not d or d[-1] == "" else "L"}{px:.1f},{py:.1f}')
            else:
                c = round(px)
                if c != col:
                    flush()
                    col, lo, hi = c, py, py
                else:
                    lo, hi = (py, hi) if py > lo else (lo, hi)
                    lo, hi = max(lo, py), min(hi, py)
            if gaps is not None and not gaps[i]:
                if envelope:
                    flush(); col = None
                d.append("")                       # break the line: the stretch to the next record is missing
        if envelope:
            flush()
        self.f.out.append(f'<path d="{" ".join(p for p in d if p)}" fill="none" stroke="{stroke}" stroke-width="{width}" '
                          f'stroke-linejoin="round" stroke-linecap="round" clip-path="url(#{self.clip})"/>')

    def dots(self, ts, xs, fill, r=3):
        for t, v in zip(ts, xs):
            if self.xd[0] <= t <= self.xd[1] and self.yd[0] <= v <= self.yd[1]:
                self.f.out.append(f'<circle cx="{self.X(t):.1f}" cy="{self.Y(v):.1f}" r="{r}" fill="{fill}" stroke="{PAPER}" stroke-width="1.5"/>')


def hours(ts): return [t / 3600 for t in ts]
compact = lambda v: "0" if v == 0 else f"{v / 1e6:g}M" if v >= 1e6 else f"{v / 1e3:g}K"


def fig1(d, narrow):
    w = 360 if narrow else 720
    L, R, ph = 46, 12, 150 if narrow else 170
    f = Fig(w, 2 * ph + 190, "Feed rate over one shift, raw and after a hard limit",
            "Top: raw records, flattened by five spikes of up to 1,000,000 t/h. Bottom: the same shift after removing records "
            "above 1,500 t/h, moving between about 850 and 1,120 t/h and following the real hourly averages.")
    xt = [0, 3, 6, 9, 12] if narrow else list(range(0, 13, 2))
    a = Panel(f, L, 34, w - L - R, ph, (0, 12), (0, 1_050_000))
    a.axes([0, 250_000, 500_000, 750_000, 1_000_000], xt, yfmt=compact, title="Raw records (t/h)")
    a.path(d["h"], d["read"], RUST, 1.4)
    sx, sv = max(zip(d["h"], d["read"]), key=lambda p: p[1])
    f.text(a.X(sx) - 8, a.Y(sv) + 12, "1,000,000 t/h", "end", MUTED)
    f.text(a.X(0.3), a.Y(0) - 8, "The real feed rate is in this line", fill=MUTED)
    top = 34 + ph + 78
    b = Panel(f, L, top, w - L - R, ph, (0, 12), (850, 1150))
    b.axes([900, 1000, 1100], xt, xlabel="Hours into the shift", title="After the hard upper limit, 1,500 t/h")
    f.legend(L, top - 34 + (0 if not narrow else 0), [("thin", RUST, "Records kept"), ("line", INK, "Real hourly average")])
    b.axes([], [])
    b.path(d["ch"], d["cx"], RUST, 1)
    hx, hy = [], []
    for h in range(12):
        hx += [h, h + 1]; hy += [d["real"][h]] * 2
    b.path(hx, hy, INK, 2.2, envelope=False)
    return f


def fig2(d, narrow):
    w = 360 if narrow else 720
    L, R, ph = 46, 12, 200 if narrow else 230
    f = Fig(w, ph + 150 + (36 if narrow else 0), "Hourly averages of the same shift, from raw records",
            "Twelve hourly averages. Nine match the true average. The hour with one spike reads 1,187 t/h against a true 1,050, "
            "inside the 1,500 t/h span. The hours with three spikes and one large spike read 3,266 and 1,946 t/h.")
    f.text(L, 22, "Hourly average from raw records (t/h)", size=14, weight=600)
    ly = f.legend(L, 44, [("swatch", GREY, "No spike in the hour"), ("swatch", RUST, "Hour holds a spike"), ("tick", INK, "True average")],
                  stacked=narrow)
    top = (ly if narrow else 44) + 22
    p = Panel(f, L, top, w - L - R, ph, (0, 12), (0, 3500))
    p.axes([0, 1000, 2000, 3000], [])
    f.line(L, p.Y(1500), w - R, p.Y(1500), MUTED, 1)
    f.text(w - R, p.Y(1500) - 6, "Instrument span, 1,500", "end", MUTED)
    bw = 14 if narrow else 24
    for h in d["hourly"][:12]:
        cx, y = p.X(h["hour"] + 0.5), p.Y(h["raw"])
        colour = RUST if h["spikes"] else GREY
        f.out.append(f'<path d="M{cx - bw / 2:.1f},{p.Y(0):.1f} V{y + 4:.1f} q0,-4 4,-4 h{bw - 8} q4,0 4,4 V{p.Y(0):.1f} Z" fill="{colour}"/>')
        ty = p.Y(h["true"])
        f.line(cx - bw / 2 - 3, ty, cx + bw / 2 + 3, ty, PAPER, 5)
        f.line(cx - bw / 2 - 3, ty, cx + bw / 2 + 3, ty, INK, 2.5)
        if h["spikes"]:
            f.text(cx, y - 7, num(h["raw"]), "middle", size=13, weight=600)
        f.text(cx, p.y + p.h + 17, str(h["hour"] + 1), "middle", MUTED)
    f.text(L + p.w / 2, p.y + p.h + 36, "Hour of the shift", "middle", MUTED)
    return f


def fig3(d, narrow):
    w = 360 if narrow else 720
    L, R, ph = 46, 12, 150
    pw = w - L - R if narrow else (w - 2 * L - R - 24) / 2
    f = Fig(w, (2 * ph + 190) if narrow else ph + 120, "Two kinds of negative reading",
            "Left: for one hour on an empty running belt the tag reads about minus 8 t/h; the repair sets it to zero. "
            "Right: a failed transmitter reads minus 37.5 t/h for 15 minutes; those records are removed and the stretch is left missing.")
    f.legend(L, 16, [("line", GREY, "Raw records"), ("line", RUST, "After cleaning")])
    hm = lambda v: f"{int(v)}:{round((v % 1) * 60):02d}"
    a = Panel(f, L, 58, pw, ph, (57.75, 59.25), (-20, 40))
    a.axes([-20, 0, 20, 40], [58, 58.5, 59], xfmt=hm, title="Zero drift on an empty belt (t/h)")
    a.path(d["h"], d["read"], GREY, 2, envelope=False)
    a.dots(d["h"], d["read"], GREY)
    a.path(d["ch"], d["cx"], RUST, 2, envelope=False)
    f.text(a.X(58.5), a.Y(-8) + 20, "Reads about −8", "middle", MUTED)
    f.text(a.X(58.5), a.Y(0) - 8, "Repaired to 0", "middle", MUTED)
    bx, by = (L, 58 + ph + 82) if narrow else (L + pw + 24 + L, 58)
    b = Panel(f, bx, by, pw, ph, (63.75, 64.5), (-100, 1100))
    b.axes([0, 500, 1000], [64, 64.25, 64.5], xfmt=hm, xlabel=None, title="Failed transmitter (t/h)")
    b.path(d["h"], d["read"], GREY, 2, envelope=False)
    b.path(d["ch"], d["cx"], RUST, 2, envelope=False, gaps=d["ck"])
    f.text(b.X(64.125), b.Y(0) - 10, "Reads −37.5 for 15 min", "middle", MUTED)
    f.text(b.X(64.125), b.Y(1000) + 4, "Left missing", "middle", MUTED)
    f.text(w / 2 if not narrow else L + pw / 2, by + ph + 38, "Hours and minutes into the four days", "middle", MUTED)
    return f


def fig4(d, narrow):
    w = 360 if narrow else 720
    L, R, ph = 46, 12, 210 if narrow else 240
    lo, hi = d["thr"]["1.5 x IQR after hard limit"]
    s_lo, s_hi = d["thr"]["3-sigma after hard limit"]
    lift = 16 if narrow else 0                    # phone: labels on two rows, so 13 px text does not overlap
    f = Fig(w, ph + 176 + lift, "Four days of cleaned feed rate, with what two statistical rules would keep",
            f"The box-plot rule keeps only {num(lo)} to {num(hi)} t/h, so it flags the surge, the trip, the shutdown, the empty belt and "
            f"a real low-feed hour. Three-sigma limits of {num(s_lo)} and {num(s_hi)} t/h flag the stops and almost none of the surge.")
    f.text(L, 22, "Cleaned records over four days (t/h)", size=14, weight=600)
    ly = f.legend(L, 44, [("thin", RUST, "Cleaned records"), ("swatch", BAND, f"Box-plot rule keeps {num(lo)} to {num(hi)}"),
                          ("line", INK, f"3-sigma limits, {num(s_lo)} and {num(s_hi)}")], stacked=True)
    top = ly + 26 + lift
    p = Panel(f, L, top, w - L - R, ph, (0, 96), (0, 1400))
    f.out.append(f'<rect x="{L}" y="{p.Y(hi):.1f}" width="{p.w}" height="{p.Y(lo) - p.Y(hi):.1f}" fill="{BAND}"/>')
    p.axes([0, 500, 1000], [0, 24, 48, 72, 96], xlabel="Hours")
    for v in (s_lo, s_hi):
        f.line(L, p.Y(v), L + p.w, p.Y(v), INK, 1.2)
    p.path(d["ch"], d["cx"], RUST, 1.1, gaps=d["ck"])
    for hr, label, up in ((20.25, "Surge", 1), (30.5, "Trip", 0), (43.5, "Shutdown", 1), (58.5, "Empty belt", 0), (8.5, "Low hour", 0)):
        dy = lift if up else 0
        f.text(p.X(hr), top - 6 - dy, label if not narrow or label != "Empty belt" else "Empty", "middle", MUTED)
        f.line(p.X(hr), top - 2 - dy, p.X(hr), top + 6, MUTED, 1)
    return f


def main(data, out):
    out.mkdir(parents=True, exist_ok=True)
    t, true, read, run, events = demo.load(data / "traces" / "seed1-base.csv")
    res, cleaned, _ = demo.analyse(t, true, read, run, events)
    ct, cx, ck = zip(*cleaned)
    import csv
    d = {"h": hours(t), "read": read, "ch": hours(ct), "cx": cx, "ck": ck, "hourly": res["hourly"], "thr": res["thresholds"],
         "real": [float(r["real_hourly_average_tph"]) for r in csv.DictReader(open(data / "hourly-real.csv"))]}
    for n, fig in enumerate((fig1, fig2, fig3, fig4), 1):
        for narrow in (False, True):
            fig(d, narrow).save(out / f"fig{n}-{'narrow' if narrow else 'wide'}.svg")
    print(f"wrote 8 figures to {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
