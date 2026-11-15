"""Render every flowsheet.mmd of a run with headless Chrome and Mermaid (from a CDN).
Writes mermaid.svg and mermaid.json (size, node and line counts) beside each file; a file Mermaid cannot
parse gets its error in mermaid.json instead.   Usage: python3 render.py ../local/runs/run3"""
import html, json, re, subprocess, sys
from pathlib import Path

PAGE = """<!doctype html><meta charset="utf-8"><title>wait</title>
<pre id="src" hidden>%s</pre><div id="out"></div>
<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.4.0/dist/mermaid.esm.min.mjs";
// Plain SVG text (no HTML labels) so the file works as an image everywhere; colours are the article's.
mermaid.initialize({startOnLoad: false, maxTextSize: 500000, maxEdges: 5000, htmlLabels: false,
  flowchart: {useMaxWidth: false, htmlLabels: false}, theme: "base", fontFamily: "Arial, Helvetica, sans-serif",
  themeVariables: {fontSize: "15px", primaryColor: "#faf9f7", primaryBorderColor: "#1a1816", primaryTextColor: "#1a1816",
    lineColor: "#1a1816", clusterBkg: "#f5e6d3", clusterBorder: "#b84f33", edgeLabelBackground: "#faf9f7",
    tertiaryColor: "#f5e6d3", titleColor: "#b84f33"}});
const out = {};
try {
  const {svg} = await mermaid.render("d", document.getElementById("src").textContent);
  document.getElementById("out").innerHTML = svg;
  const el = document.querySelector("#out svg"), b = el.getBoundingClientRect();
  // Mermaid styles its SVG with a style sheet and style attributes, which a strict security policy
  // (style-src 'self') blocks. Copy what the browser worked out onto plain attributes, then drop both.
  const SHAPE = ["fill", "stroke", "stroke-width", "stroke-dasharray", "opacity"], TEXT = ["fill", "font-family", "font-size", "font-weight", "text-anchor", "dominant-baseline"];
  const todo = [];
  for (const n of el.querySelectorAll("path,rect,polygon,circle,ellipse,line,text,tspan")) {
    const cs = getComputedStyle(n), list = n.matches("text,tspan") ? TEXT : SHAPE;
    todo.push([n, list.map((k) => [k, cs.getPropertyValue(k)]).filter(([k, v]) => v && !(k === "stroke-dasharray" && v === "none") && !(k === "opacity" && v === "1"))]);
  }
  for (const [n, attrs] of todo) for (const [k, v] of attrs) n.setAttribute(k, v);
  for (const n of el.querySelectorAll("style")) n.remove();
  for (const n of [el, ...el.querySelectorAll("[style]")]) n.removeAttribute("style");
  el.setAttribute("width", Math.ceil(b.width)); el.setAttribute("height", Math.ceil(b.height));
  Object.assign(out, {ok: true, width: Math.ceil(b.width), height: Math.ceil(b.height),
    nodes: el.querySelectorAll("g.node").length, lines: el.querySelectorAll("path.flowchart-link").length,
    groups: el.querySelectorAll("g.cluster").length});
} catch (e) { Object.assign(out, {ok: false, error: e.message}); }
document.getElementById("src").textContent = JSON.stringify(out);
document.title = "done";
</script>"""

def dump(url):
    return subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--virtual-time-budget=20000",
                           "--dump-dom", url], capture_output=True, text=True, timeout=120).stdout

for mmd in sorted(Path(sys.argv[1]).resolve().glob("*/*/flowsheet.mmd")):
    page = mmd.with_name("mermaid.html")
    page.write_text(PAGE % html.escape(mmd.read_text()))
    dom = dump(page.as_uri())
    page.unlink()
    info = json.loads(html.unescape(re.search(r'<pre id="src" hidden="">(.*?)</pre>', dom, re.S).group(1)))
    if info["ok"]:
        svg = re.search(r'<div id="out">(<svg.*</svg>)</div>', dom, re.S).group(1)
        svg = svg.replace("<br>", "<br/>")
        mmd.with_name("mermaid.svg").write_text(svg + "\n")
    mmd.with_name("mermaid.json").write_text(json.dumps(info) + "\n")
    print("/".join(mmd.parts[-3:-1]), info)
