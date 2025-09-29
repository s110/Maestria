#!/usr/bin/env python3
import os, time, csv, sys, argparse
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from joblib import parallel_backend

# ===== Evitar sobre-suscripción BLAS =====
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

def approx_mem_bytes(n_samples, n_features, dtype_bytes=8):
    # X: n_samples * n_features, y: n_samples (int64 ~8B), factor ~2.5 por copias/overhead
    return int(2.5 * (n_samples * n_features * dtype_bytes + n_samples * 8))

def parse_args():
    ap = argparse.ArgumentParser(description="RF sintético paralelo para escalabilidad")
    ap.add_argument("--n_samples", type=int, default=200_000)
    ap.add_argument("--n_features", type=int, default=40)
    ap.add_argument("--n_informative", type=int, default=20)
    ap.add_argument("--n_redundant", type=int, default=10)
    ap.add_argument("--n_classes", type=int, default=2)
    ap.add_argument("--test_size", type=float, default=0.2)
    ap.add_argument("--n_estimators", type=int, default=400)
    ap.add_argument("--max_depth", type=int, default=20)
    ap.add_argument("--reps", type=int, default=3, help="repeticiones para promediar tiempos")
    ap.add_argument("--output", type=str, default="results_rf_synth.csv")
    return ap.parse_args()

def main():
    args = parse_args()

    # Paralelismo SOLO desde N_JOBS
    n_jobs = int(os.environ.get("N_JOBS", 1))

    # Chequeo de consistencia
    if args.n_informative + args.n_redundant > args.n_features:
        print("ERROR: n_informative + n_redundant debe ser <= n_features", file=sys.stderr)
        sys.exit(2)

    # Info de memoria aproximada (útil para no pasarte de RAM del nodo)
    memB = approx_mem_bytes(args.n_samples, args.n_features)
    print(f"[INFO] Aproximación de uso de memoria (dataset) ~ {memB/1e9:.2f} GB", file=sys.stderr)

    # ===== Dataset sintético =====
    X, y = make_classification(
        n_samples=args.n_samples,
        n_features=args.n_features,
        n_informative=args.n_informative,
        n_redundant=args.n_redundant,
        n_classes=args.n_classes,
        random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42
    )

    # ===== Modelo =====
    clf = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        n_jobs=n_jobs,
        random_state=42
    )

    fit_times, pred_times, accs = [], [], []

    for r in range(args.reps):
        # Entrenamiento
        t0 = time.perf_counter()
        with parallel_backend("loky", n_jobs=n_jobs):
            clf.fit(X_train, y_train)
        fit_t = time.perf_counter() - t0

        # Predicción
        t1 = time.perf_counter()
        y_pred = clf.predict(X_test)
        pred_t = time.perf_counter() - t1
        acc = accuracy_score(y_test, y_pred)

        fit_times.append(fit_t)
        pred_times.append(pred_t)
        accs.append(acc)

    fit_avg = float(np.mean(fit_times))
    pred_avg = float(np.mean(pred_times))
    acc_avg = float(np.mean(accs))

    # ===== Guardar resultados =====
    header = [
        "n_jobs","n_samples","n_features","n_informative","n_redundant","n_classes",
        "n_estimators","max_depth","test_size","reps",
        "fit_time_s_avg","pred_time_s_avg","accuracy_avg",
        "slurm_job_id","slurm_array_task_id"
    ]
    row = {
        "n_jobs": n_jobs,
        "n_samples": args.n_samples,
        "n_features": args.n_features,
        "n_informative": args.n_informative,
        "n_redundant": args.n_redundant,
        "n_classes": args.n_classes,
        "n_estimators": args.n_estimators,
        "max_depth": args.max_depth,
        "test_size": args.test_size,
        "reps": args.reps,
        "fit_time_s_avg": round(fit_avg, 4),
        "pred_time_s_avg": round(pred_avg, 4),
        "accuracy_avg": round(acc_avg, 4),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID",""),
        "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID",""),
    }

    write_header = not os.path.exists(args.output)
    with open(args.output,"a",newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        if write_header: w.writeheader()
        w.writerow(row)

    print(f"[OK] n_jobs={n_jobs} ns={args.n_samples} nf={args.n_features} "
          f"fit_avg={fit_avg:.3f}s pred_avg={pred_avg:.3f}s acc_avg={acc_avg:.4f}")

if __name__ == "__main__":
    main()

