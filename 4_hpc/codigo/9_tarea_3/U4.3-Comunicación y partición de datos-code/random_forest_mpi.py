from mpi4py import MPI
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import time

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Generate data on one process and broadcast
if rank == 0:
    X, y = make_regression(n_samples=10000, n_features=20, noise=0.1, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
else:
    X_train = X_test = y_train = y_test = None

# Broadcast data to all processes
X_train = comm.bcast(X_train, root=0)
X_test = comm.bcast(X_test, root=0)
y_train = comm.bcast(y_train, root=0)
y_test = comm.bcast(y_test, root=0)

# Parameter grid (split manually)
param_grid = [
    {'n_estimators': 100, 'max_depth': None},
    {'n_estimators': 100, 'max_depth': 10},
    {'n_estimators': 200, 'max_depth': None},
    {'n_estimators': 200, 'max_depth': 20},
]

# Split work among processes
params_per_proc = np.array_split(param_grid, size)
local_params = params_per_proc[rank]

def train_evaluate(params):
    model = RandomForestRegressor(n_jobs=-1, random_state=42, **params)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    return {'params': params, 'mse': mse}

# Measure performance
start_time = time.time()

# Each process trains on its subset
local_results = [train_evaluate(params) for params in local_params]

# Gather results at root process
all_results = comm.gather(local_results, root=0)

# At root: flatten results and find best
if rank == 0:
    all_results = [item for sublist in all_results for item in sublist]
    best = min(all_results, key=lambda x: x['mse'])
    duration = time.time() - start_time

    # Print results
    for res in all_results:
        print(f"Params: {res['params']}, MSE: {res['mse']:.4f}")
    print(f"\nBest: {best['params']} with MSE {best['mse']:.4f}")
    print(f"Time taken with MPI and {size} processes: {duration:.2f} seconds")

