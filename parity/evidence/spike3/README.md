# Spike 3 evidence

The reviewed record of spike 3 (plan v3, §10), kept as it was produced. D-001 was accepted on
2026-10-25 on the strength of these files, and the change was committed in `filopoe` as
`542c9a96`.

| File | Contents |
|-|-|
| `content.diff` | the complete rewrite of the 15 Markdown files, byte-identical to the commit's patch |
| `compare.txt` | `just compare e872c37 deliquified parity/spike3-expected.txt`: the whole-site and dump comparison |
| `d001.txt` | `just check-d001 e872c37 deliquified`: each expected difference is D-001 only |

The comparisons ran against the clean baseline at `e872c37` and a build of the uncommitted
rewrite. Only the feed-level `<updated>` (the build time) was normalized.
