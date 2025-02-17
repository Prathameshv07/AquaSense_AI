# home/utils.py
import numpy as np

def log_transform(x):
    return np.log1p(x)  # log(1 + x) to avoid log(0) issues