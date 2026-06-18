import numpy as np
from sklearn.datasets import make_circles
from sklearn.svm import SVC
import json
import os

def main():
    # 1. Generate concentric circles data
    # 100 samples in total (50 in inner circle, 50 in outer circle)
    # Add noise to make it realistic
    X, y = make_circles(n_samples=100, noise=0.1, factor=0.5, random_state=42)

    # 2. Fit RBF SVM
    # C=1.0, gamma='scale' as requested
    clf = SVC(kernel='rbf', C=1.0, gamma='scale')
    clf.fit(X, y)

    # 3. Identify the inner circle class
    # Calculate average distance from origin for each class to find the inner one
    distances = np.linalg.norm(X, axis=1)
    mean_dist_0 = np.mean(distances[y == 0])
    mean_dist_1 = np.mean(distances[y == 1])
    
    inner_class = 0 if mean_dist_0 < mean_dist_1 else 1
    print(f"Inner circle class detected: Class {inner_class}")

    # 4. Calculate decision scores (Z-axis values)
    scores = clf.decision_function(X)

    # Adjust signs so that the inner class always gets positive scores (forms a mountain)
    # and the outer class gets negative scores (stays low / forms a valley)
    # The decision boundary remains exactly at Z = 0
    inner_class_scores = scores[y == inner_class]
    sign_flipped = False
    if np.mean(inner_class_scores) < 0:
        scores = -scores
        sign_flipped = True
        print("Flipped decision scores sign to ensure inner circle rises (Z > 0).")
    else:
        print("Inner circle naturally has positive decision scores (Z > 0).")

    # Get support vector indices
    sv_indices = clf.support_.tolist()
    print(f"Number of support vectors: {len(sv_indices)}")

    # 5. Extract support vectors data
    support_vectors = clf.support_vectors_
    sv_labels = y[clf.support_]
    sv_scores = scores[clf.support_]

    # 6. Save structured data to JSON
    # We save points and some meta parameters
    output_data = {
        "meta": {
            "gamma": float(clf._gamma),
            "C": float(clf.C),
            "inner_class": int(inner_class),
            "sign_flipped": bool(sign_flipped),
            "num_support_vectors": int(len(sv_indices))
        },
        "points": []
    }

    for i in range(len(X)):
        output_data["points"].append({
            "id": int(i),
            "x": float(X[i, 0]),
            "y": float(X[i, 1]),
            "z": float(scores[i]),
            "label": int(y[i]),
            "is_support_vector": bool(i in sv_indices)
        })

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svm_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Data successfully generated and saved to {output_path}!")

if __name__ == "__main__":
    main()
