# archivo: mlp_joblib_np_timed.py
import argparse, os, json, time, joblib, numpy as np
from joblib import Parallel, delayed
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score


# ---------------- utilidades I/O ----------------
def load_csv_numpy(path, label_col=None):
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    if label_col is None:
        return data  # solo features
    X = np.delete(data, label_col, axis=1)
    y = data[:, label_col].astype(int)
    return X, y


def make_synthetic_data(n_samples, n_features, classes, seed=42):
    rng = np.random.default_rng(seed)
    per_class = n_samples // classes
    Xs, ys = [], []
    for c in range(classes):
        mean = rng.normal(0, 5, size=(n_features,))
        cov = np.eye(n_features)
        Xc = rng.multivariate_normal(mean, cov, size=per_class)
        yc = np.full(per_class, c, dtype=int)
        Xs.append(Xc)
        ys.append(yc)
    X = np.vstack(Xs)[:n_samples]
    y = np.concatenate(ys)[:n_samples]
    return X.astype("float32"), y


# ---------------- experimento por semilla (cronometrado) ----------------
def train_one_seed_timed(X, y, seed, param_grid, max_iter, inner_n_jobs):
    t_total0 = time.perf_counter()

    # split
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y
    )

    pipe = make_pipeline(
        StandardScaler(),
        MLPClassifier(max_iter=max_iter, random_state=seed, early_stopping=True),
    )

    # GridSearch (cronometrado)
    t_gs0 = time.perf_counter()
    gs = GridSearchCV(
        pipe,
        param_grid=param_grid,
        scoring="accuracy",
        cv=3,
        n_jobs=inner_n_jobs,  # controla el paralelismo interno
        verbose=0,
        refit=True,
    )
    gs.fit(Xtr, ytr)
    t_gs1 = time.perf_counter()

    # validación holdout
    acc = accuracy_score(yte, gs.best_estimator_.predict(Xte))

    t_total1 = time.perf_counter()
    return {
        "seed": seed,
        "acc": float(acc),
        "best_params": gs.best_params_,
        "fit_time_gs_sec": t_gs1 - t_gs0,
        "fit_time_total_seed_sec": t_total1 - t_total0,
        "best_estimator": gs.best_estimator_,
    }


# ---------------- comandos ----------------
def cmd_train(args):
    # datos
    if args.train_csv:
        X, y = load_csv_numpy(args.train_csv, label_col=-1)
    else:
        X, y = make_synthetic_data(
            args.n_samples, args.n_features, args.classes, seed=args.seed
        )

    # rejilla
    hls_configs = [
        tuple(map(int, s.split(","))) for s in args.hidden_layer_sizes.split(";") if s
    ]
    param_grid = {
        "mlpclassifier__hidden_layer_sizes": hls_configs,
        "mlpclassifier__learning_rate_init": [1e-3, 5e-4],
        "mlpclassifier__alpha": [1e-4, 1e-5],
    }

    print(
        f"[INFO] SLURM_CPUS_PER_TASK={os.getenv('SLURM_CPUS_PER_TASK')}, n_jobs={args.n_jobs}, backend={args.backend}, inner_n_jobs={args.inner_n_jobs}"
    )
    t_all0 = time.perf_counter()

    # paralelo externo con joblib
    results = Parallel(n_jobs=args.n_jobs, backend=args.backend, verbose=10)(
        delayed(train_one_seed_timed)(
            X,
            y,
            seed=s,
            param_grid=param_grid,
            max_iter=args.max_iter,
            inner_n_jobs=args.inner_n_jobs,
        )
        for s in range(args.seeds)
    )

    t_all1 = time.perf_counter()

    # elegir mejor
    results_sorted = sorted(results, key=lambda r: r["acc"], reverse=True)
    best = results_sorted[0]
    joblib.dump(best["best_estimator"], args.out_model)

    # imprimir resumen
    print("\n====== RESUMEN ENTRENAMIENTO ======")
    for r in results_sorted:
        print(
            f"seed={r['seed']:>2d} | acc={r['acc']:.4f} | "
            f"gs_time={r['fit_time_gs_sec']:.3f}s | seed_total={r['fit_time_total_seed_sec']:.3f}s | params={r['best_params']}"
        )
    print("-----------------------------------")
    print(
        f"MEJOR: seed={best['seed']}  acc={best['acc']:.4f}  params={best['best_params']}"
    )
    print(f"TIEMPO TOTAL ENTRENAMIENTO (pared): {t_all1 - t_all0:.3f} s")
    print(f"[OK] Modelo guardado en {args.out_model}")

    # guardar métricas si se pide
    if args.metrics_json:
        payload = {
            "summary": {
                "n_jobs": args.n_jobs,
                "backend": args.backend,
                "inner_n_jobs": args.inner_n_jobs,
                "total_train_wall_sec": t_all1 - t_all0,
                "best_seed": best["seed"],
                "best_acc": best["acc"],
                "best_params": best["best_params"],
            },
            "per_seed": [
                {
                    k: (float(v) if isinstance(v, (np.floating,)) else v)
                    for k, v in r.items()
                    if k != "best_estimator"
                }
                for r in results_sorted
            ],
        }
        with open(args.metrics_json, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"[OK] Métricas JSON: {args.metrics_json}")

    if args.metrics_csv:
        # CSV simple por semilla
        with open(args.metrics_csv, "w") as f:
            f.write("seed,acc,fit_time_gs_sec,fit_time_total_seed_sec,params\n")
            for r in results_sorted:
                f.write(
                    f'{r["seed"]},{r["acc"]:.6f},{r["fit_time_gs_sec"]:.6f},{r["fit_time_total_seed_sec"]:.6f},"{r["best_params"]}"\n'
                )
        print(f"[OK] Métricas CSV: {args.metrics_csv}")


def cmd_predict(args):
    t0 = time.perf_counter()
    model = joblib.load(args.model)
    t1 = time.perf_counter()

    X = load_csv_numpy(args.test_csv)  # solo features
    # repetir predicción para promediar tiempo si se desea
    t_pred0 = time.perf_counter()
    for _ in range(args.repeat_predict):
        preds = model.predict(X)
    t_pred1 = time.perf_counter()

    np.savetxt(args.out_preds, preds, fmt="%d", delimiter=",")

    print("====== RESUMEN PREDICCIÓN ======")
    print(f"Carga modelo: {(t1 - t0):.6f} s")
    print(
        f"Predicción x{args.repeat_predict}: {(t_pred1 - t_pred0):.6f} s "
        f"(promedio {(t_pred1 - t_pred0) / args.repeat_predict:.6f} s/ejec)"
    )
    print(f"[OK] Predicciones -> {args.out_preds}")


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser(
        description="MLP con joblib (paralelo) + tiempos de ejecución"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    tr = sub.add_parser("train")
    tr.add_argument(
        "--train-csv",
        default=None,
        help="CSV entrenamiento (última col = etiqueta). Si se omite, usa sintético.",
    )
    tr.add_argument("--n-samples", type=int, default=60000)
    tr.add_argument("--n-features", type=int, default=64)
    tr.add_argument("--classes", type=int, default=4)
    tr.add_argument("--max-iter", type=int, default=200)
    tr.add_argument("--seeds", type=int, default=4)
    tr.add_argument("--seed", type=int, default=42)
    tr.add_argument("--n-jobs", type=int, default=int(os.getenv("N_JOBS", "4")))
    tr.add_argument(
        "--backend", choices=["loky", "threading", "multiprocessing"], default="loky"
    )
    tr.add_argument(
        "--inner-n-jobs",
        type=int,
        default=1,
        help="n_jobs interno de GridSearchCV (recomendado 1 si paralelizas por semillas).",
    )
    tr.add_argument("--out-model", default="mlp_model.joblib")
    tr.add_argument("--metrics-json", default=None)
    tr.add_argument("--metrics-csv", default=None)
    tr.add_argument(
        "--hidden-layer-sizes",
        type=str,
        default="256;128;512,256,128",
        help="Tuplas de tamaños de capas ocultas para MLPClassifier, separadas por ';'. Ejemplo: '256;128;512,256,128'",
    )

    pr = sub.add_parser("predict")
    pr.add_argument("--model", required=True)
    pr.add_argument("--test-csv", required=True, help="CSV solo con features")
    pr.add_argument("--out-preds", default="preds.csv")
    pr.add_argument(
        "--repeat-predict",
        type=int,
        default=1,
        help="Repite predict() para medir tiempo promedio.",
    )

    args = ap.parse_args()
    if args.cmd == "train":
        cmd_train(args)
    else:
        cmd_predict(args)


if __name__ == "__main__":
    main()
