# Spike 1: highlighting review

The review plan v5 asks for (§10, spike 1, G6) before the highlighter is chosen (Q12): does the
site's `_sass/_syntax.scss` style what Folia emits as it styles Rouge's output, which tokens
differ, and is the 90% decision rule met. Measured against baseline `d332352`.

**Decision (Q12): syntect, with bat's grammars (`two-face`) and the mapping to Rouge's Pygments
classes; the site keeps `_syntax.scss`.** By class, 96.3% of the characters Rouge lexes agree
with Rouge, against the unchanged 90% rule (83.2% before this round); by rendered style, 98.0%
(89.5% before). The screenshots of all 19 documents show no regression of note.

| File | Contents |
|-|-|
| `summary.md` | agreement by class and by rendered style, per language; every style disagreement; classes without a rule |
| `screenshots/NN-*.png` | Rouge (left) and Folia (right), block by block, under the site's compiled `main.css`, for each of the 19 documents |
| `heldout.md` | the same measurement on 109 files of code the mapping was not tuned on, before and after this round |
| `heldout-files.txt`, `heldout.rb` | that held-out corpus, and the script that makes its Rouge and Folia inputs |
| `review.py` | the measurement and the review pages (unchanged since the first review) |
| `render.rs` | the throwaway renderer that gives `review.py` Folia's HTML |
| `before/*.png` | the first review's screenshots: syntect's own grammars and the first mapping |

## Method

Unchanged from the first review. The 19 Markdown documents with highlighted code (49 blocks; the
20th document Jekyll highlights, `blog/microblog.html`, is an HTML listing, not Markdown) are
rendered by Folia and compared with Jekyll's body HTML from the baseline dump. For every
non-whitespace character in a `div.highlight` block, `review.py` takes the class of the innermost
span on each side, and the style the baseline's compiled `assets/css/main.css` gives that class:
color, weight, slant and background, the only properties `_syntax.scss` sets on tokens. A class
with no `.highlight .x` rule gets the `.highlight` default (`#f8f8f2` on `#1b1d1e`).

The denominator is every character of every block Rouge lexes, as in `parity markdown`'s G6
report, which gives the same 96.3%: all 11,444 characters, TOML and the one e-mail block
included. Plain-text blocks are reported but not counted, as before.

## What changed

Two changes, both in `folia_core::content::markdown::highlight`:

1. **Grammars.** syntect's bundled set has no TOML. `two-face` 0.5.2 ships bat 0.26.1's
   grammars (TOML and e-mail among them) as a syntect dump built for `fancy-regex`, loaded the
   same way; Folia now uses that set for every language, and no longer enables syntect's own
   (`default-syntaxes`). Using bat's set only for the languages syntect lacks measured 88.2% by
   class; using it throughout, 89.9%, before any mapping change.
2. **Mapping.** Each new rule copies a rule of Rouge 4.7.0's lexer for that language, rather than
   a token seen in the fixtures:
   - Python: any call is `nf` (`name(`, builtins included), a capitalized call `nc`; `def`,
     `class` and `lambda` are `k`; `self` is a plain name; `in` is `ow`; `->` is an operator.
   - HTML: tag delimiters (`<`, `</`, `>`, `/>`) take the tag's class `nt`, `=` the attribute's
     class `na`, comments `c`; the content of `<script>` follows the JavaScript rules, as Rouge
     hands it to its JavaScript lexer.
   - Bash: options (`-a`, `--colocate`) are `nt`, assigned names `nv`, and `|` is unmarked.
   - TOML: keys are names, `=` an operator, table brackets keywords.

   E-mail has no rule: the site's one `email` block is a bare address, which Rouge colors only
   because its e-mail lexer reads any line as a header name.

## Results

| | Before | After |
|-|-:|-:|
| By class, all languages Rouge lexes (11,444 characters): the G6 rule | 83.2% | **96.3%** |
| By rendered style | 89.5% | **98.0%** |
| Held-out code (136,812 characters), by class | 74.0% | 87.8% |
| Held-out code, by rendered style | 84.2% | 93.9% |

By language on the fixtures, by class: Python 97.8%, JavaScript 96.5%, HTML 98.8%, TOML 99.5%,
Bash 87.1%, YAML 84.5%, R 99.8%, Rust 100%, e-mail 0% (22 characters).

The held-out corpus (`heldout.md`) checks for fitting: Rouge's own demo for each of the 8
languages, Folia's Python, shell scripts, TOML and YAML files, two Folia Rust files, `filopoe`'s
hand-written JavaScript and its layouts and includes (HTML). Every language improved or stayed
the same, so the rules generalize. It also shows where the mapping is still weak, all in
languages the site barely uses today: YAML keys (Rouge `na` green, Folia `s` yellow), Rust calls,
attributes and doc comments, and Bash variables inside strings. They do not affect the site as it
is; a post with much YAML or Rust would look less like Rouge, though consistently styled.

## Stylesheet

Every class Folia emits has a rule in `_syntax.scss`, except `n`, `nx` and `p`, which Rouge's
output also leaves to the `.highlight` default. The other rules that touch highlighted code
(`.highlight`, `pre code`, `code`, `.highlight table pre|td`) apply to the wrapper markup, which
is identical on both sides. A matching class is therefore a matching style, and the review
compares styles, not only names; the screenshots confirm it.

## Visual review

All 19 documents were looked at, block by block. "Differences" counts the characters styled
differently.

| # | Document | Blocks | Differences | What differs |
|-:|-|-|-:|-|
| 01 | `_digital_garden/coding/python/cli.md` | 3 python | 2 | `()` after `@app.callback` green bold, as part of the decorator |
| 02 | `_digital_garden/coding/python/type_checking.md` | 2 python | 8 | the decorator's `(fun)`, and the type variables `DC` and `R`, green bold |
| 03 | `_digital_garden/coding/rust.md` | 1 rust | 0 | none |
| 04 | `_digital_garden/coding/versioning/jujutsu.md` | bash, toml | 12 | Bash: `<address>`'s `<`/`>` pink as redirections, and the `--colocate` after it plain; TOML identical |
| 05 | `_micro/notes/2025-08-21-watch.md` | 2 bash | 4 | `;` pink |
| 06 | `pages/changelog.md` | 1 text | 0 | none |
| 07 | `pages/privacy.md` | 1 text | 0 | none |
| 08 | `pages/security-policy.md` | email, text | 22 | the address plain instead of pink |
| 09 | `_posts/2020/2020-01-26-multirange.md` | 7 python | 57 | magic-method names after `def` (`__init__`, `__next__`, `__iter__`, `__len__`) plain instead of green bold; where the source mangled `__x__` into `**x**`, Rouge marks `**` as an error (grey background) and Folia leaves it plain; a few operators plain |
| 10 | `_posts/2021/2021-08-08-webmentions.md` | 3 html | 8 | `function` in the script blue instead of green |
| 11 | `_posts/2021/2021-08-17-speed-up-ggplot.md` | 4 r | 0 | none |
| 12 | `_posts/2021/2021-08-21-6-steps-personal-static-website.md` | 1 yaml | 8 | the two keys yellow instead of green |
| 13 | `_posts/2022/2022-08-27-ubuntu-ruby-jekyll.md` | 7 bash | 13 | in an error message pasted as Bash: `'require'` plain instead of yellow, `(`/`)` plain instead of pink, `--` bold |
| 14 | `_posts/2022/2022-08-28-ubuntu-grub-zfs.md` | 2 bash | 6 | GRUB's `=(`, `)` and `=` plain instead of pink |
| 15 | `_posts/2023/2023-04-21-ubuntu_lunar_lobster.md` | 2 bash | 0 | none |
| 16 | `_posts/2023/2023-07-14-steam-4k-big-ui.md` | 2 bash | 2 | a placeholder's `<`/`>` pink |
| 17 | `_posts/2025/2025-08-06-ruby-openssl.md` | 1 bash | 10 | `openssl@3` yellow and a `\` plain |
| 18 | `_posts/2025/2025-10-21-python-import-times.md` | text, toml | 1 | the `.` in a table name plain instead of blue |
| 19 | `_posts/2026/2026-07-17-background-change.md` | 4 javascript | 74 | builtin methods (`JSON.parse`, `Math.floor`, `setTimeout`, `console.warn`) plain instead of green bold; `=>` blue instead of pink; `new` pink instead of blue; `Image` plain and `Promise` green bold |

The first review's main regression, TOML without any highlighting, is gone, and so are the Python
builtin calls, operators and HTML tag delimiters it listed. What remains is a few characters per
block, visible side by side, not alone. The largest groups are Python's magic-method names after
`def` (09) and JavaScript's builtin methods (19).

## Alternatives, reassessed

Only as far as the decision needs; none was built.

- **Generate a stylesheet for syntect's scopes.** Still no help: no emitted class lacks a rule,
  and the differences are token boundaries and kinds.
- **tree-sitter** (`arborium`). Avoids `bincode`, but brings C builds and a mapping written and
  tuned from scratch, to beat 96.3%. Not worth a spike now.
- **Highlighting in the browser** (highlight.js, Prism). Adds JavaScript to every page with code,
  changes the markup and classes, and needs a new stylesheet. Not justified.
- **giallo**: still ruled out (EUPL-1.2, Oniguruma).

## `bincode` and RUSTSEC-2025-0141

- **Path:** `bincode 1.3.3` ← `syntect 5.3.0` ← `folia-core` (directly, and through `two-face`).
  syntect's `parsing` feature enables `dump-create`, and `two-face` enables `dump-load`; both pull
  in `bincode`, so no feature set of syntect 5.3.0, its latest release, avoids it. `two-face`
  itself depends on `serde` and `syntect` only, and adds no other crate.
- **Advisory** (RustSec database, fetched 2026-10-24): informational, `unmaintained`; "the
  bincode team has taken the decision to cease development permanently" after a harassment
  campaign, and "considers version 1.3.3 a complete version". No vulnerability is reported and
  no patched version exists. Without the exception, `cargo deny` reports this advisory and no
  other.
- **Use:** syntect decodes with it only the syntax set compiled into the binary
  (`include_bytes!` in `two-face`), at build time, never outside input.
- **Exception:** `deny.toml` ignores RUSTSEC-2025-0141 by ID only, and `[bans]` denies `bincode`
  to every crate but syntect (`wrappers`), so nothing else can bring it in under the exception.
  Approved with Q12; to revisit when syntect drops bincode 1, or if an advisory reports a
  vulnerability.

## Reproducing

```sh
# Folia's HTML for the 19 documents: make a scratch crate from render.rs, with
#   folia-core = { path = "<folia>/crates/core" }
# and an empty [workspace] table, then
hl-dump ../filopoe FOLIA_HTML $(cat DOCS)
# DOCS: the documents with highlighted code, from the baseline dump
(cd ../folia-baselines/d332352/dump/content && grep -rl 'class="highlight"' . \
  | sed 's|^\./||; s|\.html$||' | grep -v '^blog/' | sort) > DOCS
python3 -I parity/evidence/spike1/highlighting/review.py \
  ../folia-baselines/d332352 FOLIA_HTML DOCS OUT
# Screenshots of OUT/NN.html, reduced to 64 colors
google-chrome --headless=new --hide-scrollbars --window-size=1500,9000 \
  --screenshot=NN.png file://$PWD/OUT/NN.html
magick NN.png -trim +repage -colors 64 PNG8:NN.png

# Held-out code: ROOT holds the folia and filopoe checkouts
(cd ../filopoe && bundle exec ruby ../folia/parity/evidence/spike1/highlighting/heldout.rb \
  ../folia/parity/evidence/spike1/highlighting/heldout-files.txt .. HELDOUT) > IDS
cp ../folia-baselines/d332352/site/assets/css/main.css HELDOUT/base/site/assets/css/  # mkdir first
hl-dump HELDOUT/site HELDOUT/raw $(sed 's/$/.md/' IDS)   # then rename raw/ID.md.html to folia/ID.html
python3 -I parity/evidence/spike1/highlighting/review.py HELDOUT/base HELDOUT/folia IDS OUT
```

`heldout-files.txt` names Folia files as of the commit that added it; those that have changed
since give slightly different counts.
