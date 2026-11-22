### thinking

Question: Which size fraction contains the most copper? Ambiguity: "contains the most copper" could mean either the highest Cu grade (ppm) or the largest mass contribution to total Cu (grade × mass%). Let's try calculating both.

Cu ppm: +106: 2250, +75: 1864, +53: 1265, C1: 1390, C3: 775, C5: 860, -C5: 1084.

Mass%: 8.6, 7.7, 10.1, 13.1, 13.8, 5.2, 33.3.

Contribution = ppm × mass%:
+106: 2250×8.6 = 19350
+75: 1864×7.7 = 14352.8
+53: 1265×10.1 = 12776.5
C1: 1390×13.1 = 18209
C3: 775×13.8 = 10695
C5: 860×5.2 = 4472
-C5: 1084×33.3 = 36109.2

So by mass, CTS-C5 contains the most copper (about 36% of total Cu). By grade, it's CTS+106.

Let's verify in Python.

### bash

```
python3 - <<'EOF'
mass = {'CTS+106':8.6,'CTS+75':7.7,'CTS+53':10.1,'CTS+C1':13.1,'CTS+C3':13.8,'CTS+C5':5.2,'CTS-C5':33.3}
cu   = {'CTS+106':2250,'CTS+75':1864,'CTS+53':1265,'CTS+C1':1390,'CTS+C3':775,'CTS+C5':860,'CTS-C5':1084}
total = sum(cu[f]*mass[f] for f in mass)
for f in mass:
    contrib = cu[f]*mass[f]
    print(f"{f:8s} Cu grade {cu[f]:5d} ppm | mass {mass[f]:5.1f}% | Cu contribution {contrib:9.1f} ({contrib/total*100:5.1f}% of total)")
EOF
```

Result:

```
CTS+106  Cu grade  2250 ppm | mass   8.6% | Cu contribution   19350.0 ( 16.7% of total)
CTS+75   Cu grade  1864 ppm | mass   7.7% | Cu contribution   14352.8 ( 12.4% of total)
CTS+53   Cu grade  1265 ppm | mass  10.1% | Cu contribution   12776.5 ( 11.0% of total)
CTS+C1   Cu grade  1390 ppm | mass  13.1% | Cu contribution   18209.0 ( 15.7% of total)
CTS+C3   Cu grade   775 ppm | mass  13.8% | Cu contribution   10695.0 (  9.2% of total)
CTS+C5   Cu grade   860 ppm | mass   5.2% | Cu contribution    4472.0 (  3.9% of total)
CTS-C5   Cu grade  1084 ppm | mass  33.3% | Cu contribution   36097.2 ( 31.1% of total)
```

### thinking

Answer: It depends on the interpretation. By grade, it's CTS+106. By absolute mass of copper, it's CTS-C5. I'll present both, but since "carries the most copper" usually means total quantity, I'll lead with CTS-C5.

### reply

It depends on what you mean by "carries the most copper":

- **By grade (Cu concentration):** the **CTS+106** (coarsest, >106 µm) fraction, at **2 250 ppm Cu** — the highest of any fraction.
- **By absolute copper carried (grade × mass fraction):** the **CTS−C5** (finest, <5 µm) fraction, which contributes **≈31% of the total copper** in the sample (1 084 ppm × 33.3% mass), roughly double the next-highest fraction (CTS+106, ≈17%).

So if the question is which fraction *holds* the most copper in the tailings, the answer is the **CTS−C5 (<5 µm) fine fraction**; if it's which fraction is most *enriched* in copper, it's the **CTS+106** fraction.

