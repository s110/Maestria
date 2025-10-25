from mpi4py import MPI
import numpy as np
from collections import Counter
import sys

# Only rank 0 will import these for visualization
if MPI.COMM_WORLD.Get_rank() == 0:
    from sklearn.datasets import make_classification
    from sklearn.decomposition import PCA
    import csv
    import os
#    import matplotlib.pyplot as plt


def euclidean_distance(a, b):
    return np.sqrt(np.sum((a - b) ** 2, axis=1))


# MPI setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Parameters
k = 3
num_features = 10
test_size = 200

# Get dataset size from CLI or use default
if len(sys.argv) >= 2:
    train_size = int(sys.argv[1])
else:
    train_size = 1000

# Generate synthetic classification data (only on rank 0)
if rank == 0:
    X, y = make_classification(
        n_samples=train_size + test_size,
        n_features=num_features,
        n_informative=6,  # Important: informative features
        n_redundant=0,
        n_classes=3,
        random_state=42,
    )
    X_train = X[:train_size]
    y_train = y[:train_size]
    X_test = X[train_size:]
    y_test = y[train_size:]
else:
    X_train = y_train = X_test = y_test = None

# Broadcast test data and labels
X_test = comm.bcast(X_test, root=0)
y_test = comm.bcast(y_test, root=0)

# Divide training data
local_train_size = train_size // size
local_X = np.empty((local_train_size, num_features), dtype="float64")
local_y = np.empty(local_train_size, dtype="int")

# Timing
t_start = MPI.Wtime()
comm.Scatter(X_train, local_X, root=0)
comm.Scatter(y_train, local_y, root=0)
t_dist = MPI.Wtime()

# Local distance computation
local_predictions = []
for x in X_test:
    dists = euclidean_distance(local_X, x)
    k_indices = dists.argsort()[:k]
    k_labels = local_y[k_indices]
    local_predictions.append((dists[k_indices], k_labels))
t_comp = MPI.Wtime()

# Gather all partial predictions
all_dists = comm.gather(local_predictions, root=0)
t_gather = MPI.Wtime()

# Final prediction on rank 0
if rank == 0:
    final_preds = []
    for i in range(test_size):
        all_neighbors = []
        for proc_preds in all_dists:
            all_neighbors.extend(zip(proc_preds[i][0], proc_preds[i][1]))
        all_neighbors.sort(key=lambda x: x[0])
        top_k = [label for _, label in all_neighbors[:k]]
        final_pred = Counter(top_k).most_common(1)[0][0]
        final_preds.append(final_pred)

    final_preds = np.array(final_preds)
    accuracy = np.mean(final_preds == y_test)

    total_time = t_gather - t_start
    dist_time = t_dist - t_start
    comp_time = t_comp - t_dist
    gather_time = t_gather - t_comp

    print(f"[Process Count: {size}] Dataset Size: {train_size}")
    print(f"Total Time       : {total_time:.4f} sec")
    print(f"  - Distribution : {dist_time:.4f} sec")
    print(f"  - Computation  : {comp_time:.4f} sec")
    print(f"  - Gathering    : {gather_time:.4f} sec")
    print(f"Accuracy         : {accuracy:.4f}")
    print(f"Etiquetas reales : {y_test}")
    print(f"Predicciones     : {final_preds}")

    results_file = "logs/knn_mpi_results.csv"
    file_exists = os.path.isfile(results_file)
    with open(results_file, "a", newline="") as csvfile:
        fieldnames = [
            "process_count",
            "train_size",
            "total_time",
            "distribution_time",
            "computation_time",
            "gathering_time",
            "accuracy",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "process_count": size,
                "train_size": train_size,
                "total_time": f"{total_time:.4f}",
                "distribution_time": f"{dist_time:.4f}",
                "computation_time": f"{comp_time:.4f}",
                "gathering_time": f"{gather_time:.4f}",
                "accuracy": f"{accuracy:.4f}",
            }
        )

    # Visualize results with PCA
    pca = PCA(n_components=2)
    X_test_2D = pca.fit_transform(X_test)
"""
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 4))

    # Ground truth
    plt.subplot(1, 2, 1)
    plt.scatter(X_test_2D[:, 0], X_test_2D[:, 1], c=y_test, cmap='viridis', edgecolor='k')
    plt.title("Etiquetas reales")
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.colorbar()

    # Predictions
    plt.subplot(1, 2, 2)
    plt.scatter(X_test_2D[:, 0], X_test_2D[:, 1], c=final_preds, cmap='viridis', edgecolor='k')
    plt.title("Predicciones KNN")
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.colorbar()

    plt.tight_layout()
    plt.show()
"""
