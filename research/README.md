# research/ — proving the unknowns, one at a time

The `facts/`, `unknowns/`, and `theories/` directories *catalog* what is known. This directory does the harder thing: takes a single `[CONTESTED]` or `[OPEN]` claim and **tests it** — with a simulation or a dataset — to the point where the confidence tag can honestly move.

Each experiment is self-contained, runs from the command line, validates against **real measured data** (not just internal consistency), and states plainly what it does and does **not** prove. The discipline is the same as the rest of the repo: a result is only as strong as the seam between mechanism and meaning, kept visible.

## Experiments

| # | Question | Claim tested | Result | Tag movement |
|---|----------|--------------|--------|--------------|
| [01](./01-energy-failure-gamma-surge/) | Does energy failure *alone* produce the dying-brain gamma surge? | end-of-life gamma surge `[CONTESTED]` | **Yes** — a biophysical network with no consciousness reproduces the surge, at the measured ~10 s timing, surge-before-silence, 6/6 seeds, validated vs. real [K⁺]ₒ data | *electrical surge* → `[SUPPORTED]` as mechanism; "surge = conscious NDE" stays `[SPECULATIVE]` |
| [02](./02-is-the-surge-rich-or-just-loud/) | Is the surge *rich* (could feel like something) or just *loud*? | "surge = vivid final experience" | **Leans loud-not-rich** — surge complexity ~0.4× waking (seizure-like: high power + synchrony, low differentiation), 4/4 seeds, two measures agree | "surge supports *rich* experience" → leans-against; experience itself stays `[OPEN]` |
| [03](./03-neural-net/) *(in progress)* | Can a net classify dying-brain states, and does the surge transfer to *real* seizure/anesthesia EEG? | "surge = seizure-like" as a real-data prediction | **Learnability validated** (77% on a held-out network, 85% surge recall); dataset sweep + real-EEG transfer test pending | TBD |

## The bar for an experiment here

1. **One claim.** Pick a single tagged statement from `facts/`/`unknowns/`. Don't boil the ocean.
2. **Validate first.** A ≤20-line test that the core mechanism even works before building anything (see Experiment 01's `validate_single_neuron.py`).
3. **Hit real numbers.** The model/analysis must reproduce values it was *not* tuned to, cited to primary literature. Matching a cartoon proves nothing.
4. **Name the seam.** State what is proven (usually: *a mechanism is sufficient*) and what is not (usually: *necessity*, and always: *anything about subjective experience*).
5. **Reproducible.** Exact commands, fixed seeds, committed outputs.

## Open experiment ideas (unclaimed)

- **02 — Hypothermia and the survival window.** Does cooling delay terminal depolarization in the model, quantitatively reproducing the clinical "nobody's dead until warm and dead" rule? Needs temperature-dependent metabolic rate. (Flagged by Experiment 01.)
- **Spatial spreading depolarization.** Extend Exp 01 to a 1-D/2-D cortex to reproduce the *propagating* terminal SD wave (Dreier 2018) and its measured ~mm/min speed.
- **Reversibility window.** At what point after arrest does restoring `ox` no longer rescue the network? Compare to the clinical 4–6 min figure and the BrainEx (Vrselja 2019) result that cellular function is restorable hours later.
