### thinking

Question: Which size fraction contains the most copper? "Carries the most copper" — this could mean either the highest grade (ppm) or the total mass of copper (ppm × mass%). Let's calculate both.

Cu ppm: +106: 2250 (8.6%), +75: 1864 (7.7), +53: 1265 (10.1), C1: 1390 (13.1), C3: 775 (13.8), C5: 860 (5.2), -C5: 1084 (33.3).

Total Cu contribution: 2250*8.6=19350; 1864*7.7=14352.8; 1265*10.1=12776.5; 1390*13.1=18209; 775*13.8=10695; 860*5.2=4472; 1084*33.3=36097.2.

Therefore, by total mass, CTS-C5 (the coarsest fraction, 33.3% of the mass) contains the most copper. By grade, +106.

"Carries the most copper" — probably means total mass. Answer: CTS-C5. Let's verify with Python.

### bash

```
python3 -c "
data = {
 'CTS+106': (8.6, 2250),
 'CTS+75':  (7.7, 1864),
 'CTS+53':  (10.1, 1265),
 'CTS+C1':  (13.1, 1390),
 'CTS+C3':  (13.8, 775),
 'CTS+C5':  (5.2, 860),
 'CTS-C5':  (33.3, 1084),
}
tot = sum(m*g for m,g in data.values())
for f,(m,g) in data.items():
    print(f, f'grade={g} ppm, mass={m}%, Cu mass contrib={m*g:.0f} ({m*g/tot*100:.1f}%)')
"
```

Result:

```
CTS+106 grade=2250 ppm, mass=8.6%, Cu mass contrib=19350 (16.7%)
CTS+75 grade=1864 ppm, mass=7.7%, Cu mass contrib=14353 (12.4%)
CTS+53 grade=1265 ppm, mass=10.1%, Cu mass contrib=12776 (11.0%)
CTS+C1 grade=1390 ppm, mass=13.1%, Cu mass contrib=18209 (15.7%)
CTS+C3 grade=775 ppm, mass=13.8%, Cu mass contrib=10695 (9.2%)
CTS+C5 grade=860 ppm, mass=5.2%, Cu mass contrib=4472 (3.9%)
CTS-C5 grade=1084 ppm, mass=33.3%, Cu mass contrib=36097 (31.1%)
```

### thinking

Answer: CTS-C5 (the coarsest fraction, >5 mm… actually "CTS-C5" — C probably means coarse, and -C5 means coarser than 5 mm? Hmm, the naming: +106, +75, +53 are mesh sizes, and C1/C3/C5 are probably mm. CTS-C5 = coarser than 5 mm? But then it would overlap with +106… Actually, +106 mesh = -150 µm. In any case, CTS-C5 is the largest fraction, 33.3% of the mass.)

### reply

**The CTS‑C5 fraction carries the most copper.**

- Highest *grade*: CTS+106 at 2250 ppm Cu
- But by *total mass of copper* (grade × fraction mass), CTS‑C5 dominates: 1084 ppm × 33.3% mass ≈ 36,100 relative units, i.e. **~31% of all the copper in the sample** — more than double the next highest fraction (CTS+106, ~17%).

So although CTS‑C5 is only moderately enriched in copper, it makes up nearly a third of the sample mass, which makes it the fraction that carries the most copper overall.

