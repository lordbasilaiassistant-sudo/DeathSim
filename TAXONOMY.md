# Taxonomy — the confidence tags

Every claim in this repository carries exactly one tag. The tag is a promise about *how much we actually know*, not how much we'd like to believe.

| Tag | Meaning | Bar to qualify |
|-----|---------|----------------|
| `[ESTABLISHED]` | Settled science. Reproducible, mechanistically understood, not seriously disputed. | Multiple independent sources; textbook-level consensus. |
| `[SUPPORTED]` | Good evidence, real consensus *direction*, but with open edges or limited data. | Peer-reviewed primary evidence; broadly accepted but not closed. |
| `[CONTESTED]` | Active scientific disagreement. Real data on more than one side. | At least one peer-reviewed result and a peer-reviewed rebuttal/limitation. |
| `[OPEN]` | A genuine unknown. The question is well-posed, has been investigated, and has no settled answer. | Documented research attempts that failed to resolve it. |
| `[SPECULATIVE]` | A hypothesis, framework, or belief presented *as such*. May be philosophically or culturally serious; is not empirically established. | Must be explicitly labeled. Never dressed as fact. |

## The rules

1. **No bare assertions.** A factual claim (`[ESTABLISHED]`, `[SUPPORTED]`, `[CONTESTED]`) needs a citation keyed to [`SOURCES.md`](./SOURCES.md).
2. **Unknowns get a reason.** An `[OPEN]` entry must explain *why* it's unresolved — what was tried, what the obstacle is — not just shrug.
3. **Speculation stays in its lane.** `[SPECULATIVE]` content is welcome in [`theories/`](./theories/) and must never migrate into [`facts/`](./facts/).
4. **The scientific default is not exempt.** "Consciousness ends with brain function" is the parsimonious, physicalist default — but as a claim about subjective experience it rests on inference, not direct measurement. Where that's true, it's tagged honestly, not promoted to `[ESTABLISHED]` by popularity.
5. **Correlation is not the surge.** Many death-neuroscience findings are small-N, confounded, or correlational. Tag to the *weakest* link in the claim, not the headline.
6. **Disagreement is data.** When sources conflict, we record the conflict (`[CONTESTED]`) rather than picking a winner.

## Why this matters

The failure mode of every "what happens when you die" piece is the smuggle: start with real biology (`[ESTABLISHED]`), end with metaphysics (`[SPECULATIVE]`), and never mark the seam. This taxonomy *is* the seam, made explicit on every line.
