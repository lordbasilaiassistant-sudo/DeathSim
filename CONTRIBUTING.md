# Contributing to DeathSim

This is a knowledge ledger, not an essay collection. The contribution bar is about **epistemic honesty**, not prose.

## The single hard rule

> **Cite the evidence, or mark it as a hypothesis.** Every claim gets exactly one confidence tag from [`TAXONOMY.md`](./TAXONOMY.md). A factual claim needs a real source keyed to [`SOURCES.md`](./SOURCES.md).

A claim with no source and no `[OPEN]`/`[SPECULATIVE]` tag is a defect. We will treat it as a bug, not a style nit.

## What good contributions look like

- **New facts** → `facts/`, tagged `[ESTABLISHED]`/`[SUPPORTED]`/`[CONTESTED]`, with a primary source. Forensic, clinical, and neurophysiological data welcome.
- **New unknowns** → `unknowns/`, tagged `[OPEN]`, *with a reason it's unresolved* — what was tried, what the obstacle is. "We don't know" alone is not enough; explain the gap.
- **New theories** → `theories/`, tagged `[SPECULATIVE]`, honestly placed relative to evidence. Do not dress speculation as fact, and do not strawman a framework you disagree with.
- **Corrections** → especially welcome. If a claim is mistagged (e.g., something `[SUPPORTED]` that should be `[CONTESTED]`), open an issue or PR. **Disagreement between sources is recorded, not resolved** — promote to `[CONTESTED]` and cite both sides.

## What gets rejected

- The **smuggle**: starting in `[ESTABLISHED]` biology and sliding into `[SPECULATIVE]` metaphysics without marking the seam.
- **Overclaiming** an unknown in *either* direction ("science proved consciousness just switches off" / "science can't disprove survival, so it survives"). Both misuse the evidence.
- Sources that aren't real or aren't checkable. If you can't link it, you can't tag the claim as fact.
- Advocacy. This repo doesn't comfort and doesn't debunk. It records.

## Tone

Plain, exact, unsentimental. This is a subject people care about deeply; the respect we show is *accuracy*, not reassurance.

## Process

1. Read [`TAXONOMY.md`](./TAXONOMY.md) first — it governs everything.
2. Make your change with inline tags and citations.
3. Add any new source to [`SOURCES.md`](./SOURCES.md) with a real locator.
4. Open a PR describing which tag each new/changed claim carries and why.
