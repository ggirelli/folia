# Rebaseline at `d332352`

The D-002 source fix (`eggs**!**` → `eggs<strong>!</strong>` in
`_posts/2016/2016-09-04-chocolate-salame.md`) was verified on an uncommitted tree, as baseline
`542c9a9-d002` (`parity/evidence/spike1/d002-compare.txt`), then committed alone in `filopoe` as
`d3323522`, on top of `542c9a96`. The reference baseline was rebuilt there
(`just baseline-verify d332352`: a second run and a build without the dump plugin agree, every
built file is in the manifest, and no date comes from an mtime).

Committing the file moved the post's git date, since it has no front matter date. That is the
only difference from the verified build:

| File | Contents |
|-|-|
| `compare.txt` | `just compare 542c9a9-d002 d332352`: the post's meta dump, its page, the `dessert` tag feed and the sitemap differ |
| `dates.txt` | `just check-date-shift 542c9a9-d002 d332352`: each of those differences is the one changed date |
| `BASELINE.json` | what the new baseline was built from; `site.path`, an absolute local path when recorded, is shown relative to the Folia checkout |

So `d332352` is the `542c9a9` baseline with the post's last-modified date moved to the commit
time (2026-10-25T15:43:44+01:00): its body, excerpt and every other output are unchanged.
`just check-date-shift 542c9a9 d332352` reports the same single date.

`check_date_shift.py` now leaves a baseline's `site.diff` out of the files it compares, as it
already did `BASELINE.json`: both record how a baseline was built, and only a build of
uncommitted changes has a `site.diff`, so the check could not otherwise pass for one.
