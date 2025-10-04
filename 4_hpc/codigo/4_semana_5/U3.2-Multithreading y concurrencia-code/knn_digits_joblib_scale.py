
# knn_digits_joblib_scale.py
import argparse
import os
import time
from collections import Counter

import numpy as np
from joblib import Parallel, delayed, parallel_backend
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

# Data expansion utilities
def expand_samples(X, y, factor: int, jitter: float = 0.0, seed: int = 42):
    # Duplicate dataset 'factor' times (exact copies). If jitter>0, add Gaussian noise per feature.
    if factor <= 1:
        return X, y
    rng = np.random.RandomState(seed)
    X_big = np.repeat(X, factor, axis=0)
    y_big = np.repeat(y, factor, axis=0)
    if jitter > 0.0:
        X_big = X_big + rng.normal(0.0, jitter, size=X_big.shape)
    return X_big, y_big

def expand_features(X, feature_mult: int, mode: str = "repeat", seed: int = 42):
    # Increase dimensionality by an integer factor: repeat or random linear mix
    if feature_mult <= 1:
        return X
    n, d = X.shape
    if mode == "repeat":
        return np.tile(X, (1, feature_mult))
    elif mode == "mix":
        rng = np.random.RandomState(seed)
        W = rng.normal(0, 1, size=(d, (feature_mult - 1) * d))
        X_new = X @ W
        return np.concatenate([X, X_new], axis=1)
    else:
        raise ValueError("feat-mode must be 'repeat' or 'mix'")

# KNN helpers
def euclidean_distance_batch(X_train: np.ndarray, x: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum((X_train - x) ** 2, axis=1))

def predict_one(x: np.ndarray, X_train: np.ndarray, y_train: np.ndarray, k: int) -> int:
    dists = euclidean_distance_batch(X_train, x)
    k_indices = np.argpartition(dists, k)[:k]
    k_labels = y_train[k_indices]
    cnt = Counter(k_labels)
    return sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

def knn_predict_joblib(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, k: int,
                       n_jobs: int, backend: str) -> np.ndarray:
    with parallel_backend(backend=backend, n_jobs=n_jobs):
        preds = Parallel()(delayed(predict_one)(x, X_train, y_train, k) for x in X_test)
    return np.array(preds, dtype=y_train.dtype)

def estimate_flops(n_train: int, n_test: int, d: int, k: int):
    flops_dist = n_test * n_train * (3.0 * d)
    flops_select = n_test * (5.0 * n_train)
    return flops_dist, flops_select, flops_dist + flops_select

def main():
    ap = argparse.ArgumentParser(description="KNN (joblib) with data scaling knobs and FLOPs.")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--test-size", type=float, default=0.25)
    ap.add_argument("--jobs", type=int, default=-1, help="-1: all cores")
    ap.add_argument("--backend", type=str, default="loky", choices=["loky", "threading"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--feat-mult", type=int, default=1)
    ap.add_argument("--feat-mode", type=str, default="repeat", choices=["repeat", "mix"])
    ap.add_argument("--mult-train", type=int, default=1)
    ap.add_argument("--mult-test", type=int, default=1)
    ap.add_argument("--jitter", type=float, default=0.0)

    args = ap.parse_args()

    digits = load_digits()
    X = digits.data.astype(np.float64) / 16.0
    y = digits.target.astype(np.int32)

    X = expand_features(X, feature_mult=args.feat_mult, mode=args.feat_mode, seed=args.seed)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed, stratify=y
    )

    X_train, y_train = expand_samples(X_train, y_train, factor=args.mult_train, jitter=args.jitter, seed=args.seed)
    X_test,  y_test  = expand_samples(X_test,  y_test,  factor=args.mult_test,  jitter=args.jitter, seed=args.seed)

    n_train, d = X_train.shape
    n_test = X_test.shape[0]

    _ = euclidean_distance_batch(X_train[:min(8, n_train)], X_test[0])

    start = time.perf_counter()
    y_pred = knn_predict_joblib(X_train, y_train, X_test, k=args.k, n_jobs=args.jobs, backend=args.backend)
    end = time.perf_counter()

    acc = float(np.mean(y_pred == y_test))
    fdist, fsel, ftotal = estimate_flops(n_train, n_test, d, args.k)

    print("\n[Joblib KNN]")
    print(f"[Backend           ]: {args.backend}")
    print(f"[n_jobs            ]: {args.jobs}")
    print(f"[Train Samples     ]: {n_train}")
    print(f"[Test Samples      ]: {n_test}")
    print(f"[Features          ]: {d}")
    print(f"[k                 ]: {args.k}")
    print(f"[Accuracy          ]: {acc:.4f}")
    print(f"[Tiempo Total      ]: {end - start:.4f} sec")
    print(f"[FLOPs (Distance)  ]: {fdist:.2e}")
    print(f"[FLOPs (Select)    ]: {fsel:.2e}")
    print(f"[Total FLOPs       ]: {ftotal:.2e}\n")

if __name__ == "__main__":
    main()
