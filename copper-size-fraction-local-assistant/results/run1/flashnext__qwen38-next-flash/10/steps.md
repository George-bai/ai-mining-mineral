### thinking

The question: "Which size fraction carries the most copper?" Two interpretations: highest Cu grade (ppm) → CTS+106 at 2250 ppm. But "carries the most copper" in terms of mass contribution (grade × mass%) — need to compute cumulative/distribution. Let's compute.

Mass% × Cu ppm → contribution to overall Cu. Let's compute.

CTS+106: 8.6 * 2250 = 19350
CTS+75: 7.7 * 1864 = 14352.8
CTS+53: 10.1*1265 = 12776.5
CTS+C1: 13.1*1390 = 18209
CTS+C3: 13.8*775 = 10695
CTS+C5: 5.2*860 = 4472
CTS-C5: 33.3*1084 = 36097.2

Sum = 19350+14352.8+12776.5+18209+10695+4472+36097.2 = 115952.5. Check mass sum: 8.6+7.7+10.1+13.1+13.8+5.2+33.3 = 91.8. Hmm, mass% sums to 91.8, not 100. So there may be missing fractions or losses. Normalize anyway.

So CTS-C5 (the -5 µm? slime fraction) carries the most copper by mass (~31%), despite mid-grade, because it's 33% of the mass. Highest grade is CTS+106.

Also could compute the head grade: 115952.5/91.8 ≈ 1263 ppm (if normalized to 100 mass, grade would be 1263 ppm).

Let me run Python to compute quickly, and also produce distribution percentages.

Also note CTS+106 highest grade but only 8.6% mass → 16.7% of Cu.

Let me do the computation.

### bash

```
cd /tmp && cat > cu.py <<'EOF'
mass = {"CTS+106":8.6,"CTS+75":7.7,"CTS+53":10.1,"CTS+C1":13.1,"CTS+C3":13.8,"CTS+C5":5.2,"CTS-C5":33.3}
cu   = {"CTS+106":2250,"CTS+75":1864,"CTS+53":1265,"CTS+C1":1390,"CTS+C3":775,"CTS+C5":860,"CTS-C5":1084}

tm = sum(mass.values())
tot = sum(mass[f]*cu[f] for f in mass)          # Mass% * ppm  -> ppm*mass% units
print("mass%% sums to %.1f" % tm)
print("head grade (mass-weighted, normalised to 100%%): %.0f ppm Cu" % (tot/tm))
print()
rows=[]
for f in mass:
    contrib = mass[f]*cu[f]
    rows.append((f, mass[f], cu[f], contrib, 100*contrib/tot))
rows.sort(key=lambda r:-r[4])
print(f"{'frac':9}{'mass%':>7}{'Cu ppm':>8}{'Cu mass units':>15}{'% Cu carried':>14}{'cum %':>8}")
cum=0
for f,m,g,c,p in rows:
    cum+=p
    print(f"{f:9}{m:7.1f}{g:8d}{c:15.1f}{p:14.1f}{cum:8.1f}")
print()
print("highest grade   :", max(cu, key=cu.get), max(cu.values()), "ppm")
print("most Cu by mass :", rows[0][0])
# coarse vs fines check
coarse=[f for f in mass if f.startswith("CTS+")]
print("coarse (+53/+75/+106) share of Cu: %.1f%%  (mass %.1f%%)" % (
    sum(mass[f]*cu[f] for f in coarse)/tot*100, sum(mass[f] for f in coarse)))
print("-5 fraction alone: %.1f%% of Cu from %.1f%% of mass" % (
    mass["CTS-C5"]*cu["CTS-C5"]/tot*100, mass["CTS-C5"]))
EOF
python3 cu.py
```

Result:

```
mass% sums to 91.8
head grade (mass-weighted, normalised to 100%): 1263 ppm Cu

frac       mass%  Cu ppm  Cu mass units  % Cu carried   cum %
CTS-C5      33.3    1084        36097.2          31.1    31.1
CTS+106      8.6    2250        19350.0          16.7    47.8
CTS+C1      13.1    1390        18209.0          15.7    63.5
CTS+75       7.7    1864        14352.8          12.4    75.9
CTS+53      10.1    1265        12776.5          11.0    86.9
CTS+C3      13.8     775        10695.0           9.2    96.1
CTS+C5       5.2     860         4472.0           3.9   100.0

highest grade   : CTS+106 2250 ppm
most Cu by mass : CTS-C5
coarse (+53/+75/+106) share of Cu: 68.9%  (mass 58.5%)
-5 fraction alone: 31.1% of Cu from 33.3% of mass
```

### thinking

Give answer: depends on interpretation. The "carries the most copper" — the fines CTS-C5 carries the largest share of the copper inventory (~31%), while highest grade is CTS+106. Also note the coarse fractions combined hold ~69% of Cu in 58.5% of mass.

Note mass% sums to 91.8 — mention normalization.

### reply

## Answer

**It depends on which "most" you mean — the two answers are different, and that's the interesting part of this table.**

| Fraction | Mass % | Cu ppm | Mass×Cu | % of total Cu | Cum. % |
|---|---|---|---|---|---|
| **CTS‑C5** | 33.3 | 1084 | 36,097 | **31.1 %** | 31.1 |
| **CTS+106** | 8.6 | **2250** | 19,350 | 16.7 % | 47.8 |
| CTS+C1 | 13.1 | 1390 | 18,209 | 15.7 % | 63.5 |
| CTS+75 | 7.7 | 1864 | 14,353 | 12.4 % | 75.9 |
| CTS+53 | 10.1 | 1265 | 12,777 | 11.0 % | 86.9 |
| CTS+C3 | 13.8 | 775 | 10,695 | 9.2 % | 96.1 |
| CTS+C5 | 5.2 | 860 | 4,472 | 3.9 % | 100.0 |

- **Highest copper grade:** **CTS+106** (+106 µm), 2,250 ppm Cu — the coarsest fraction is ~3× leaner‑than‑average CTS+C3.
- **Largest share of the copper inventory:** **CTS‑C5** (the ultrafine slime fraction) — it holds **~31 % of all the Cu**, purely because it is a third of the tailings by mass. Grade alone would put it mid‑pack.

Mass‑weighted head grade ≈ **1,263 ppm Cu** (fraction masses sum to 91.8 %, i.e. ~8 % unsampled/loss, so this is normalised).

Two further observations relevant to any re‑treatment plan:
- Copper is *coarse‑enriched on a bulk basis*: the three +53/+75/+106 µm fractions carry **68.9 % of the Cu from 58.5 % of the mass** (mass‑normalised grade index ~1.18), so screening out the coarse product would recover most of the metal.
- CTS+106 is also the most Cu‑efficient fraction (16.7 % of Cu from 8.6 % of mass, index ~1.9), and it is the only fraction where Cu tracks the Fe spike (14.6 % Fe there vs 56 % Fe in CTS+C1, which is the lowest‑Cu‑per‑mass coarse fraction). The fine‑fines CTS‑C5 is instead the gangue/trace‑element sink (highest Al, K, Th, U₃O₈, Y, LREE, Zn, Ni, Pb) — its Cu is diluted by clay/sericite‑rich matrix rather than being genuinely leach‑poor.

