# Fresh clone of `542c9a9`

A baseline built from a fresh clone of `filopoe` at `542c9a96`, compared with the reference
baseline built from the original checkout (`compare.txt`). Both builds pass every baseline check
on their own; they differ in two ways, both existing Jekyll behavior:

- **Page order.** Jekyll reads directories in filesystem order, so it lists pages in a different
  order in each checkout. The Lunr index and its content dump hold the same documents in a
  different order. `compare-builds.sh` checks such files entry by entry (`parity/same_entries.py`)
  and reports them as *reordered*; any changed entry would still fail.
- **Static-file dates.** `jekyll-sitemap` dates the 7 static files it lists (6 PDFs under
  `assets/pdf/` and `yandex_0bc73e3d94eb9bc8.html`) by their mtime, which in a clone is the
  checkout time. Those `<lastmod>` values differ, so `sitemap.xml` is reported as changed. This is
  recorded, not normalized.

Neither affects route parity: routes depend on paths, not on file order, contents or mtimes.
