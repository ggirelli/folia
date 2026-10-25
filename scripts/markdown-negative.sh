#!/usr/bin/env bash
# Shows that the Markdown parity check fails when it should (plan v5, §10 spike 1): it copies a
# baseline's dump, changes it once per gate, and also narrows and widens D-003's sources in a
# copy of the ledger, then runs `parity markdown` on the copies. It must exit 1.
#
#   scripts/markdown-negative.sh SITE BASELINE WORKDIR
#
# WORKDIR must not exist. It receives the changed baseline, the changed ledger and report.md.
set -euo pipefail

[[ $# -eq 3 ]] || { echo "usage: $0 SITE BASELINE WORKDIR" >&2; exit 2; }
site=$1
baseline=$2
work=$3
[[ -e $work ]] && { echo "$work already exists" >&2; exit 1; }

mkdir -p "$work/baseline"
cp -r "$baseline/dump" "$baseline/BASELINE.json" "$work/baseline/"
[[ -e $baseline/site.diff ]] && cp "$baseline/site.diff" "$work/baseline/"
cp parity/deviations.toml "$work/deviations.toml"

python3 -I - "$work" <<'EOF'
import pathlib
import sys

work = pathlib.Path(sys.argv[1])
dump = work / "baseline" / "dump"


def change(path, old, new):
    file = dump / path
    text = file.read_text()
    if old not in text:
        sys.exit(f"{path}: {old!r} not found")
    file.write_text(text.replace(old, new, 1))


post = "content/_posts/2021/2021-08-08-webmentions.md.html"
# G1: a heading id
change(post, 'id="privacy-and-content-ownership"', 'id="privacy-and-content-ownership-x"')
# G2 attributes: the first target="blank" goes
change(post, ' target="blank"', "")
# G2 link targets: an href loses its trailing slash
change(post, 'href="https://wordpress.org/"', 'href="https://wordpress.org"')
# G3 and G4: text
change(post, "a forum", "a fórum")
# G5: a micro entry's excerpt
change("excerpt/_micro/notes/2026-04-08-finished.md.html", "<p>", "<p>Extra. ")
# G6, and D-003's check for the note: Jekyll's body changes, so the resolved excerpt no longer
# shows what it shows
change(
    "content/_digital_garden/coding/rust.md.html",
    '<pre class="highlight"><code>',
    '<pre class="highlight"><code>X',
)
# D-003 scope: Jekyll's excerpt of a listed note shows its links resolved, so the note no longer
# shows the deviation
note = "_digital_garden/projects/index.md.html"
(dump / "excerpt" / note).write_text((dump / "content" / note).read_text())

# D-003 scope in the ledger: a note with the deviation is dropped, and one without it is added
ledger = work / "deviations.toml"
text = ledger.read_text()
dropped = '  "_digital_garden/travel-tips/index.md",\n'
added = '  "_digital_garden/quotes.md",\n'
if dropped not in text:
    sys.exit("deviations.toml: D-003 does not list travel-tips/index.md")
ledger.write_text(text.replace(dropped, added, 1))
EOF

status=0
cargo run --quiet --locked -p parity -- markdown --site "$site" --baseline "$work/baseline" \
  --ledger "$work/deviations.toml" --report "$work/report.md" >/dev/null || status=$?
if [[ $status -ne 1 ]]; then
  echo "parity markdown exited with $status on the changed copies; expected 1" >&2
  exit 1
fi
echo "parity markdown failed, as it should; see $work/report.md" >&2
