import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from joblib import Parallel, delayed
import numpy as np

# Create dataset
X, y = make_regression(n_samples=80000, n_features=20, noise=0.1, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Parameter grid
param_grid = [
    {'n_estimators': 100, 'max_depth': None},
    {'n_estimators': 100, 'max_depth': 10},
    {'n_estimators': 200, 'max_depth': None},
    {'n_estimators': 200, 'max_depth': 20},
]

# Train/evaluate function with timing
def train_evaluate(params):
    start_time = time.time()
    model = RandomForestRegressor(n_jobs=16, random_state=42, **params)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    elapsed_time = time.time() - start_time
    return {'params': params, 'mse': mse, 'time': elapsed_time}

# Measure total execution time
total_start = time.time()
#results = Parallel(n_jobs=1,backend='threading',verbose=10)(
results = Parallel(backend='threading',verbose=10)(
    delayed(train_evaluate)(params) for params in param_grid
)
total_elapsed = time.time() - total_start

# Output results
print("\n=== Model Results ===")
for res in results:
    print(f"Params: {res['params']}, MSE: {res['mse']:.4f}, Time: {res['time']:.2f}s")

# Best model
best_result = min(results, key=lambda x: x['mse'])
print(f"\n Best Parameters: {best_result['params']}")
print(f" Best MSE: {best_result['mse']:.4f}")
print(f"  Total Parallel Time: {total_elapsed:.2f}s")

