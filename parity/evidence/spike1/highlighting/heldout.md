# Highlighting: held-out code

Output of `review.py` on the 109 files of `heldout-files.txt` (see `README.md`): code the
mapping was not tuned on. Rouge's side is what kramdown makes of each file as a fenced block.

## Before (syntect's own grammars, the first mapping)

| Language | Blocks | Characters | Same class | Same style |
|-|-:|-:|-:|-:|
| bash | 6 | 11339 | 66.6% | 85.5% |
| html | 65 | 49099 | 87.3% | 91.5% |
| javascript | 9 | 19186 | 86.3% | 91.2% |
| python | 6 | 24688 | 93.5% | 95.9% |
| r | 1 | 108 | 73.1% | 73.1% |
| rust | 3 | 10858 | 48.2% | 81.1% |
| toml | 14 | 11163 | 0.0% | 25.7% |
| yaml | 5 | 10371 | 56.9% | 73.9% |
| **lexed by Rouge** | | 136812 | **74.0%** | **84.2%** |
| lexed by Rouge, without TOML | | 125649 | 80.6% | 89.4% |

## After (bat's grammars through `two-face`, the revised mapping)

| Language | Blocks | Characters | Same class | Same style |
|-|-:|-:|-:|-:|
| bash | 6 | 11339 | 71.6% | 88.1% |
| html | 65 | 49099 | 98.0% | 98.2% |
| javascript | 9 | 19186 | 91.4% | 96.3% |
| python | 6 | 24688 | 96.8% | 97.8% |
| r | 1 | 108 | 73.1% | 73.1% |
| rust | 3 | 10858 | 49.5% | 81.1% |
| toml | 14 | 11163 | 99.4% | 99.6% |
| yaml | 5 | 10371 | 56.9% | 73.9% |
| **lexed by Rouge** | | 136812 | **87.8%** | **93.9%** |
| lexed by Rouge, without TOML | | 125649 | 86.8% | 93.4% |

Style disagreements (characters):

| Language | Rouge class | Folia class | Rouge style | Folia style | Characters |
|-|-|-|-|-|-:|
| yaml | `na` | `s` | #a6e22e | #d7d787 | 2643 |
| rust | `nf` | `nb` | #a6e22e bold | #f8f8f2 | 920 |
| bash | `nv` | `s2` | #f8f8f2 | #d7d787 | 751 |
| html | `err` | `na` | #f8f8f2 bg #403d3d | #a6e22e | 406 |
| rust | `nf` | `n` | #a6e22e bold | #f8f8f2 | 338 |
| rust | `nd` | `n` | #a6e22e bold | #f8f8f2 | 331 |
| python | `si` | `p` | #d7d787 | #f8f8f2 | 210 |
| html | `err` | `s` | #f8f8f2 bg #403d3d | #d7d787 | 172 |
| javascript | `nf` | `kd` | #a6e22e bold | #66d9ef bold | 144 |
| html | `na` | `` | #a6e22e | #f8f8f2 | 127 |
| bash | `nt` | `` | #f92672 | #f8f8f2 | 126 |
| javascript | `o` | `k` | #f92672 bold | #66d9ef bold | 124 |
| javascript | `nx` | `nf` | #f8f8f2 | #a6e22e bold | 116 |
| javascript | `nf` | `nb` | #a6e22e bold | #f8f8f2 | 93 |
| javascript | `nx` | `nc` | #f8f8f2 | #a6e22e bold | 90 |
| python | `s` | `se` | #d7d787 | #af87ff | 83 |
| bash | `s2` | `` | #d7d787 | #f8f8f2 | 82 |
| html | `nt` | `` | #f92672 | #f8f8f2 | 82 |
| rust | `nf` | `p` | #a6e22e bold | #f8f8f2 | 80 |
| python | `sa` | `k` | #d7d787 | #66d9ef bold | 79 |
| bash | `o` | `nb` | #f92672 bold | #f8f8f2 | 72 |
| rust | `nb` | `k` | #f8f8f2 | #66d9ef bold | 71 |
| bash | `o` | `p` | #f92672 bold | #f8f8f2 | 68 |
