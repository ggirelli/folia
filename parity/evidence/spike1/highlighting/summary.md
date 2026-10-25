# Highlighting: Rouge against Folia, by class and by rendered style

Output of `review.py` (see `README.md`) against baseline `d332352`, for the 19 documents with
highlighted code.

| Language | Blocks | Characters | Same class | Same style |
|-|-:|-:|-:|-:|
| bash | 17 | 1176 | 87.1% | 96.0% |
| email | 1 | 22 | 0.0% | 0.0% |
| html | 3 | 641 | 98.8% | 98.8% |
| javascript | 4 | 3148 | 96.5% | 97.6% |
| python | 12 | 5204 | 97.8% | 98.7% |
| r | 4 | 454 | 99.8% | 100.0% |
| rust | 1 | 104 | 100.0% | 100.0% |
| text | 4 | 15039 | 100.0% | 100.0% |
| toml | 2 | 624 | 99.5% | 99.8% |
| yaml | 1 | 71 | 84.5% | 88.7% |
| **lexed by Rouge** | | 11444 | **96.3%** | **98.0%** |
| lexed by Rouge, without TOML | | 10820 | 96.1% | 97.9% |

Style disagreements (characters):

| Language | Rouge class | Folia class | Rouge style | Folia style | Characters |
|-|-|-|-|-|-:|
| javascript | `nf` | `nb` | #a6e22e bold | #f8f8f2 | 33 |
| python | `nf` | `nb` | #a6e22e bold | #f8f8f2 | 31 |
| email | `nt` | `` | #f92672 | #f8f8f2 | 22 |
| python | `o` | `p` | #f92672 bold | #f8f8f2 | 11 |
| python | `err` | `p` | #f8f8f2 bg #403d3d | #f8f8f2 | 10 |
| javascript | `nc` | `nx` | #a6e22e bold | #f8f8f2 | 10 |
| bash | `nt` | `` | #f92672 | #f8f8f2 | 9 |
| bash | `s1` | `` | #d7d787 | #f8f8f2 | 9 |
| bash | `` | `s2` | #f8f8f2 | #d7d787 | 9 |
| javascript | `k` | `ow` | #66d9ef bold | #f92672 bold | 9 |
| html | `nf` | `kd` | #a6e22e bold | #66d9ef bold | 8 |
| yaml | `na` | `s` | #a6e22e | #d7d787 | 8 |
| bash | `o` | `` | #f92672 bold | #f8f8f2 | 8 |
| javascript | `o` | `k` | #f92672 bold | #66d9ef bold | 8 |
| javascript | `nb` | `nc` | #f8f8f2 | #a6e22e bold | 7 |
| javascript | `k` | `nf` | #66d9ef bold | #a6e22e bold | 5 |
| python | `p` | `nd` | #f8f8f2 | #a6e22e bold | 4 |
| bash | `` | `o` | #f8f8f2 | #f92672 bold | 4 |
| bash | `p` | `o` | #f8f8f2 | #f92672 bold | 4 |
| python | `n` | `nc` | #f8f8f2 | #a6e22e bold | 3 |
| python | `n` | `nd` | #f8f8f2 | #a6e22e bold | 3 |
| python | `mi` | `n` | #af87ff | #f8f8f2 | 3 |
| python | `sa` | `k` | #d7d787 | #66d9ef bold | 2 |
| bash | `nt` | `o` | #f92672 | #f92672 bold | 2 |
| javascript | `se` | `s2` | #af87ff | #d7d787 | 2 |
| bash | `nt` | `p` | #f92672 | #f8f8f2 | 1 |
| bash | `se` | `p` | #af87ff | #f8f8f2 | 1 |
| toml | `k` | `p` | #66d9ef bold | #f8f8f2 | 1 |

Classes each side emits that the stylesheet has no rule for (characters; they show the default):

- rouge: `n` 2915, `p` 947, `nx` 893, `pi` 2
- folia: `n` 2922, `p` 973, `nx` 904

Other rules touching highlighted code: `.highlight`, `.highlight table pre`, `code`, `pre code`,
`.highlight table td`
