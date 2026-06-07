# Experiment 03 — Neural-net classifier of dying-brain states *(IN PROGRESS)*

**Status: scaffolding + learnability validated. Dataset sweep and full training not yet complete.**

## Goal (chosen direction: "Classifier + real-EEG transfer test")

Train a neural net to classify brain-state regime — **baseline / surge / silence** — from the multichannel signal, then (Stage 2) test whether a net trained on the *simulated* surge labels **real human EEG** (seizure / anesthesia / waking) consistently with Exp 02's "surge = seizure-like" finding. That would turn Exp 02 into a falsifiable prediction against real data.

## What's done

- **Learnability validated** ([`validate_nn.py`](./validate_nn.py)): a small MLP trained on 3 simulated networks and tested on a 4th it never saw reaches **77% accuracy (chance 56%)**, with **baseline perfectly separable and 85% surge recall**. → the dying-state is learnable and generalizes across runs. Greenlit.
- **Dataset generator** ([`build_dataset.py`](./build_dataset.py)): sweeps the simulator (drive × seed) into labeled 192 ms windows tagged by run-id for grouped train/test splits. (A run was interrupted; re-run to regenerate `results/dataset.npz` — it is gitignored as a large regenerable artifact.)

## What's next (not yet done)

1. Finish the dataset sweep → `dataset.npz`.
2. Train the 3-class classifier with grouped CV, **reusing the training/eval harness from the local `Torsion` project** (`Torsion/experiments/00-synthetic-regime/run.py` — Adam + F1 early-stopping + checkpointing + class-imbalance weighting), adapting the binary head to 3-class softmax. Optionally race a vanilla 1D-CNN against Torsion's `MobiusConv1d` (built for regime-seam detection).
3. **Stage 2 — real-EEG transfer test.** Needs `mne` (free pip install, not yet installed). Domain-gap caveat: model outputs *point-neuron membrane V*, real EEG is *scalp field potential* — so compare **derived state-features** (band-power ratios, complexity, synchrony) defined identically for both, not raw waveforms.

## The seam (unchanged)

A classifier is a *pattern* detector. It can test whether the surge **resembles** known unconscious states; it **cannot** detect experience. A positive transfer result strengthens the mechanistic story; it still says nothing about whether anything is felt. That stays `[OPEN]`.
