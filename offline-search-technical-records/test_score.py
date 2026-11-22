"""python test_score.py: the scoring rules on made-up excerpt lists."""
from score import QUESTIONS, score_list

T26 = "x/newmont-cadia-trs-2026.md", "Newmont 2026 / Page 14-3"
T24 = "x/newmont-cadia-trs-2024.md", "Newmont 2024 / Page 14-4"
Q21 = "x/newcrest-2021-12-quarterly.md", "Newcrest / Page 3"
P9 = "x/newcrest-2021-12-quarterly.md", "Newcrest / Page 9"
ex = lambda where, text: {"path": where[0], "heading": where[1], "content": text}
FEED1, FEED2 = "The molybdenum plant receives feed from the overland copper concentrate pipeline that", "transports slurry to the Blayney concentrate filter plant."
MILE = "Commissioning of the Molybdenum Plant is continuing with the milestone of producing a filtered moly concentrate achieved."

# the feed sentence split over two excerpts from the same page counts once both are shown
s = score_list(QUESTIONS["q02"], [ex(T26, FEED1), ex(Q21, "Cadia gold"), ex(T26, FEED2), ex(Q21, MILE)])
assert s["shown"] == {"feed": 3, "filtered-2021": 4} and s["complete@5"] and s["page"]["feed"] == 1
# q03 needs the 2026 edition: the 2024 copy is the right fact from the wrong edition
s = score_list(QUESTIONS["q03"], [ex(T24, FEED1 + " " + FEED2), ex(Q21, MILE)])
assert s["shown"]["feed"] is None and s["wrong_edition"]["feed"] == 1 and not s["complete@10"]
# only the first 10 excerpts count; a right page without the words is a page hit, not a fact
s = score_list(QUESTIONS["q02"], [ex(T26, "Table 14-1")] + [ex(P9, "other")] * 10 + [ex(T26, FEED1 + FEED2)])
assert s["shown"]["feed"] is None and s["page"]["feed"] == 1 and s["pages@5"] is False
print("ok")
