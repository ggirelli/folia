# Spike 2 evidence

Route parity (plan v4, §10) against the reference baseline `542c9a9`, built from `filopoe`
commit `542c9a96`. `routes.txt` is the output of `just routes 542c9a9`.

| Check | Jekyll | Folia | Result |
|-|-|-|-|
| Authored outputs (source, URL, output) | 985 | 985 | identical |
| Classification of sources | 977 | 977 | identical |
| Generated outputs (URL, output) | 92 | 92 | identical |
| Redirect stubs (URL, output) | 26 | 26 | identical |
| Duplicate URLs or output files in Folia's table | | 0 | none |

The 985 authored outputs are the 977 sources plus the 8 further listing pages, which Jekyll
renders from `blog/index.html`. The 92 generated outputs are 51 feeds, 26 redirect stubs, 10
category archives, 2 source maps, the sitemap, `redirects.json` and the note graph.

## How the checks were shown to work

Each of these makes the run fail, naming exactly the difference:

| Change | Reported |
|-|-|
| one URL in a copy of the manifest changed in case | the post, only in Jekyll with the old URL and only in Folia with the new |
| `LICENSE*` removed from the configuration's `exclude` | the 3 `LICENSE-*.txt` files, only in Folia |
| `pages/about.md` added to `exclude` | the page missing, its classification, and its redirect stub `/blog/about` |
| the baseline of a different commit (`e872c37`) | refused: the checkout is at `542c9a96` |

The same run against a fresh clone of `542c9a96` also holds, so route parity does not depend on
the checkout (unlike the page order and static-file dates described in plan v4, §2.6).
