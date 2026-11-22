# Hand-check rules (fixed 20 Nov 2026, before any item was read)

The script grades every answer first. Each answer is then read beside its key and graded again by these rules.
A correction applies to every model and run that gave the same answer to the same question.

**What counts as the answer.** The model's first non-empty output line, as the paper's
evaluator reads it. A leading "Answer:" or "The answer is" label, bullets, bold or quotes are ignored. Later lines
do not count. A first line that is reasoning or prose and states no answer scores 0.

**The key is never changed.** If the key itself looks wrong, grade against it anyway and record a `key_issue`.

## Mineral-Term (definition → term)
1 when the answer names the same concept as the key term: the term itself, a spelling variant (US/UK spelling,
diacritics such as Lüders/Lueders, hyphen or space), singular/plural, or an accepted synonym that standard
geological glossaries treat as the same thing. 0 for a broader, narrower or merely related term, and for the key
term with an added word that changes what it names (e.g. "skarn deposit" for "skarn").

## Mineral-Property (mineral + property → value)
- **element_list**: 1 when the set of elements equals the key's set exactly. Order is ignored; symbols, names or a
  formula are all fine. One missing or extra element is 0.
- **crystal_system**: 1 for the same crystal system. Cubic = isometric, triclinic = anorthic; trigonal and
  hexagonal are accepted for each other (one crystal family). Naming two systems is 0 unless the key has both.
- **hardness**: 1 when the answer's value (the midpoint of a range) lies within 0.5 Mohs of the key, or of the key's
  range widened by 0.5 on each side.
- **specific_gravity**: 1 when the answer's value (the midpoint of a range) lies within 3 % of the key, or of the
  key's range widened by 3 %. Units are ignored.
- **luster, streak, colour**: 1 when every value the answer names appears in the key, and it names at least one.
  "X to Y", "X - Y" and "X, Y" are the same list. Spelling variants match (grey/gray, colourless/colorless,
  lustre/luster). Synonyms: vitreous = glassy, dull = earthy. A shade qualifier (pale, light, dark, deep, bright)
  matches the plain colour; a compound such as "yellowish brown" matches "brown", "yellowish brown" or
  "yellow-brown" in the key. For streak only, white and colourless match each other. Submetallic is not metallic.
- **cleavage**: 1 when the answer's quality matches the key's: perfect (= excellent), good (= distinct),
  fair, poor (= imperfect, indistinct), none (= absent, no cleavage). Miller indices, if the answer gives them and the
  key has them, must match. When the key lists several cleavages, one correctly named is enough, provided nothing
  in the answer contradicts the key.

## Geo-NER (text → entities by label)
Entities are matched by exact span within the same label, as the script does. The hand check adds a match only when
a predicted span and a gold span of the same label are the same mention, differing by case, singular/plural,
whitespace or spacing around a hyphen ("pre - existing"), a leading article, or a possessive. A partial span
("dunite" for "chromititic dunite"), a longer span, a different label, or an abbreviation not in the key is not a
match. Correct entities missing from the key are recorded as `key_issue`, not scored.
