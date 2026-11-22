### thinking

The question: "Which size fraction carries the most copper?" Ambiguous: highest grade (concentration) vs. most total copper mass (grade × mass%). The trick: CTS+106 has the highest Cu grade (2250 ppm) but only 8.6% mass; CTS-C5 has 1084 ppm but 33.3% mass → carries the most copper overall. Let me compute.

Let me run Python.

### bash

```
cd /tmp && cat > cu.py <<'EOF'
data = [
 ("CTS+106",  8.6, 2250),
 ("CTS+75",   7.7, 1864),
 ("CTS+53",  10.1, 1265),
 ("CTS+C1",  13.1, 1390),
 ("CTS+C3",  13.8,  775),
 ("CTS+C5",   5.2,  860),
 ("CTS-C5",  33.3, 1084),
]
tot_mass = sum(m for _,m,_ in data)
tot_cu   = sum(m*c for _,m,c in data)
print("mass% sum:", tot_mass, " weighted-mean Cu grade (ppm):", tot_cu/tot_mass)
print(f"{'fraction':9} {'mass%':>6} {'Cu ppm':>7} {'rel mass Cu':>12} {'% of total Cu':>14} {'Cu index (m*c)':>15}")
for n,m,c in sorted(data, key=lambda r: -(r[1]*r[2])):
    print(f"{n:9} {m:6.1f} {c:7.0f} {m*c/ (data[0][1]*data[0][2]):12.2f} {100*m*c/tot_cu:14.1f} {m*c:15.0f}")
print()
print("highest grade :", max(data, key=lambda r: r[2])[0])
print("largest Cu mass carry:", max(data, key=lambda r: r[1]*r[2])[0])
# coarse vs fines sanity
EOF
python3 cu.py
```

Result:

```
mass% sum: 91.8  weighted-mean Cu grade (ppm): 1263.099128540305
fraction   mass%  Cu ppm  rel mass Cu  % of total Cu  Cu index (m*c)
CTS-C5      33.3    1084         1.87           31.1           36097
CTS+106      8.6    2250         1.00           16.7           19350
CTS+C1      13.1    1390         0.94           15.7           18209
CTS+75       7.7    1864         0.74           12.4           14353
CTS+53      10.1    1265         0.66           11.0           12776
CTS+C3      13.8     775         0.55            9.2           10695
CTS+C5       5.2     860         0.23            3.9            4472

highest grade : CTS+106
largest Cu mass carry: CTS-C5
```

### thinking

Note mass% sums to 91.8 (not 100) — presumably some mass loss in splitting; normalizing doesn't change ranking.

Give answer: it depends — highest grade is CTS+106 (+106 µm), but the -C5 (fines) fraction carries most of the copper because it's 33% of the mass.

### reply

## Answer

**It depends on what "carries" means — and the two answers differ:**

| Fraction | Mass % | Cu (ppm) | Share of total Cu |
|---|---|---|---|
| **CTS‑C5** | 33.3 | 1084 | **31.1 %** ← most copper overall |
| CTS+106 | 8.6 | 2250 | 16.7 % ← highest grade |
| CTS+C1 | 13.1 | 1390 | 15.7 % |
| CTS+75 | 7.7 | 1864 | 12.4 % |
| CTS+53 | 10.1 | 1265 | 11.0 % |
| CTS+C3 | 13.8 | 775 | 9.2 % |
| CTS+C5 | 5.2 | 860 | 3.9 % |

Weighted‑mean head grade ≈ **1263 ppm Cu** (mass% sums to 91.8, so this is on the normalised split).

- **Highest Cu concentration:** the coarsest fraction, **CTS+106 µm** at 2250 ppm — chalcopyrite/Pb‑sulphide mineralisation is liberated and concentrated in the coarse grains (Co, Ag, Cu all peak there together with Fe and S).
- **Largest copper mass:** the **-C5 µm slimes, CTS‑C5** — its grade is only half the coarse fraction's, but it is a third of the whole tailings pile by mass, so it holds ~31 % of the copper, ~1.9× the coarse +106 fraction's contribution.

So: **grade‑wise the +106 µm fraction, tonnage‑wise the −5 µm (CTS‑C5) fraction**, which is the practical reason regrinding/rougher recovery of the slimes matters for any reprocessing scheme. The slimes are also the most metallurgically awkward host (highest Al, K, P, Th, U, Y/REE and Zn — i.e. clay‑ and oxy‑salt‑rich), so the largest copper pool sits in the fraction that is hardest to float.

