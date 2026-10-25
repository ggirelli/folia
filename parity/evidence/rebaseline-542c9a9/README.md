# Rebaseline at `542c9a9`

After D-001 was accepted, the spike 3 rewrite was committed in `filopoe` as `542c9a96`, and the
reference baseline was rebuilt there (`just baseline-verify 542c9a9`, all checks passing).

Committing the 15 files moved the git dates of the 13 that have no front matter date. That is
the only difference from the build of the uncommitted rewrite that spike 3 verified:

| File | Contents |
|-|-|
| `compare.txt` | `just compare deliquified 542c9a9`: 13 meta dumps and 21 site files differ |
| `dates.txt` | `just check-date-shift deliquified 542c9a9`: each of those differences is a changed date |
| `BASELINE.json` | what the new baseline was built from; `site.path`, an absolute local path when recorded, is shown relative to the Folia checkout |

Together with the spike 3 evidence, this shows the new baseline is the clean `e872c37` baseline
plus D-001, plus 4 last-modified dates moving to the commit time (2026-10-25T10:35:27+01:00).
