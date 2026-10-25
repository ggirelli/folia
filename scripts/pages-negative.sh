#!/usr/bin/env bash
# Shows that the page parity check fails when it should (plan v6, §12.2 step 1): it copies a
# baseline's manifest and site, changes the copy of each file Folia builds where the check looks,
# then runs `parity pages` on the copy. It must exit 1, and report each change.
#
#   scripts/pages-negative.sh SITE BASELINE WORKDIR
#
# WORKDIR must not exist. It receives the changed baseline and report.txt.
set -euo pipefail

[[ $# -eq 3 ]] || { echo "usage: $0 SITE BASELINE WORKDIR" >&2; exit 2; }
site=$1
baseline=$2
work=$3
[[ -e $work ]] && { echo "$work already exists" >&2; exit 1; }

mkdir -p "$work/baseline/dump"
cp "$baseline/BASELINE.json" "$work/baseline/"
[[ -e $baseline/site.diff ]] && cp "$baseline/site.diff" "$work/baseline/"
cp "$baseline/dump/manifest.jsonl" "$work/baseline/dump/"
cp -r "$baseline/site" "$work/baseline/site"

python3 -I - "$work/baseline/site" <<'EOF'
import pathlib
import sys

site = pathlib.Path(sys.argv[1])


def change(path, old, new):
    file = site / path
    text = file.read_text()
    if old not in text:
        sys.exit(f"{path}: {old!r} not found")
    file.write_text(text.replace(old, new, 1))


# Fingerprint, outside the main content: a category count and the footer's year
change("about.html", "journal (16)", "journal (15)")
change("about.html", "2012-2026", "2012-2025")
# Fingerprint and main content: the last-updated date
change("about.html", "Jan 4, 2026", "Jan 5, 2026")
# Main content only: a template comment
change("about.html", "<!-- Post Content -->", "<!-- Content -->")
# The redirect stub, and a static file
change("blog/about.html", "Redirecting&hellip;</h1>", "Redirecting...</h1>")
change("CNAME", "ggirelli.info", "ggirelli.example")
EOF

status=0
cargo run --quiet --locked -p parity -- pages --site "$site" --baseline "$work/baseline" \
  --config parity/filopoe.toml >"$work/report.txt" || status=$?
if [[ $status -ne 1 ]]; then
  echo "parity pages exited with $status on the changed copy; expected 1" >&2
  exit 1
fi
for expected in \
  'FAILS: about.html: fingerprint; 2 differences' \
  'FAILS: about.html: div.main-content equal after normalization' \
  'FAILS: redirect stubs and static files byte-identical (1 stubs, 775 static files); 2 differences' \
  'blog/about.html: differs' \
  'CNAME: differs'; do
  grep -qF "$expected" "$work/report.txt" || {
    echo "the report lacks: $expected (see $work/report.txt)" >&2
    exit 1
  }
done
echo "parity pages failed, as it should; see $work/report.txt" >&2
