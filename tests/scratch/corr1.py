import scipy as sp
import numpy as np
import pandas as pd

arrs = {
    "sleep_quality": [0, 0, 1, 2, 4, 0, 4],
    "cycle_phase": [
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        3,
        4,
        4,
        4,
        4,
        0,
        0,
        0,
        0,
    ],
    "diet_quality": [0, 0, 1, 0, 1, 0, 4],
    "stress_level": [0, 0, 0, 2, 4, 0, 0],
    "e": [2, 2, 3, 4, 0, 0, 0],
}

outcome = [1, 1, 1, 2, 2, 4, 4]

corrs = []


def smooth_arr(arr: list, alpha: float = 0.5) -> list:
    """smooth an array using exponetial moving average"""

    s = pd.Series(arr)
    smoothed = s.ewm(alpha=alpha).mean()

    return smoothed.to_list()


for k, arr in arrs.items():
    s_arr = smooth_arr(arr)
    corr = sp.stats.spearmanr(s_arr, outcome)  # ordinal data suits spearman
    corrs.append({k: corr.correlation})


dsc_corrs = sorted(corrs, key=lambda d: next(iter(d.values())), reverse=True)
asc_corrs = sorted(corrs, key=lambda d: next(iter(d.values())), reverse=False)


print(f"most pos corr: {dsc_corrs[0]}")
print(f"most neg corr: {asc_corrs[0]}")
