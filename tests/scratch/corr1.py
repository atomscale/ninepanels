import scipy as sp
import numpy as np
import pandas as pd

arrs = {
    "sleep_quality": [
        9,
        8,
        8,
        9,
        9,
        7,
        4,
        9,
        9,
        7,
        2,
        3,
        4,
        4,
        2,
        2,
        2,
        4,
        3,
        4,
        3,
        7,
        6,
        7,
        8,
        6,
        5,
        4,
        3,
        2,

    ],
}

outcome = [
    4,
    4,
    4,
    4,
    5,
    4,
    5,
    4,
    3,
    4,
    5,
    4,
    5,
    5,
    6,
    7,
    8,
    8,
    7,
    8,
    8,
    8,
    9,
    7,
    7,
    6,
    5,
    4,
    5,
    6,
]

corrs = []


def smooth_arr(arr: list, alpha: float = 0.5) -> list:
    """smooth an array using exponetial moving average"""

    s = pd.Series(arr)
    smoothed = s.ewm(alpha=alpha).mean()

    return smoothed.to_list()


for k, arr in arrs.items():
    s_arr = smooth_arr(arr, 0.1)
    corr = sp.stats.spearmanr(s_arr, outcome)  # ordinal data suits spearman
    corrs.append({k: corr.correlation})


dsc_corrs = sorted(corrs, key=lambda d: next(iter(d.values())), reverse=True)
asc_corrs = sorted(corrs, key=lambda d: next(iter(d.values())), reverse=False)


print(f"most pos corr: {dsc_corrs[0]}")
print(f"most neg corr: {asc_corrs[0]}")
