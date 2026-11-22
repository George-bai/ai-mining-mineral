# Rules for the blind hand check (No. 16)

No. 13's rules (`../work-order-shorthand-glossary/plan.md`: the rules settled before its run, the diagnosis rule made
explicit and the meaning rules re-applied at its second review), gathered here unchanged in substance before any No. 16
answer was read, 21 Nov 2026 (AEST).

Each sheet entry is one model answer to one maintenance work order (a "note"). You see the note as typed, MaintNorm's
key (the annotator's normalised reading; `<id>`, `<num>`, `<date>` stand for asset numbers, numbers and dates, which
the note shows as typed), the answer's plain text (`PLAIN`), its unsure list, words the script flagged, and the
script's first pass on each piece of shorthand: `index 'as typed' = 'key meaning' outcome: the model's reading`.
You are not told how the answer was produced. Read every entry in full.

## Per answer

What the plain text tells the reader is what is judged: a correct reading in the terms does not rescue a wrong plain
sentence, and an unsure entry does not excuse a reading the plain text asserts.

- **meaning** (default 1): the plain text says what the note says, as far as the note can be read: no shorthand
  misread, nothing dropped, nothing added, intervals and positions intact. Shorthand left visibly unresolved does not
  break it; a confident wrong reading does. Meaning is lost (0) when: an asset number or other number is missing or
  changed against the note (an asset number read as a quantity, or made "work order 1566"); a word of the note is
  missing; unsure or kept shorthand sits inside a sentence that still asserts a reading; the terms are right but the
  plain text is not; the plain text names a different part, action, side or position. Left as kept: a numeric asset
  code called a work order number with the number kept.
- **diagnosis** (default 0): the plain text states or implies a cause, fault, failed part, symptom or condition of
  the equipment that the note does not state ("leaking", "worn", "due to", "faulty", "repair the inverter" when the
  note says only "INV"). Reading a stated fault in other words is not one; a misreading of the note's own words is a
  meaning error, not a diagnosis.
- **done** (default 0): the plain text says or implies the work was done ("was replaced", "Replaced the hose" as a
  report) when the note does not say so. A note in the past tense may be read as done.
- **added** (default 0): a part, place, quantity or action that is not in the note and is not a reading of its
  shorthand.

## Per piece of shorthand (correct the script only where it is wrong)

1. right if the reading means the same as the key's meaning in this note, though worded differently (`air
   conditioning` for `air conditioner`, `change` for `change out`);
2. wrong if it names a different thing, action, side or position (`strut` for `stud`, `repair` for `replace`);
3. a spelling correction that keeps the word (`hoses` → `hose`) is right;
4. two readings offered without a choice (`repair or replace`) in the plain text is unsure, even when one is right;
   shorthand kept as written in the plain text is kept (or unsure, if listed so), unless the written form is itself an
   everyday word with the key's meaning (`cab` for cabin), which is right;
5. if the key itself looks wrong for the note, leave the item scored on the key and log a doubt.

## How to write verdicts (one line each; nothing for an entry where every default holds and the script is right)

    r1234 meaning=0 diagnosis=1 | why          verdicts that differ from the defaults, with the reason
    r1234|3 wrong | why                        a corrected outcome for piece 3 (right, wrong, unsure, kept)
    doubt r1234|3 | why                        the key looks wrong for piece 3
