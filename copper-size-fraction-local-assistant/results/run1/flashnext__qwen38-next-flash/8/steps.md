### thinking

The question: "Which size fraction carries the most copper?" Two interpretations: highest Cu grade (ppm) → CTS+106 at 2250 ppm. But "carries the most copper" in terms of mass contribution (grade × mass%) → weighted. Let's compute.

CTS+106: 8.6% × 2250 = 19,350
CTS+75: 7.7 × 1864 = 14,353
CTS+53: 10.1 × 1265 = 12,777
CTS+C1: 13.1 × 1390 = 18,209
CTS+C3: 13.8 × 775 = 10,695
CTS+C5: 5.2 × 860 = 4,472
CTS-C5: 33.3 × 1084 = 36,097

So CTS-C5 (the -5 µm slime fraction) carries the most copper by mass — about 38% of total Cu, despite modest grade of 1084 ppm.

Let me run Python to verify.

Also compute mass-weighted average grade: sum/100 = 11,595... let's compute: 19,350+14,353+12,777+18,209+10,695+4,472+36,097 = 115,953; /100 = 1159.5 ppm.

Let me run.

### bash

```
cd /tmp && cat > cu.py <<'EOF'
frac = {
 "CTS+106": (8.6, 2250),
 "CTS+75":  (7.7, 1864),
 "CTS+53":  (10.1, 1265),
 "CTS+C1":  (13.1, 1390),
 "CTS+C3":  (13.8, 775),
 "CTS+C5":  (5.2, 860),
 "CTS-C5":  (33.3, 1084),
}
tot_w = sum(m for m,_ in frac.values())
tot_cu = sum(m*c for m,c in frac.values())
print("mass% sum =", tot_w, " total Cu (ppm*fraction) =", tot_cu)
print("mass-weighted head grade = %.0f ppm" % (tot_cu/tot_w))
print(f"{'frac':9} {'mass%':>6} {'Cu ppm':>7} {'Cu share%':>10} {'Cu units':>9}")
rows=[]
for f,(m,c) in frac.items():
    u=m*c; rows.append((f,m,c,u,100*u/tot_cu))
for f,m,c,u,s in rows:
    print(f"{f:9} {m:6.1f} {c:7d} {s:10.1f} {u:9.0f}")
print()
print("highest grade :", max(rows,key=lambda r:r[2])[0])
print("largest Cu mass carry :", max(rows,key=lambda r:r[3])[0])
EOF
python3 cu.py
```

Result:

```
mass% sum = 91.8  total Cu (ppm*fraction) = 115952.5
mass-weighted head grade = 1263 ppm
frac       mass%  Cu ppm  Cu share%  Cu units
CTS+106      8.6    2250       16.7     19350
CTS+75       7.7    1864       12.4     14353
CTS+53      10.1    1265       11.0     12776
CTS+C1      13.1    1390       15.7     18209
CTS+C3      13.8     775        9.2     10695
CTS+C5       5.2     860        3.9      4472
CTS-C5      33.3    1084       31.1     36097

highest grade : CTS+106
largest Cu mass carry : CTS-C5
```

### thinking

Note mass% sums to 91.8 (not 100 — likely incomplete splitting/moisture loss); normalize shares by 91.8 → head grade 1263 ppm. Shares above computed on 115,952.5 which already sums the fractional masses — fine.

Let me present both answers.

### reply

## Answer

**By mass (the metal actually "carried" by each split): the −5 µm slimes, CTS‑C5.**

Recomputing the table as mass × grade (Mass% × Cu ppm):

| Fraction | Mass% | Cu ppm | Cu mass units | % of total Cu |
|---|---|---|---|---|
| CTS+106 | 8.6 | 2250 | 19,350 | 16.7 % |
| CTS+75 | 7.7 | 1864 | 14,353 | 12.4 % |
| CTS+53 | 10.1 | 1265 | 12,776 | 11.0 % |
| CTS+C1 | 13.1 | 1390 | 18,209 | 15.7 % |
| CTS+C3 | 13.8 | 775 | 10,695 | 9.2 % |
| CTS+C5 | 5.2 | 860 | 4,472 | 3.9 % |
| **CTS‑C5** | **33.3** | **1084** | **36,097** | **31.1 %** |

Mass‑weighted head grade ≈ **1,263 ppm Cu** (mass% sums to 91.8, so shares are normalised to the recovered mass).

Two senses of "most copper", worth stating explicitly:

- **Highest concentration (grade):** CTS+106 at 2,250 ppm — the coarsest fraction is the Cu‑rich one (also the highest S, 0.25 %→0.47 % trend aside, chalcopyrite liberation concentrates in the coarse +106/+75 µm splits, and Cu correlates inversely with Fe/magnetite dilution).
- **Largest share of the total copper budget:** **CTS‑C5 (−5 µm)**, which holds only ~1,084 ppm but, at 33.3 % of the tailings mass, accounts for roughly **31 % of all the copper** — more than double the coarse +106 µm split's contribution in absolute terms.

Practical implication: a grade‑led re‑processing strategy would target +106 µm, but a recovery‑led strategy cannot ignore the slimes, which lock up the single largest copper package despite being the hardest fraction to float.

