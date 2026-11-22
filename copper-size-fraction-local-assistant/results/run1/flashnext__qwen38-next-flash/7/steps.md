### thinking

The question: "Which size fraction carries the most copper?" This is ambiguous — highest Cu grade (ppm) vs. highest total Cu mass (grade × mass%). The trick: CTS+106 has highest grade (2250 ppm), but CTS-C5 has 33.3% mass at 1084 ppm → largest share of total Cu. Let's compute.

Also check mass sums: 8.6+7.7+10.1+13.1+13.8+5.2+33.3 = 91.8, not 100. Hmm. Let me compute normalized.

Let me run Python.

### bash

```
cat << 'EOF' > /tmp/cu.py
fr = [("CTS+106",8.6,2250),("CTS+75",7.7,1864),("CTS+53",10.1,1265),
      ("CTS+C1",13.1,1390),("CTS+C3",13.8,775),("CTS+C5",5.2,860),
      ("CTS-C5",33.3,1084)]
tot_m = sum(m for _,m,_ in fr)
tot_cu = sum(m*c for _,m,c in fr)
print("sum mass%% =", tot_m)
print(f"{'frac':9} {'mass%':>6} {'ppm':>5} {'Cu mass units':>13} {'%of Cu (norm)':>13} {'%mass':>6}")
for n,m,c in sorted(fr, key=lambda x:-x[1]*x[2]):
    print(f"{n:9} {m:6.1f} {c:5d} {m*c:13.1f} {100*m*c/tot_cu:12.1f}% {100*m/tot_m:5.1f}%")
print()
print("head grade (ppm Cu, mass-weighted) =", round(tot_cu/tot_m,1))
EOF
python3 /tmp/cu.py
```

Result:

```
sum mass%% = 91.8
frac       mass%   ppm Cu mass units %of Cu (norm)  %mass
CTS-C5      33.3  1084       36097.2         31.1%  36.3%
CTS+106      8.6  2250       19350.0         16.7%   9.4%
CTS+C1      13.1  1390       18209.0         15.7%  14.3%
CTS+75       7.7  1864       14352.8         12.4%   8.4%
CTS+53      10.1  1265       12776.5         11.0%  11.0%
CTS+C3      13.8   775       10695.0          9.2%  15.0%
CTS+C5       5.2   860        4472.0          3.9%   5.7%

head grade (ppm Cu, mass-weighted) = 1263.1
```

### thinking

So answer: by grade, CTS+106 (coarsest, +106 µm) at 2250 ppm. By mass (metal inventory), CTS-C5 (the -5 µm slime fraction) holds ~31% of total Cu.

The question "Which size fraction carries the most copper?" — probably intended answer: the fines/slime fraction CTS-C5 when you weight by mass% — that's the interesting insight (a published-mining angle: the ultrafine fraction hosts a large share of Cu). But I should give both, with clear framing. The mass% sums to 91.8 (some loss in sizing), so normalize.

Let me also check correlation of Cu with S etc. Not needed but could be nice. Keep concise.

Maybe quickly check: coarsest fractions highest Cu grade → Cu is liberated/coarse in coarse fractions; but slimes still hold 1/3 of the Cu because they're a third of the mass. Mention recoverability implications briefly.

### reply

**Short answer: it depends which "most" you mean — and the two answers differ.**

```
frac       mass%   Cu ppm   Cu mass units   % of total Cu (normalized)
CTS-C5      33.3     1084        36097            31.1%
CTS+106      8.6     2250        19350            16.7%
CTS+C1      13.1     1390        18209            15.7%
CTS+75       7.7     1864        14353            12.4%
CTS+53      10.1     1265        12777            11.0%
CTS+C3      13.8      775        10695             9.2%
CTS+C5       5.2      860         4472             3.9%
```
(mass% sums to 91.8 due to sizing losses, so the % columns above are renormalized; overall tailings grade ≈ 1263 ppm Cu)

- **Highest grade:** the coarsest cut, **CTS+106 (+106 µm), 2250 ppm Cu** — chalcopyornite/pyrite is liberated coarse, so Cu grade falls monotonically-ish with fineness (aside from the C1 bump).
- **Most copper overall (metal inventory):** the **-5 µm slimes, CTS-C5** — only 1084 ppm, but it is a third of the tailings mass, so it holds ~31% of all the Cu, i.e. more than the +106, +75 and +53 cuts *combined* (40% of mass... actually 39.6% of Cu).

So: richest material = CTS+106; biggest copper reservoir = CTS-C5. The mine-relevant point is that the ultrafine fraction is the single largest copper repository in the tailings — invisible if you only look at grades, and it is the fraction most likely lost to slimes during flotation.

