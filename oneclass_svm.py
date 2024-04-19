import os
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.model_selection import train_test_split
from preprocess import SpectrumObject


# Function to load and process data from a specific directory
def load_data(directory):
    data = []
    id = []
    for root, dirs, files in os.walk(directory):
        acqu_path = None
        fid_path = None
        for file in files:
            if file.endswith("acqu"):
                acqu_path = os.path.join(root, file)
            elif file.endswith("fid"):
                fid_path = os.path.join(root, file)

            if acqu_path and fid_path:
                spectrum = SpectrumObject.from_bruker(acqu_path, fid_path)
                if spectrum:
                    processed = spectrum.preprocess_as_R()
                    if processed is not None:
                        data.append(processed.intensity)
                        # the directory where the file is is the ID
                        id.append(root.split("/")[3])
                acqu_path, fid_path = None, None  # Reset paths after use
    return data, id


def train_and_predict(model, X_train, X_test, outlier_data, outlier_ids):
    print(f"Training {model.__class__.__name__}...")
    model.fit(X_train)

    print("Predicting on test set...")
    test_predictions = model.predict(X_test)
    test_inliers = np.sum(test_predictions == 1)
    print(f"Accuracy on test set: {test_inliers / len(test_predictions)}")

    print("Predicting on hungria data...")
    outlier_predictions = model.predict(outlier_data)
    outliers_detected = np.sum(outlier_predictions == -1)
    print("Outliers detected:", outliers_detected)

    # Retrieve IDs of detected outliers
    outlier_ids_detected = [
        id for pred, id in zip(outlier_predictions, outlier_ids) if pred == -1
    ]
    print("IDs of detected outliers:", outlier_ids_detected)


# Load the datasets
print("Loading autocdiff_data...")
autocdiff_data, _ = load_data("data/bruker_file/all_maldi")
X_train, X_test = train_test_split(autocdiff_data, test_size=0.2, random_state=42)

print("Loading hungria_data...")
hungria_data, hungria_ids = load_data("data/bruker_file/data_hungria")

# Convert lists to NumPy arrays
myXtrain = np.array(X_train)
myXtest = np.array(X_test)
outlierX = np.array(hungria_data)

# Initialize models
iso_forest = IsolationForest(n_estimators=100, contamination="auto", random_state=42)
one_class_svm = OneClassSVM(kernel="rbf", gamma="auto")
lof = LocalOutlierFactor(n_neighbors=20, novelty=True, contamination="auto")

# Train and predict using each model
train_and_predict(iso_forest, myXtrain, myXtest, outlierX, hungria_ids)
train_and_predict(one_class_svm, myXtrain, myXtest, outlierX, hungria_ids)
train_and_predict(lof, myXtrain, myXtest, outlierX, hungria_ids)
