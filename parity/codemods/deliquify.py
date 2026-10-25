"""Replace the Liquid in the reference site's Markdown with its production expansion.

Plan v2, §10 spike 3. A one-off rewrite of FILES in the Jekyll site:

    python3 -I parity/codemods/deliquify.py --check SITE   # print the diff, exit 1 if any
    python3 -I parity/codemods/deliquify.py --write SITE   # apply it

Only the constructs in the plan's table are rewritten, and only in FILES. Any other Liquid,
in these files or in any other Markdown file of the site, fails with its file and line, and
nothing is written. The rewrite is idempotent: once applied, --check finds nothing to do.
"""

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

# The 15 Markdown files whose bodies contain Liquid (plan v2, §2.2).
FILES = (
    "_digital_garden/index.md",
    "_posts/2014/2014-05-23-vaccini-omeopatia.md",
    "_posts/2015/2015-12-13-tissue-head.md",
    "_posts/2017/2017-01-13-brush-markers.md",
    "_posts/2017/2017-02-21-eyes-palettes.md",
    "_posts/2018/2018-09-09-tao-dance-theater.md",
    "_posts/2018/2018-11-01-inktober.md",
    "_posts/2019/2019-11-01-inktober.md",
    "_posts/2020/2020-01-26-multirange.md",
    "_posts/2020/2020-11-01-inktober.md",
    "_posts/2021/2021-08-08-webmentions.md",
    "_posts/2021/2021-08-17-speed-up-ggplot.md",
    "_posts/2021/2021-09-25-isola-del-garda.md",
    "_posts/2022/2022-09-03-command-palette.md",
    "_posts/2023/2023-05-15-May-train-trip-pt3.md",
)

# Values in a production build (JEKYLL_ENV=production, _config.yml at e872c37).
SITE_VALUES = {
    "site.baseurl": "",
    "site.url": "https://ggirelli.info",
    "site.paths.home": "/blog/",
    "site.webmentions.tag": "ggirelli.info",
    "site.webmentions.help_page": "/blog/2021/08/08/webmentions",
}

# page.url of the files that use it, from the spike 0 manifest.
PAGE_URLS = {
    "_posts/2021/2021-08-08-webmentions.md": "/blog/2021/08/08/webmentions",
    "_posts/2022/2022-09-03-command-palette.md": "/blog/2022/09/03/command-palette",
}

# Includes that may be expanded, with the value of each include parameter they read.
INCLUDES = {
    "digital-garden/notes_graph.html": {"include.link_classes": ""},
}

# Jekyll's own front matter pattern (Jekyll::Document::YAML_FRONT_MATTER_REGEXP).
FRONT_MATTER = re.compile(r"\A(---\s*\n.*?\n?)^((---|\.\.\.)\s*$\n?)", re.DOTALL | re.MULTILINE)
ASSIGN = re.compile(r"\{%\s*assign\s+(\w+)\s*=\s*(.+?)\s*%\}")
ASSIGN_LINE = re.compile(r"^\s*(?:\{%\s*assign\s[^%]*%\}\s*)+$")
HIGHLIGHT_OPEN = re.compile(r"^\{%\s*highlight\s+(\w+)\s*%\}$")
HIGHLIGHT_CLOSE = re.compile(r"^\{%\s*endhighlight\s*%\}$")
INCLUDE = re.compile(r"\{%\s*include\s+(\S+)\s*%\}")
OUTPUT = re.compile(r"\{\{\s*(.*?)\s*\}\}")
LITERAL = re.compile(r"""^(?:'([^']*)'|"([^"]*)")(?:\s*\|\s*prepend:\s*site\.baseurl)?$""")
LIQUID = re.compile(r"\{%|\{\{")


class LiquidError(Exception):
    """A Liquid construct the codemod does not know how to expand."""


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="print the diff; exit 1 if any")
    mode.add_argument("--write", action="store_true", help="apply the rewrite")
    parser.add_argument("site", type=Path, help="the Jekyll site")
    args = parser.parse_args()

    errors = check_other_files(args.site)
    rewrites = {}
    for rel in FILES:
        before = read(args.site / rel)
        try:
            rewrites[rel] = (before, rewrite(args.site, rel, before))
        except LiquidError as error:
            errors.append(f"{rel}:{error}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2

    changed = {rel: pair for rel, pair in rewrites.items() if pair[0] != pair[1]}
    if args.write:
        for rel, (_, after) in changed.items():
            write(args.site / rel, after)
        print(f"Rewrote {len(changed)} of {len(FILES)} files.", file=sys.stderr)
        return 0

    for rel, (before, after) in changed.items():
        sys.stdout.writelines(
            difflib.unified_diff(
                before.splitlines(True), after.splitlines(True), f"a/{rel}", f"b/{rel}"
            )
        )
    print(f"{len(changed)} of {len(FILES)} files would change.", file=sys.stderr)
    return 1 if changed else 0


# --- Rewriting a file ----------------------------------------------------------------------


def rewrite(site, rel, text):
    """Returns text with every Liquid construct in its body replaced by its expansion."""
    match = FRONT_MATTER.match(text)
    front, body = (text[: match.end()], text[match.end() :]) if match else ("", text)
    offset = front.count("\n")
    variables = {}
    lines = []  # None marks a line that held only assign tags
    highlight = None  # (language, body lines, opening line number) inside a highlight block

    for number, line in enumerate(body.splitlines(True), start=offset + 1):
        content = line.rstrip("\r\n")
        if highlight:
            if HIGHLIGHT_CLOSE.match(content):
                lines.append(fence(highlight, line[len(content) :]))
                highlight = None
            elif LIQUID.search(content):
                raise LiquidError(f"{number}: Liquid inside a highlight block")
            else:
                highlight[1].append(line)
        elif opening := HIGHLIGHT_OPEN.match(content):
            highlight = (opening.group(1), [], number)
        elif ASSIGN_LINE.match(content):
            for name, expression in ASSIGN.findall(content):
                variables[name] = evaluate(expression, rel, variables, number)
            lines.append(None)
        else:
            lines.append(expand_line(site, rel, line, variables, number))

    if highlight:
        raise LiquidError(f"{highlight[2]}: highlight block is never closed")
    return front + "".join(drop_assign_lines(lines))


def fence(highlight, newline):
    """A fenced code block for a highlight block. Jekyll strips the code's leading and
    trailing line terminators, so the fence does too. Jekyll labels the block with Rouge's
    lexer tag, which is lowercase, while a fence keeps its language verbatim: lowercasing it
    keeps the language class (`language-r`, not `language-R`)."""
    language, body, _ = highlight
    code = "".join(body).strip("\r\n")
    return f"```{language.lower()}{newline}{code}{newline}```{newline}"


def drop_assign_lines(lines):
    """Liquid renders each assign-only line as an empty line, so a run of them is one blank
    line to Markdown. Keep exactly one blank line there: none is added next to an existing
    one, and of two that would meet, one is dropped."""
    out = []
    index = 0
    while index < len(lines):
        if lines[index] is not None:
            out.append(lines[index])
            index += 1
            continue
        end = index
        while end < len(lines) and lines[end] is None:
            end += 1
        blank_before = not out or not out[-1].strip()
        blank_after = end == len(lines) or not lines[end].strip()
        if blank_before and blank_after and end < len(lines):
            end += 1
        elif not blank_before and not blank_after:
            out.append("\n")
        index = end
    return out


def expand_line(site, rel, line, variables, number):
    line = INCLUDE.sub(lambda m: render_include(site, m.group(1), number), line)
    line = OUTPUT.sub(lambda m: evaluate(m.group(1), rel, variables, number), line)
    if LIQUID.search(line):
        raise LiquidError(f"{number}: unrecognized Liquid: {line.strip()}")
    return line


def evaluate(expression, rel, variables, number):
    """The production value of a Liquid expression from the plan's table."""
    if expression in variables:
        return variables[expression]
    if expression in SITE_VALUES:
        return SITE_VALUES[expression]
    if expression == "page.url" and rel in PAGE_URLS:
        return PAGE_URLS[rel]
    if literal := LITERAL.match(expression):
        value = literal.group(1) if literal.group(1) is not None else literal.group(2)
        return SITE_VALUES["site.baseurl"] + value if "prepend" in expression else value
    raise LiquidError(f"{number}: unrecognized expression: {expression}")


def render_include(site, name, number):
    if name not in INCLUDES:
        raise LiquidError(f"{number}: unrecognized include: {name}")
    text = read(site / "_includes" / name)
    params = INCLUDES[name]

    def parameter(match):
        if match.group(1) not in params:
            raise LiquidError(f"{number}: include {name} reads {match.group(1)}")
        return params[match.group(1)]

    text = OUTPUT.sub(parameter, text)
    if LIQUID.search(text):
        raise LiquidError(f"{number}: include {name} holds other Liquid")
    return text


# --- Other files ---------------------------------------------------------------------------


def check_other_files(site):
    """Errors for Liquid in any tracked Markdown file outside FILES."""
    listed = subprocess.run(
        ["git", "-C", str(site), "ls-files", "-z", "--", "*.md", "*.markdown"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.split("\0")
    errors = []
    for rel in sorted(filter(None, listed)):
        if rel in FILES or not (site / rel).is_file():
            continue
        text = read(site / rel)
        match = FRONT_MATTER.match(text)
        start = match.end() if match else 0
        for found in LIQUID.finditer(text, start):
            errors.append(
                f"{rel}:{text.count(chr(10), 0, found.start()) + 1}: Liquid outside FILES"
            )
    return errors


def read(path):
    with path.open(encoding="utf-8", newline="") as file:
        return file.read()


def write(path, text):
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(text)


if __name__ == "__main__":
    sys.exit(main())
