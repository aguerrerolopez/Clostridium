import argparse
import yaml
import pickle
import numpy as np
from performance_tools import plot_importances
import os

maldi_path = "data/df_train_exp2.pkl"

# ============ Load data ===================
print("Loading data...")
with open(maldi_path, "rb") as handle:
    data = pickle.load(handle)

x = [x[:20000] for x in data["intensity"]]
x = np.vstack(x)

masses = [x[:20000] for x in data["mz"]]
masses = np.vstack(masses)

y = data["label"]

# ============ Preprocess data ===================
# Make bins bases on masses
for i in range(len(masses)):
    bins = np.arange(2000, 20000 + 1e-8, 3)
    mz_bins = bins[:-1] + np.diff(bins) / 2

    bins, _ = np.histogram(masses[i], bins, weights=SpectrumObj.intensity)
