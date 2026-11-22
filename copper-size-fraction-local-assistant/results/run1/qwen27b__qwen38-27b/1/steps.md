### thinking

The question is: which size fraction contains the most copper? It's ambiguous: either the highest Cu grade (ppm), or the largest total Cu mass (grade × mass fraction). "Carries the most copper" — probably total mass. Let me calculate.

Cu ppm: +106: 2250, +75: 1864, +53: 1265, C1: 1390, C3: 775, C5: 860, -C5: 1084.

Mass %: 8.6, 7.7, 10.1, 13.1, 13.8, 5.2, 33.3.

Cu contribution = ppm × mass%:
+106: 2250×8.6 = 19350
+75: 1864×7.7 = 14352.8
+53: 1265×10.1 = 12776.5
C1: 1390×13.1 = 18209
C3: 775×13.8 = 10695
C5: 860×5.2 = 4472
-C5: 1084×33.3 = 36109.2

Total ≈ 115,965. -C5 is the largest, about 31%.

Highest grade: +106 (2250 ppm).

"Carries the most copper" — total mass → CTS-C5. Let me run Python to confirm.

### bash

```
python3 - <<'EOF'
data = {
 'CTS+106': (8.6, 2250),
 'CTS+75':  (7.7, 1864),
 'CTS+53':  (10.1, 1265),
 'CTS+C1':  (13.1, 1390),
 'CTS+C3':  (13.8, 775),
 'CTS+C5':  (5.2, 860),
 'CTS-C5':  (33.3, 1084),
}
total = sum(m*c for m,c in data.values())
for f,(m,c) in data.items():
    print(f, f"grade={c} ppm, share of Cu = {m*c/total*100:.1f}%")
print("sum mass% =", sum(m for m,_ in data.values()))
EOF
```

Result:

```
CTS+106 grade=2250 ppm, share of Cu = 16.7%
CTS+75 grade=1864 ppm, share of Cu = 12.4%
CTS+53 grade=1265 ppm, share of Cu = 11.0%
CTS+C1 grade=1390 ppm, share of Cu = 15.7%
CTS+C3 grade=775 ppm, share of Cu = 9.2%
CTS+C5 grade=860 ppm, share of Cu = 3.9%
CTS-C5 grade=1084 ppm, share of Cu = 31.1%
sum mass% = 91.8
```

### thinking

Answer: CTS-C5 (the fraction finer than 5 µm) contains the most copper in absolute terms (about 31% of the total Cu in the sample), but the highest grade is CTS+106 (2250 ppm).

### reply

**CTS‑C5 (the fraction finer than 5 µm) carries the most copper.**

While the coarsest fraction (CTS+106) has the highest *grade* (2,250 ppm Cu), the CTS‑C5 fraction is by far the most abundant (33.3% of the sample mass) and still assays 1,084 ppm Cu. Multiplying grade × mass share, CTS‑C5 holds about **31% of the total copper** in the sample — more than any other fraction (next highest: CTS+106 at ~17% and CTS+C1 at ~16%).

