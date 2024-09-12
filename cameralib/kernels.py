import numpy as np
from functools import lru_cache

@lru_cache(maxsize=5)
def circle_kernel(d):
    mid = (d - 1) / 2
    distances = np.indices((d, d)) - np.array([mid, mid])[:, None, None]
    return ((np.linalg.norm(distances, axis=0) - mid) <= 0).astype(int)