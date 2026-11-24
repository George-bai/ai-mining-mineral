You are checking an answer key before it is used to score a tag search system. Work only with the files in this folder; do not search the web.

Files:
- test-questions.yaml: 60 questions people might ask about a mock mining company's plant historian.
- key.yaml: for each question, how it counts (counts_as) and the expected tags (asset-tree attribute paths, or a data-server point path for a point not in the asset tree).
- make_key.py: how each entry was chosen and why calculated readings count as one tag or a group; make_key_round1_rules.py: the counting rules, in its docstring.
- plant-attributes.tsv: every attribute in the plant (path, PI point it references, unit, variant). plant-points.tsv: every PI point (name, descriptor, the attribute it is linked to, blank if unlinked).

Note on locations: in the questions, "con 2" means Concentrator 2. "Site D" means Site D.

For each of the 60 questions, check:
1. Does the key's counts_as fit the question under the rules in make_key.py? (one, several, ambiguous, none)
2. Are the expected tags right: do they exist in plant-attributes.tsv or plant-points.tsv, is anything missing that the question clearly means, is anything included that it clearly does not mean?
3. For "none" questions: confirm with the TSVs that no tag matches exactly (search the point names for the code, and the attribute names for QC, Calc, alarm or moving-average variants), and say whether the near matches are sensible.

Output markdown: a table with one row per question (id, verdict OK / CHANGE, and for CHANGE the exact correction with paths), then a short list of anything systematic. Be strict but do not invent requirements the rules do not state.
