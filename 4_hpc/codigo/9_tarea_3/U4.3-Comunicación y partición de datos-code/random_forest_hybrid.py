from mpi4py import MPI
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from joblib import Parallel, delayed
import numpy as np
import time
import os

# ========== MPI Setup ==========
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# ========== Data Preparation ==========
if rank == 0:
    X, y = make_regression(n_samples=80000, n_features=20, noise=0.1, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
else:
    X_train = X_test = y_train = y_test = None

# Broadcast data to all ranks
X_train = comm.bcast(X_train, root=0)
X_test = comm.bcast(X_test, root=0)
y_train = comm.bcast(y_train, root=0)
y_test = comm.bcast(y_test, root=0)

# ========== Parameter Grid ==========
param_grid = [
    {'n_estimators': 100, 'max_depth': None},
    {'n_estimators': 100, 'max_depth': 10},
    {'n_estimators': 200, 'max_depth': None},
    {'n_estimators': 200, 'max_depth': 20},
]

# Distribute params across ranks
params_per_proc = np.array_split(param_grid, size)
local_params = params_per_proc[rank]

# ========== Hybrid Parallel Function ==========
def train_evaluate(params):
    # Detect logical CPU cores (or limit via env)
    max_cores = min(2, os.cpu_count())  # limit to avoid oversubscription
    #model = RandomForestRegressor(n_jobs=max_cores, random_state=42, **params)
    model = RandomForestRegressor(n_jobs=1,random_state=42, **params)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    return {'params': params, 'mse': mse}

# ========== Time Measurement and Execution ==========
start_time = time.time()

# Parallel training on local parameter list using joblib
num_jobs = min(len(local_params), os.cpu_count() or 1)
#local_results = Parallel(n_jobs=num_jobs)(
local_results = Parallel(n_jobs=1)(
    delayed(train_evaluate)(p) for p in local_params
)

# Gather all results to root process
all_results = comm.gather(local_results, root=0)

# ========== Result Aggregation ==========
if rank == 0:
    all_results = [item for sublist in all_results for item in sublist]
    best = min(all_results, key=lambda x: x['mse'])
    duration = time.time() - start_time

    # Print all results
    for res in all_results:
        print(f"Params: {res['params']}, MSE: {res['mse']:.4f}")
    print(f"\n Best Params: {best['params']}, MSE: {best['mse']:.4f}")
    print(f"Time Taken (hybrid MPI + joblib, {size} ranks): {duration:.2f} sec")

