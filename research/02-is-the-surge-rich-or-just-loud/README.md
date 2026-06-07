# Experiment 02 — Is the gamma surge *rich* (could feel like something) or just *loud*?

**Status: result obtained, 4/4 seeds, two independent complexity measures agree.**
**Tag impact:** the surge being a substrate for *rich* conscious experience moves toward `[SPECULATIVE]`-leaning-against; the question of experience itself stays `[OPEN]`.

---

## The question

Experiment 01 showed energy failure reproduces the dying-brain gamma surge. But a surge of **power** is not a surge of **experience**. In living brains, the *level* of consciousness tracks **neural complexity** (Lempel-Ziv / PCI — the basis of the clinical "consciousness meter"): **high** in waking, REM, and on psychedelics; **low** in anesthesia, coma, and **seizure** (hypersynchrony). So:

> Is the surge a *differentiated, rich* state (the kind that could support a vivid final experience), or a *uniform, hypersynchronous* discharge (seizure-like — the wrong kind of activity for rich experience)?

## Method

Re-ran the Exp-01 network recording per-neuron membrane V (125 channels @ 250 Hz). In three **equal-length** windows — baseline (waking-like) / surge / silence — computed:
- **Complexity:** multichannel Lempel-Ziv (Schartner et al. 2015 method), plus a **gzip/LZ77 cross-check**, each normalized by a shuffled surrogate. Low = ordered/uniform; high = differentiated.
- **Synchrony** (variance of the mean field ÷ mean of per-channel variance) and **power**.

Equal-length windows matter: LZ complexity grows with sequence length, so a fair comparison requires it. Code: [`exp02_complexity.py`](./exp02_complexity.py).

## Result (mean over 4 seeds)

| window | complexity (LZc) | synchrony | power |
|---|---|---|---|
| baseline (waking-like) | **0.91** (rich) | 0.04 | ~110 |
| **surge** | **0.39** (low) | **0.35** (~8×) | ~370 (~3.5×) |
| silence | 0.25 *(unreliable — see note)* | 0.04 | ~0 |

**The surge is loud and hypersynchronous but informationally impoverished** — complexity drops to ~0.4× the waking baseline, while power rises ~3.5× and synchrony ~8×. Both complexity measures (LZ76 and gzip) agree, every seed (`surge/baseline` LZc ratio 0.40–0.45). See [`results/figure_exp02.png`](./results/figure_exp02.png) — the per-neuron heatmap shows baseline *speckle* (diverse) → surge *stripes* (everyone firing together) → silence *flat*.

By the standard consciousness-complexity correlate, that profile — **high power + high synchrony + low differentiation** — is the signature of the **unconscious** (anesthesia, coma, seizure), not of rich experience. The model's surge looks more like a **terminal hypersynchronous discharge** than a vivid final thought.

## What this does and does NOT prove

- **Leans:** the surge is the *wrong kind of activity* to support a rich, world-building final experience. It pushes **against** the romantic "vivid life-review flash" reading rather than feeding it.
- **Does NOT prove the lights are off.** Complexity (LZc/PCI) is a *correlate* of consciousness level, not a measure of experience. This is a **minimal point-neuron model**; real cortex in those seconds could be more structured. And real NDE survivors *do* report vivid experiences. So the question of whether anything is *felt* stays `[OPEN]` — see [`../../unknowns/consciousness-at-death.md`](../../unknowns/consciousness-at-death.md).

## Limitations / honest notes

- **Silence complexity is unreliable** — a flat (depolarization-blocked) signal binarized by its own mean is dominated by numerical noise, so its LZc varies wildly across seeds (0.05–0.58). The robust, meaningful comparison is **baseline vs surge**; silence is reported for completeness only.
- Same minimal-model caveats as Exp 01 (point neurons, single well-mixed ECS, PING gamma).
- LZc bounds the *capacity* of the activity to support rich experience; it cannot detect presence/absence of feeling.

## Reproduce

```bash
cd research/02-is-the-surge-rich-or-just-loud
for s in 1 2 3 4; do py exp02_complexity.py --seed $s; done   # writes results/exp02_summary.jsonl
py plot_exp02.py                                              # writes results/figure_exp02.png
```
Requires Python 3 + numpy + scipy + matplotlib. ~1–2 min per seed (LZ76 is the slow step).

---

**Cited methods/data:** Schartner et al. 2015 (LZc); Casali et al. 2013 (PCI); Lempel & Ziv 1976; Borjigin2013 — see [`../../SOURCES.md`](../../SOURCES.md).
