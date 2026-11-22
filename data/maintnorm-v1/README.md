# MaintNorm, version 1

MaintNorm: 12,000 maintenance work order texts ("maintenance short texts") from three Australian mining and mineral
processing companies, A, B and C, 4,000 each, mostly heavy mobile equipment. Every token is paired with its
normalised form (abbreviations expanded, misspellings corrected, case fixed) by one annotator; asset numbers,
numbers, dates and names are masked as `<id>`, `<num>`, `<date>` and `<sensitive>`, and the raw text carries mock
values in their place, not the companies' own.

Bikaun, T., Hodkiewicz, M. and Liu, W. (2024). MaintNorm. Proceedings of the Ninth Workshop on Noisy and
User-generated Text (W-NUT 2024), pages 68–78. https://aclanthology.org/2024.wnut-1.7

| Property | Value |
|---|---|
| Source | https://github.com/nlp-tlp/maintnorm, commit `e98ca406f7afffbb0ab3243aa7c922f3b64bc7c8` (10 Jan 2025) |
| Licence | MIT, "Copyright (c) [2024] [NLP-TLP Group]". A slice may be republished with that notice |
| Files | `local/repo/` (gitignored): the cloned repository; the data is `data/company_{a,b,c}/{train,val,test}.norm` |
| Format | WNUT normalisation format: one `raw<TAB>normalised` token per line, a blank line between texts |
| Split | per company 3,200 train, 400 val, 400 test texts |
| Cloned | 20 Nov 2026 |

SHA-256 of the files used:

| File | SHA-256 |
|---|---|
| `company_a/train.norm` | `0cbd2efe0dca234891e0d4ec9a7560c65003359f9657132df05f115d37fa77ed` |
| `company_a/val.norm` | `6b06cad2ab591ebf142c6e06afa41a74d5eb499d941b5ee8e9c9aca34b5528b0` |
| `company_a/test.norm` | `cf91bfcf4e7f934f9d9d1b09811822a529603049f0aaec1bef332f434d8a0529` |
| `company_b/train.norm` | `41ca9c5053bb37867361b424ed5140f3b356c0a436f7e3c9a0fc2228b46835e4` |
| `company_b/val.norm` | `53c25e2760e459200b3dab421baf62b7c3fad3f860fbf82184d448ed1d4a755d` |
| `company_b/test.norm` | `a564dea24ecce9ecdcd5a92ca146351c7e20c57c801a83dab03a370d5887a948` |
| `company_c/train.norm` | `884b021847cf2250c5a14b5f33341cd2d3580021a6954b9e44e54d233e1b5149` |
| `company_c/val.norm` | `e226fc23297108276e0343c07cedf5ca3be23281080445eae2d37644b5800a64` |
| `company_c/test.norm` | `fcfabb40697fa1eece6879b9d3ec68f689283b7cbcf08e2dc38889c9c49bbf41` |

Get it again:

```bash
git clone https://github.com/nlp-tlp/maintnorm.git ~/git/ai-mining-mineral/data/maintnorm-v1/local/repo
git -C ~/git/ai-mining-mineral/data/maintnorm-v1/local/repo checkout e98ca406f7afffbb0ab3243aa7c922f3b64bc7c8
```

Notes found while using it (20 Nov 2026): some tokens are merged into the one before (`A FRAME` → `A-frame`, the
second token normalised to nothing); some priority or code letters are dropped the same way (`P Burst hose` →
`burst hose`); a number fused to a word is masked with the word kept (`1000h` → `<num> hour`).
