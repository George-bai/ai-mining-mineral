### thinking

Question: "Which size fraction carries the most copper?" This could mean either the highest concentration (Cu ppm), or the total mass of copper (concentration × mass %). "Carries" suggests the total amount of copper within the fraction. Let me calculate.

Cu values: CTS+106: 2250, mass 8.6; +75: 1864, 7.7; +53: 1265, 10.1; C1: 1390, 13.1; C3: 775, 13.8; C5: 860, 5.2; -C5: 1084, 33.3.

Concentration: +106 is the highest at 2250.

Total amount: 2250*8.6=19350; 1864*7.7=14353; 1265*10.1=12776; 1390*13.1=18209; 775*13.8=10695; 860*5.2=4472; 1084*33.3=36097.

So, in terms of total amount, CTS-C5 (the coarsest fraction) carries the most copper, and in terms of concentration, CTS+106 is the highest. The question says "carries the most copper"—it's ambiguous, but "carries" suggests total amount. Let me run Python to confirm.

### bash

```
python3 -c "
fracs = {
 'CTS+106': (8.6, 2250),
 'CTS+75': (7.7, 1864),
 'CTS+53': (10.1, 1265),
 'CTS+C1': (13.1, 1390),
 'CTS+C3': (13.8, 775),
 'CTS+C5': (5.2, 860),
 'CTS-C5': (33.3, 1084),
}
total = sum(m*c for m,c in fracs.values())
for f,(m,c) in fracs.items():
    print(f, 'conc ppm:', c, '  mass-weighted Cu (ppm*%):', round(m*c,1), f'({m*c/total*100:.1f}% of total Cu)')
"
```

Result:

```
CTS+106 conc ppm: 2250   mass-weighted Cu (ppm*%): 19350.0 (16.7% of total Cu)
CTS+75 conc ppm: 1864   mass-weighted Cu (ppm*%): 14352.8 (12.4% of total Cu)
CTS+53 conc ppm: 1265   mass-weighted Cu (ppm*%): 12776.5 (11.0% of total Cu)
CTS+C1 conc ppm: 1390   mass-weighted Cu (ppm*%): 18209.0 (15.7% of total Cu)
CTS+C3 conc ppm: 775   mass-weighted Cu (ppm*%): 10695.0 (9.2% of total Cu)
CTS+C5 conc ppm: 860   mass-weighted Cu (ppm*%): 4472.0 (3.9% of total Cu)
CTS-C5 conc ppm: 1084   mass-weighted Cu (ppm*%): 36097.2 (31.1% of total Cu)
```

### thinking

Answer: In terms of concentration, the +106 (coarsest) fraction is the highest at 2250 ppm, but in terms of total copper carried (concentration × mass), CTS-C5 is the highest at 31% of the total. The question "which size fraction carries the most copper" — "carries" suggests total amount. Answer: CTS-C5 (the coarsest fraction, >106 µm… actually, CTS-C5 means coarser than 5 µm, i.e., the coarsest fraction). Note that the fraction labels are CTS+106 (coarsest, >106 µm), CTS+75, +53, +C1, +C3, +C5, and -C5 (finest, <5 µm). Hmm, actually, in the case of tailings, "CTS+106" probably means +106 µm. Therefore, the coarsest fraction has the highest concentration, and the finest fraction (CTS-C5, <5 µm) has the largest total copper due to its 33.3% mass.

### reply

**The CTS‑C5 fraction (the finest fraction, <5 µm, 33.3% of the sample mass) carries the most copper overall.**

- By **concentration**, the coarsest fraction (CTS+106) is richest at 2250 ppm Cu.
- By **total copper carried** (concentration × mass), CTS‑C5 dominates: 1084 ppm × 33.3% mass ≈ 36,100 (ppm·%), i.e. about **31% of the total Cu** in the sample — more than any other fraction (next highest is CTS+106 at ~17%).

So, since CTS‑C5 makes up nearly a third of the sample mass and still holds ~1084 ppm Cu, it holds the largest absolute share of the copper.

