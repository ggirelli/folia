"""Highlighting review for spike 1: Rouge (Jekyll) against Folia (syntect), by rendered style.

usage: python3 -I review.py BASELINE FOLIA_HTML DOCS_LIST OUT_DIR

FOLIA_HTML holds Folia's body HTML for each document, as `render.rs` writes it; DOCS_LIST names
the documents (paths relative to the dump's `content/`, without `.html`).

For every highlighted block (div.highlight) of each document, each non-whitespace character
gets the class of its innermost span on both sides. The site's compiled stylesheet gives each
class a style (color, weight, slant, background); a class without a rule gets the `.highlight`
default. Agreement is reported both by class and by style, and review pages are written with
each block side by side, under the site's real main.css.
"""

import collections
import html
import html.parser
import json
import pathlib
import re
import sys

baseline, folia_dir, docs_list, out = map(pathlib.Path, sys.argv[1:5])
out.mkdir(parents=True, exist_ok=True)

css_text = (baseline / "site/assets/css/main.css").read_text()
(out / "main.css").write_text(css_text)

# --- styles from the compiled stylesheet -------------------------------------------------------
DEFAULT = {
    "color": "#f8f8f2",
    "font-weight": "normal",
    "font-style": "normal",
    "background-color": "none",
}
styles = {}
other_highlight_selectors = set()
for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css_text):
    decls = {
        k.strip(): v.strip() for k, v in (d.split(":", 1) for d in body.split(";") if ":" in d)
    }
    for sel in selectors.split(","):
        sel = sel.strip()
        m = re.fullmatch(r"\.highlight \.([a-z0-9]+)", sel)
        if m:
            styles.setdefault(m.group(1), {}).update(decls)
        elif ".highlight" in sel or "pre code" in sel or sel == "code":
            other_highlight_selectors.add(sel)


def style(cls):
    s = dict(DEFAULT)
    if cls:
        s.update({k: v for k, v in styles.get(cls, {}).items() if k in DEFAULT})
    return (s["color"], s["font-weight"], s["font-style"], s["background-color"])


def show(st):
    color, weight, slant, bg = st
    parts = [color]
    if weight != "normal":
        parts.append(weight)
    if slant != "normal":
        parts.append(slant)
    if bg != "none":
        parts.append("bg " + bg)
    return " ".join(parts)


# --- per-character classes ------------------------------------------------------------------------
class Blocks(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []  # (lang, [(char, class)], raw_html)
        self.lang_stack = []
        self.in_highlight = 0
        self.code = None
        self.spans = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "div":
            lang = next((c[len("language-") :] for c in classes if c.startswith("language-")), None)
            self.lang_stack.append(lang)
        if tag == "pre" and "highlight" in classes:
            self.in_highlight += 1
        if tag == "code" and self.in_highlight:
            lang = next((l for l in reversed(self.lang_stack) if l), None)
            self.code = (lang, [])
            self.spans = []
        elif tag == "span" and self.code is not None:
            self.spans.append(classes[0] if classes else "")

    def handle_endtag(self, tag):
        if tag == "span" and self.code is not None and self.spans:
            self.spans.pop()
        elif tag == "code" and self.code is not None:
            self.blocks.append(self.code)
            self.code = None
        elif tag == "pre" and self.in_highlight:
            self.in_highlight -= 1
        elif tag == "div" and self.lang_stack:
            self.lang_stack.pop()

    def handle_data(self, data):
        if self.code is not None:
            cls = self.spans[-1] if self.spans else ""
            self.code[1].extend((ch, cls) for ch in data)


def blocks_of(text):
    p = Blocks()
    p.feed(text)
    return p.blocks


# --- compare ------------------------------------------------------------------------------------
by_lang = collections.defaultdict(lambda: [0, 0, 0, 0])  # blocks, chars, class-agree, style-agree
style_conf = collections.Counter()
emitted = {"rouge": collections.Counter(), "folia": collections.Counter()}
pages = []
docs = [d for d in docs_list.read_text().split() if not d.startswith("blog/")]
for doc in docs:
    j = blocks_of((baseline / "dump/content" / (doc + ".html")).read_text())
    f = blocks_of((folia_dir / (doc + ".html")).read_text())
    assert len(j) == len(f), (doc, len(j), len(f))
    rows = []
    for (lang, jc), (_, fc) in zip(j, f, strict=True):
        assert "".join(c for c, _ in jc) == "".join(c for c, _ in fc), doc
        lang = lang or "?"
        entry = by_lang[lang]
        entry[0] += 1
        for (ch, a), (_, b) in zip(jc, fc, strict=True):
            if ch.isspace():
                continue
            emitted["rouge"][a] += 1
            emitted["folia"][b] += 1
            entry[1] += 1
            entry[2] += a == b
            sa, sb = style(a), style(b)
            entry[3] += sa == sb
            if sa != sb:
                style_conf[(lang, a, b, show(sa), show(sb))] += 1
        rows.append((lang, jc, fc))
    pages.append((doc, rows))


def pct(a, b):
    return f"{100 * a / max(b, 1):.1f}%"


lines = ["| Language | Blocks | Characters | Same class | Same style |", "|-|-:|-:|-:|-:|"]
tot = [0, 0, 0]
for lang, (n, c, ca, sa) in sorted(by_lang.items()):
    lines.append(f"| {lang} | {n} | {c} | {pct(ca, c)} | {pct(sa, c)} |")
    if lang not in ("text", "plaintext"):
        tot[0] += c
        tot[1] += ca
        tot[2] += sa
lines.append(
    f"| **lexed by Rouge** | | {tot[0]} | **{pct(tot[1], tot[0])}** | **{pct(tot[2], tot[0])}** |"
)
no_toml = [
    sum(v[i] for k, v in by_lang.items() if k not in ("text", "plaintext", "toml"))
    for i in (1, 2, 3)
]
lines.append(
    f"| lexed by Rouge, without TOML | | {no_toml[0]} | {pct(no_toml[1], no_toml[0])} | {pct(no_toml[2], no_toml[0])} |"
)
lines += [
    "",
    "Style disagreements (characters):",
    "",
    "| Language | Rouge class | Folia class | Rouge style | Folia style | Characters |",
    "|-|-|-|-|-|-:|",
]
for (lang, a, b, sa, sb), n in style_conf.most_common(40):
    lines.append(f"| {lang} | `{a}` | `{b}` | {sa} | {sb} | {n} |")
lines += [
    "",
    "Classes each side emits that the stylesheet has no rule for (characters; they show the default):",
    "",
]
for side in ("rouge", "folia"):
    unstyled = {c: n for c, n in emitted[side].items() if c and c not in styles}
    lines.append(
        f"- {side}: "
        + (
            ", ".join(f"`{c}` {n}" for c, n in sorted(unstyled.items(), key=lambda x: -x[1]))
            or "none"
        )
    )
lines += [
    "",
    "Other rules touching highlighted code: "
    + ", ".join(f"`{s}`" for s in sorted(other_highlight_selectors)),
]
(out / "summary.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))


# --- review pages -------------------------------------------------------------------------------
def render(chars):
    parts, cur, buf = [], None, []
    for ch, cls in chars + [("", None)]:
        if cls != cur and buf:
            text = html.escape("".join(buf))
            parts.append(f'<span class="{cur}">{text}</span>' if cur else text)
            buf = []
        cur = cls
        buf.append(ch)
    return "".join(parts)


for i, (doc, rows) in enumerate(pages, 1):
    body = []
    for k, (lang, jc, fc) in enumerate(rows, 1):
        diff = sum(
            1
            for (ch, a), (_, b) in zip(jc, fc, strict=True)
            if not ch.isspace() and style(a) != style(b)
        )
        body.append(
            f'<h3>block {k} · {lang} · {diff} characters styled differently</h3><div class="pair">'
            f'<div><b>Rouge (Jekyll)</b><div class="highlight"><pre class="highlight"><code>{render(jc)}</code></pre></div></div>'
            f'<div><b>Folia (syntect)</b><div class="highlight"><pre class="highlight"><code>{render(fc)}</code></pre></div></div></div>'
        )
    (out / f"{i:02d}.html").write_text(
        f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="main.css">'
        f"<style>body{{padding:16px;max-width:none}} .pair{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}"
        f" pre{{white-space:pre-wrap;font-size:13px;padding:8px}} h3{{font-size:15px;margin-top:16px}}</style>"
        f"<h2>{html.escape(doc)}</h2>{''.join(body)}"
    )
(out / "pages.json").write_text(json.dumps([d for d, _ in pages], indent=1))
