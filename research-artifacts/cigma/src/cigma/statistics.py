"""Seeded bootstrap confidence intervals and paired randomization tests."""

from __future__ import annotations

from typing import Any

import numpy as np


def bootstrap_mean_ci(
    values: list[float] | np.ndarray,
    *,
    seed: int,
    resamples: int = 5000,
    confidence: float = 0.95,
) -> dict[str, float | int]:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        return {"mean": 0.0, "ci_low": 0.0, "ci_high": 0.0, "n": 0}
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, array.size, size=(resamples, array.size))
    bootstrap = np.mean(array[indexes], axis=1)
    alpha = (1.0 - confidence) / 2.0
    return {
        "mean": float(np.mean(array)),
        "ci_low": float(np.quantile(bootstrap, alpha)),
        "ci_high": float(np.quantile(bootstrap, 1.0 - alpha)),
        "n": int(array.size),
    }


def paired_comparison(
    treatment: list[float] | np.ndarray,
    baseline: list[float] | np.ndarray,
    *,
    seed: int,
    resamples: int = 5000,
    permutations: int = 10000,
) -> dict[str, Any]:
    """Paired bootstrap CI and two-sided sign-randomization p-value."""

    left = np.asarray(treatment, dtype=float)
    right = np.asarray(baseline, dtype=float)
    if left.shape != right.shape or left.ndim != 1:
        raise ValueError("paired samples must be equal-length vectors")
    if left.size == 0:
        return {
            "mean_difference": 0.0,
            "ci_low": 0.0,
            "ci_high": 0.0,
            "permutation_p": 1.0,
            "n": 0,
        }
    differences = left - right
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, left.size, size=(resamples, left.size))
    boot = np.mean(differences[indexes], axis=1)
    observed = abs(float(np.mean(differences)))
    signs = rng.choice(np.asarray([-1.0, 1.0]), size=(permutations, left.size))
    randomized = np.abs(np.mean(signs * differences, axis=1))
    p_value = (1.0 + float(np.sum(randomized >= observed - 1e-15))) / (
        permutations + 1.0
    )
    return {
        "mean_difference": float(np.mean(differences)),
        "ci_low": float(np.quantile(boot, 0.025)),
        "ci_high": float(np.quantile(boot, 0.975)),
        "permutation_p": float(p_value),
        "n": int(left.size),
    }
