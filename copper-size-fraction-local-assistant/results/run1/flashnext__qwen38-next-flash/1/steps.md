### thinking

The question: "Which size fraction carries the most copper?" Ambiguity: highest grade (concentration) vs. most copper mass (grade × mass%). The coarse +106 has highest Cu grade (2250 ppm), but the -C5 fraction (33.3 mass%) at 1084 ppm carries the most Cu mass. Let's compute.

Let me run Python.

### bash

```
cat << 'EOF' > /tmp/cu.py
fr = [
 ("CTS+106", 8.6, 2250),
 ("CTS+75", 7.7, 1864),
 ("CTS+53", 10.1, 1265),
 ("CTS+C1", 13.1, 1390),
 ("CTS+C3", 13.8, 775),
 ("CTS+C5", 5.2, 860),
 ("CTS-C5", 33.3, 1084),
]
tot_mass = sum(m for _,m,_ in fr)
tot_cu = sum(m*c for _,m,c in fr)
print("mass sum", tot_mass, "weighted head grade ppm", tot_cu/tot_mass)
rows = sorted(fr, key=lambda r: -(r[1]*r[2]))
print(f"{'frac':10} {'mass%':>6} {'Cu ppm':>7} {'mass*Cu':>9} {'%Cu in':>7} {'recovery':>9}")
cum=0
for f,m,c in rows:
    w=m*c
    cum+=w
    print(f"{f:10} {m:6.1f} {c:7.0f} {w:9.1f} {100*w/tot_cu:7.1f} {100*cum/tot_cu:9.1f}")
print()
print("highest grade:", max(fr, key=lambda r:r[2])[0])
print("largest Cu mass share:", rows[0][0])
EOF
python3 /tmp/cu.py
```

Result:

```
mass sum 91.8 weighted head grade ppm 1263.099128540305
frac        mass%  Cu ppm   mass*Cu  %Cu in  recovery
CTS-C5       33.3    1084   36097.2    31.1      31.1
CTS+106       8.6    2250   19350.0    16.7      47.8
CTS+C1       13.1    1390   18209.0    15.7      63.5
CTS+75        7.7    1864   14352.8    12.4      75.9
CTS+53       10.1    1265   12776.5    11.0      86.9
CTS+C3       13.8     775   10695.0     9.2      96.1
CTS+C5        5.2     860    4472.0     3.9     100.0

highest grade: CTS+106
largest Cu mass share: CTS-C5
```

### thinking

Note mass% sums to 91.8, not 100 — likely rounding/missing fractions. Normalize anyway. Let me also note normalized shares (they're the same relative). Answer: depends on interpretation.

Also worth noting: Cu grade peaks in coarsest +106 µm fraction (coarse chalcopyrite/pyrite-rich), but the fines -C5 (33.3% of mass) hold the biggest slice of the copper budget (~31%).

Let me compute with normalized mass (dividing by 91.8) — same percentages. Good.

Give final answer.

### reply

## Answer

It depends on what "carries" means — the table supports two different answers:

**Highest copper *grade*: CTS+106 µm** (the coarsest fraction) at **2,250 ppm Cu** — Cu grade falls monotonically-ish with decreasing size (2250 → 1864 → 1265 → 1390 → 775 → 860 → 1084 ppm).

**Largest share of the total copper *budget*: CTS‑C5 µm** (the <5 µm slimes), simply because it is by far the biggest size class at 33.3 mass%.

Computed mass budget (mass% × ppm; the listed mass% sum to 91.8, so shares are normalised):

| Fraction | Mass% | Cu ppm | mass×Cu | % of total Cu | cum. |
|---|---|---|---|---|---|
| CTS‑C5 | 33.3 | 1084 | 36,097 | **31.1 %** | 31.1 % |
| CTS+106 | 8.6 | 2250 | 19,350 | 16.7 % | 47.8 % |
| CTS+C1 | 13.1 | 1390 | 18,209 | 15.7 % | 63.5 % |
| CTS+75 | 7.7 | 1864 | 14,353 | 12.4 % | 75.9 % |
| CTS+53 | 10.1 | 1265 | 12,777 | 11.0 % | 86.9 % |
| CTS+C3 | 13.8 | 775 | 10,695 | 9.2 % | 96.1 % |
| CTS+C5 | 5.2 | 860 | 4,472 | 3.9 % | 100 % |

Mass‑weighted head grade of the whole tailings: **~1,263 ppm Cu**.

**Bottom line:** copper is *enriched* in the coarsest fraction (CTS+106, 2,250 ppm ≈ 1.8× the head grade), but because the ultrafines (CTS‑C5) make up a third of the tailings mass, that slimes fraction holds the single largest slice of the contained copper (~31%), and the two together (coarsest + finest) account for ~48% of the copper while being only 42% of the mass. Notably, the Cu distribution is bimodal and does *not* follow Fe (which peaks in CTS+C1), so the copper is not simply riding on the magnetite‑rich coarse‑mid fraction.

