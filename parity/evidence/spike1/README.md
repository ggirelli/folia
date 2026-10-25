# Spike 1 evidence

Markdown compatibility (plan v5, §10) against the reference baseline `d332352`: `filopoe` commit
`d3323522`, which is `542c9a96` plus the D-002 source fix, built clean
(`parity/evidence/rebaseline-d332352/`). Folia renders all 190 Markdown documents of the site (79
posts, 39 micro entries, 54 garden notes, 18 pages) and their 172 excerpts, and `parity` compares
them with the HTML Jekyll's kramdown made, after the normalization the plan prescribes.

| File | Contents |
|-|-|
| `markdown.txt` | `just markdown d332352 --report …`: the gates, highlighting agreement, every document that differs or fails a gate |
| `negative.txt` | `just markdown-negative d332352`: the same check on a copy of the baseline changed once per gate, with D-003 narrowed and widened; each change is reported |
| `routes.txt` | `just routes d332352`: route parity (spike 2) at the new commit |
| `d002-compare.txt` | `just compare 542c9a9 542c9a9-d002`: Jekyll's output before and after the D-002 source fix, verified before committing it, and rechecked on a fresh build |
| `site-diff-check.txt` | how `parity` accepts a checkout for a baseline of uncommitted changes (`site.diff`), and refuses every other state |
| `highlighting/` | the highlighting review and the decision on Q12 |

## Results

`just markdown d332352` exits 0.

| Gate | Kind | Result |
|-|-|-|
| G1 heading IDs | hard | pass: 190 of 190 documents equal, in order |
| G2 link targets and attributes | hard | pass: 190 of 190 |
| G3 text | hard | pass: 190 of 190 |
| G4 structure | decision (95%) | met: 190 of 190 (100%) equal after normalization; 135 byte-identical |
| G5 excerpt values | hard | pass: 153 of 172 equal; the other 19 are the accepted deviation D-003, each passing its check |
| G6 code text | hard | pass: 77 of 77 blocks equal |
| G6 token classes | decision (about 90%) | met: 96.3% of the 11,444 characters Rouge lexes have Rouge's class (98.0% have Rouge's rendered style); Q12 decided |

- **D-002 withdrawn**: `eggs**!**` became `eggs<strong>!</strong>` in the source, committed in
  `filopoe` as `d3323522`. Jekyll's output is unchanged (`d002-compare.txt`: dumps byte for byte,
  the site after normalizing the feeds' build time), and Folia matches it with no deviation.
- **D-003 accepted**: Folia renders a garden excerpt with the body's wiki-link resolver
  (`folia_core::content::markdown::excerpt_html`). The ledger lists exactly the 19 notes with
  wiki-links. For each, the G5 difference counts as D-003 only if resolving changes the excerpt,
  Jekyll's excerpt differs from Jekyll's own body (the defect shows), and Folia's excerpt values
  equal those of Jekyll's body. A listed note that stops showing the deviation fails the run;
  every other note's excerpt must match Jekyll's exactly.
  The first check rendered excerpts without resolving and found 18 notes. The 19th,
  `indieweb/index.md`, shows the defect differently: Jekyll's excerpt reads `[[blogroll]]` as `[`,
  a reference link to `https://blogroll.org/`, and `]`.
- **Highlighting (Q12)**: syntect with bat's grammars (`two-face`), mapped to Rouge's Pygments
  classes, so the site keeps `_syntax.scss`; see `highlighting/README.md`.
- Route parity holds (`routes.txt`).

## How the checks were shown to work

`negative.txt` records it: a changed heading ID fails G1, a removed `target` and a changed `href`
fail G2, changed text fails G3 and G4, a changed micro excerpt fails G5, and a changed code block
fails G6 and also D-003's check for that note. On the ledger side, a D-003 note whose Jekyll
excerpt no longer shows the defect, a note dropped from D-003, and an unrelated note added to it
each fail the run.

`site-diff-check.txt` shows, on a scratch clone of `filopoe`, that a baseline built from
uncommitted changes is accepted only for a checkout of its commit with exactly the recorded
changes and no untracked files, and that a dirty baseline without `site.diff` is refused.

## Before the clean baseline

Spike 1 was first reviewed against `542c9a9-d002`, the same tree with the fix uncommitted (built
with `--allow-dirty`, which records `site.diff`). The bodies and excerpts in both baselines'
dumps are identical; committing moved one git date only, so every Markdown result is the same.
