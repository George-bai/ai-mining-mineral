"""Output normalisation, task-specific parsing and sample-level scoring (paper Sec. 3.3/3.4).

The Evaluator applies *bounded surface normalisation* only: character-form differences, outer
formatting markers, predefined answer prefixes and redundant whitespace. It does not search
explanatory prose for answers and does not perform semantic correction. Outputs that cannot be
validly parsed are scored 0.
"""
from __future__ import annotations

import json
import re
import unicodedata

# --------------------------------------------------------------------------------------
# surface normalisation
# --------------------------------------------------------------------------------------
_PREFIX_RE = re.compile(
    r"^\s*(?:the\s+)?(?:answer|term|entity|entities|result|output|final answer|core answer)"
    r"\s*(?:is|:|=|->|-)?\s*",
    re.IGNORECASE,
)
_LEAD_BULLET_RE = re.compile(r"^[\s\-*•>\u2022]+")
_PUNCT = "`\"'’‘“”«»()[]{}<>|/\\,:;.!?¡¿#$%^&*~_+=–—-…"


def normalize(text: str) -> str:
    """Bounded surface normalisation used for both scoring and Inter-round Consistency."""
    if text is None:
        return ""
    s = unicodedata.normalize("NFKC", str(text)).strip()
    # take the first non-empty content line (multi-line answers are a formatting artefact)
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    if lines:
        s = lines[0]
    changed = True
    while changed:
        changed = False
        new = _LEAD_BULLET_RE.sub("", s)
        new = _PREFIX_RE.sub("", new)
        if new != s:
            s, changed = new, True
    s = s.strip().strip(_PUNCT).strip()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def lower_norm(text: str) -> str:
    s = normalize(text).lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^\w\s%/\.\-–]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^(a|an|the)\s+", "", s)
    return s


def token_set(text: str) -> set[str]:
    return set(re.findall(r"\w+|[-/.,]", lower_norm(text)))


# --------------------------------------------------------------------------------------
# number / range parsing (Mineral-Property)
# --------------------------------------------------------------------------------------
_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_RANGE = re.compile(r"(-?\d+(?:\.\d+)?)\s*(?:-|–|—|to|~)\s*(-?\d+(?:\.\d+)?)")


def numbers(text: str) -> list[float]:
    return [float(m) for m in _NUM.findall(normalize(text))]


def ranges(text: str) -> list[tuple[float, float]]:
    out = [(float(a), float(b)) for a, b in _RANGE.findall(normalize(text).lower())]
    for n in numbers(text):
        out.append((n, n))
    return sorted({(min(a, b), max(a, b)) for a, b in out})


NUMERIC_PROPS = {"hardness", "specific_gravity", "sg", "refractive_index", "density",
                 "mohs_hardness", "fusion"}
DESCRIPTIVE_PROPS = {"cleavage", "luster", "streak", "colour", "color", "habit", "diagram",
                     "crystal_form", "luminescence", "field_occurrences", "associated_minerals",
                     "type_of_occurrence", "imagetext"}
TEXT_PROPS = {"crystal_system"} | DESCRIPTIVE_PROPS


def first_numeric_expr(text: str) -> list[tuple[float, float]]:
    """Parse only the first numeric expression of a concise answer (bounded parsing)."""
    s = normalize(text)
    m = _RANGE.search(s)
    if m and (not _NUM.search(s) or m.start() <= _NUM.search(s).start()):
        a, b = float(m.group(1)), float(m.group(2))
        return [(min(a, b), max(a, b))]
    m = _NUM.search(s)
    if m:
        v = float(m.group())
        return [(v, v)]
    # spelled-out values ("five", "seven and a half") are not parsed by design
    return []


def numeric_match(pred: str, gold: str, tol: float = 0.15) -> bool:
    """The predicted value is correct when its first numeric expression matches a gold range."""
    pr, gr = first_numeric_expr(pred), ranges(gold)
    if not pr or not gr:
        return False
    for a, b in gr:
        span = max(b - a, abs(a) * 0.05, 0.05)
        for c, d in pr:
            lo, hi = max(a, c) - span * tol, min(b, d) + span * tol
            if lo <= hi:
                return True
    return False


ELEMENT_RE = re.compile(r"\b[A-Z][a-z]?\b")


def element_set(text: str) -> set[str]:
    toks = ELEMENT_RE.findall(normalize(text).replace(",", " "))
    valid = {
        "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P",
        "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
        "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru",
        "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce",
        "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf",
        "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn",
        "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
        "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Fl", "Mc",
        "Lv", "Ts", "Og",
    }
    return {t for t in toks if t in valid}


_CRYSTAL_ALIAS = {
    "isometric": {"cubic", "isometric"},
    "cubic": {"cubic", "isometric"},
    "hexagonal": {"hexagonal", "trigonal"},
    "trigonal": {"hexagonal", "trigonal"},
    "monoclinic": {"monoclinic"},
    "orthorhombic": {"orthorhombic"},
    "triclinic": {"triclinic", "anorthic"},
    "anorthic": {"triclinic", "anorthic"},
    "tetragonal": {"tetragonal", "diprysmatic"},
    "amorphous": {"amorphous", "glassy", "cryptocrystalline", "non-crystalline"},
}
_LUSTER_ALIAS = {
    "vitreous": {"vitreous", "glassy"},
    "glassy": {"vitreous", "glassy"},
    "metallic": {"metallic"},
    "adamantine": {"adamantine"},
    "pearly": {"pearly"},
    "silky": {"silky", "satiny"},
    "resinous": {"resinous", "resin", "rosy"},
    "greasy": {"greasy", "grease", "fat"},
    "dull": {"dull", "earthy"},
    "earthy": {"dull", "earthy"},
    "submetallic": {"submetallic", "metallic"},
    "subvitreous": {"subvitreous", "vitreous", "glassy"},
}


def property_scorer(prop: str):
    """Return a (pred, gold) -> bool comparator for a Mineral-Property question type."""
    prop = (prop or "").lower()
    if prop in ("element_list", "elements", "element_list_raw", "chemical_formula_elements"):
        def cmp(p, g):
            ps, gs = element_set(p), element_set(g)
            return bool(gs) and ps == gs
        return cmp
    if prop in NUMERIC_PROPS:
        return numeric_match
    if prop == "crystal_system":
        def cmp(p, g):
            pl, gl = lower_norm(p), lower_norm(g)
            if pl == g.lower() or gl in pl or pl in gl:
                return True
            for key, group in _CRYSTAL_ALIAS.items():
                if key in gl and any(a in pl for a in group):
                    return True
            return False
        return cmp
    if prop in DESCRIPTIVE_PROPS:
        return descriptive_match
    if prop in ("formula", "chemical_formula"):
        return formula_match
    # default: normalized containment match (short-answer tasks)
    return short_answer_match


def formula_match(pred: str, gold: str) -> bool:
    """Compare chemical formulas ignoring case-insensitive whitespace/parenthesis surface forms."""
    def canon(s: str) -> str:
        s = normalize(s)
        return re.sub(r"\s+", "", s).replace("(", "[").replace(")", "]").lower()
    return canon(pred) == canon(gold) or (
        canon(gold) in canon(pred) and len(canon(pred)) <= len(canon(gold)) + 4)


# --------------------------------------------------------------------------------------
# task-level scoring
# --------------------------------------------------------------------------------------
_STOP = {
    "the", "a", "an", "of", "in", "on", "and", "or", "to", "with", "is", "are", "its",
    "cleavage", "crystal", "system", "hardness", "luster", "streak", "colour", "color",
    "specific", "gravity", "habit", "form", "forms", "very", "rather", "some",
}


def content_tokens(text: str) -> set[str]:
    return {t for t in lower_norm(text).split() if t and t not in _STOP}


def descriptive_match(pred: str, gold: str) -> bool:
    """Surface match for descriptive property values (cleavage, streak, habit, colour...).

    Bounded: gold content tokens must all appear in a *concise* prediction (<= 25 tokens), and a
    direct substring match also counts. No semantic inference is performed.
    """
    p, g = lower_norm(pred), lower_norm(gold)
    if not p or not g:
        return False
    if p == g or g in p or p in g:
        return True
    if len(p.split()) > 25:
        return False
    gt, pt = content_tokens(g), content_tokens(p)
    return bool(gt) and gt <= pt


def short_answer_match(pred: str, gold: str) -> bool:
    """Normalised exact match; a longer output counts only if it *is* the answer (bounded)."""
    p, g = lower_norm(pred), lower_norm(gold)
    if not p or not g:
        return False
    if p == g:
        return True
    # single-token gold answers tolerate a plural / hyphen-variant surface form
    if " " not in g and p.rstrip("s") == g.rstrip("s"):
        return True
    return False


def term_scorer(pred: str, gold: str) -> bool:
    p, g = lower_norm(pred), lower_norm(gold)
    if not p or not g:
        return False
    if p == g:
        return True
    if p.startswith(g) and len(p) <= len(g) + 12:
        return True
    # "X decay", "X zone" style multi-word terms: accept when the whole gold term appears
    if len(g.split()) >= 2 and re.search(rf"\b{re.escape(g)}\b", p):
        return True
    return False


# --------------------------------------------------------------------------------------
# Geo-NER: entity-set parsing + sample-level F1
# --------------------------------------------------------------------------------------
def extract_entities(raw: str, wanted_types: list[str]) -> dict[str, set[str]]:
    """Parse a model output into {type: {span}}. Unparseable output -> {} (scored 0)."""
    out: dict[str, set[str]] = {}
    if not raw or not raw.strip():
        return out
    text = normalize_full(raw)
    # 1) try JSON-ish object
    for candidate in _json_candidates(text):
        parsed = _parse_entity_obj(candidate, wanted_types)
        if parsed:
            _merge(out, parsed)
    if out:
        return out
    # 2) fallback: "TYPE: [a, b]" / "TYPE: a, b" surface lines
    for t in wanted_types:
        m = re.search(rf"\b{re.escape(t)}\b\s*[:=]\s*(\[[^\]]*\]|[^\n\]]+)", text, re.IGNORECASE)
        if m:
            chunk = m.group(1).strip("[] ")
            spans = {norm_span(s) for s in re.split(r",|;|\band\b", chunk) if norm_span(s)}
            if spans:
                out.setdefault(t, set()).update(spans)
    return out


def normalize_full(text: str) -> str:
    s = unicodedata.normalize("NFKC", str(text))
    return re.sub(r"\s+", " ", s).strip()


def _json_candidates(text: str):
    for m in re.finditer(r"[\[{]", text):
        depth, i = 0, m.start()
        open_c, close_c = text[i], ("]" if text[i] == "[" else "}")
        while i < len(text):
            if text[i] == open_c:
                depth += 1
            elif text[i] == close_c:
                depth -= 1
                if depth == 0:
                    yield text[m.start(): i + 1]
                    break
            i += 1


def _parse_entity_obj(chunk: str, wanted: list[str]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    obj = None
    for loader in (json.loads, _lenient_json):
        try:
            obj = loader(chunk)
            break
        except Exception:
            obj = None
    if obj is None:
        return out
    dicts = []
    if isinstance(obj, dict):
        dicts = [obj]
    elif isinstance(obj, list):
        dicts = [d for d in obj if isinstance(d, dict)]
    for d in dicts:
        for k, v in d.items():
            key = str(k).strip().upper().replace("-", "_").replace(" ", "_")
            match = next((w for w in wanted if w.upper().replace("-", "_") == key), None)
            if match is None:
                continue
            vals = v if isinstance(v, list) else ([v] if isinstance(v, str) else [])
            spans = {norm_span(x) for x in vals if isinstance(x, str) and norm_span(x)}
            if spans:
                out.setdefault(match, set()).update(spans)
    return out


def _lenient_json(chunk: str):
    c = re.sub(r"^\s*```(?:json)?|```\s*$", "", chunk.strip())
    c = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_\- ]*)(\s*:)", r'\1"\2"\3', c)
    c = re.sub(r",\s*([}\]])", r"\1", c)
    return json.loads(c)


def norm_span(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower()
    s = re.sub(r"[^\w\s\-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _merge(dst: dict[str, set[str]], src: dict[str, set[str]]) -> None:
    for k, v in src.items():
        dst.setdefault(k, set()).update(v)


def gold_entities(sample: dict) -> dict[str, set[str]]:
    return {t: {norm_span(x) for x in spans} for t, spans in sample["answer"].items()}


def f1_score(pred: dict[str, set[str]], gold: dict[str, set[str]]) -> float:
    p = {(t, e) for t, spans in pred.items() for e in spans}
    g = {(t, e) for t, spans in gold.items() for e in spans}
    if not g:
        return 1.0 if not p else 0.0
    if not p:
        return 0.0
    tp = len(p & g)
    if tp == 0:
        return 0.0
    prec, rec = tp / len(p), tp / len(g)
    return 2 * prec * rec / (prec + rec)


def score_sample(sample: dict, raw_output: str) -> tuple[float, str]:
    """Return (sample-level score in [0,1], normalised output used for IC)."""
    t = sample["type"]
    if t == "Geo-NER":
        pred = extract_entities(raw_output, sample["input"]["entity_types"])
        ser = json.dumps({k: sorted(v) for k, v in sorted(pred.items())}, ensure_ascii=False)
        return f1_score(pred, gold_entities(sample)), normalize_full(ser)
    gold = sample["answer"]
    prop = sample.get("meta", {}).get("property")
    if t == "Mineral-Term":
        ok = term_scorer(raw_output, gold)
    elif prop:
        ok = property_scorer(prop)(raw_output, gold)
    else:
        ok = short_answer_match(raw_output, gold)
    return (1.0 if ok else 0.0), normalize(raw_output)
