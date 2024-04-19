import pandas as pd
import os
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from preprocess import SpectrumObject


def read_data(dir, train=False):

    # read train data
    train_data_acqu_path = []
    train_data_fid_path = []
    train_label = []
    train_id = []

    # Each "acqu" file contains the data for a single sample, a "fid" file contains the metadata
    # Walk through the train directory and read the data
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith("acqu"):
                if train:
                    id = root.split("/")[5].split("-")[1]
                    train_id.append(id)
                    label = root.split("/")[4]
                    train_label.append(label)
                else:
                    id = [str(i) for i in root.split("/") if len(i) > 6][0]
                    train_id.append(id)
                train_data_acqu_path.append(os.path.join(root, file))
            if file.endswith("fid"):
                train_data_fid_path.append(os.path.join(root, file))

    # For each acqu and fid file, create a SpectrumObject and store it in a list
    train_data = []

    for i in range(len(train_data_acqu_path)):
        try:
            spectrum = SpectrumObject.from_bruker(
                train_data_acqu_path[i], train_data_fid_path[i], preprocess=True
            )
        except UnboundLocalError:
            train_data.append(None)
            continue
        train_data.append(spectrum)

    # Remove from train id and trian label the samples where train data is None
    if train:
        train_id = [
            train_id[i] for i in range(len(train_data)) if train_data[i] is not None
        ]
        train_label = [
            train_label[i] for i in range(len(train_data)) if train_data[i] is not None
        ]
    train_data = [
        train_data[i] for i in range(len(train_data)) if train_data[i] is not None
    ]

    if train:
        assert len(train_data) == len(train_id) == len(train_label)

    return train_data, train_id, train_label


path = "data/bruker_file/all_maldi"

# train directory
train_dir = os.path.join(path, "initial")

# test directory
test_dir = os.path.join(path, "test")

# outbreak directory
outbreak_dir = os.path.join(path, "outbreak")

train_data, train_id, train_label = read_data(train_dir, train=True)
test_data, test_id, test_label = read_data(test_dir)
outbreak_data, outbreak_id, outbreak_label = read_data(outbreak_dir)

# RandomForestClassifier
from sklearn.ensemble import RandomForestClassifier

# Use the intensitys as values
X = np.vstack([data.intensity for data in train_data])
y = train_label

# Categorize the labels
from sklearn import preprocessing

le = preprocessing.LabelEncoder()
le.fit(y)
train_label = le.transform(y)


# %%
# Lets do the full pipeline 10 times to check the variability of the results
balanced_acc = []
folds = 3
for f in range(folds):
    print("Fold: ", f)

    # We have to split the data into training and test sets by train_id which is the identifier unique of each sample (They are repeated)
    unique_train_id = np.unique(train_id)
    # Split the unique_train_id into training and test sets
    x_train_id, x_test_id = train_test_split(
        unique_train_id, test_size=0.2, random_state=0
    )

    # Create the training and test sets
    X_train = np.vstack(
        [X[i] for i in range(len(train_id)) if train_id[i] in x_train_id]
    )
    y_train = np.array(
        [train_label[i] for i in range(len(train_id)) if train_id[i] in x_train_id]
    )
    X_test = np.vstack([X[i] for i in range(len(train_id)) if train_id[i] in x_test_id])
    y_test = np.array(
        [train_label[i] for i in range(len(train_id)) if train_id[i] in x_test_id]
    )

    # Get the value counts of labels per set
    print(pd.Series(y_train).value_counts())
    print(pd.Series(y_test).value_counts())

    # Now translate them to real labels
    print(pd.Series(le.inverse_transform(y_train)).value_counts())
    print(pd.Series(le.inverse_transform(y_test)).value_counts())

    # Oversample with SMOTE
    from imblearn.over_sampling import SMOTE

    sm = SMOTE(random_state=0)
    X_train, y_train = sm.fit_resample(X_train, y_train)

    # GridSearch a RF
    from sklearn.model_selection import GridSearchCV

    # Create the parameter grid based on the results of random search
    param_grid = {
        "bootstrap": [True, False],
        "max_depth": [70, 80, 90],
        "max_features": [50, 1000, 3000, None],
        "min_samples_leaf": [3, 5],
        "min_samples_split": [8, 12],
        "n_estimators": [100],
    }

    # Create a based model
    rf = RandomForestClassifier()

    # Instantiate the grid search model
    grid_search = GridSearchCV(
        estimator=rf, param_grid=param_grid, cv=3, n_jobs=-1, verbose=1
    )

    # Fit the grid search to the data
    grid_search.fit(X_train, y_train)

    # Train the Classifier to take the training features and learn how they relate to the training y (the species)
    grid_search.best_estimator_.fit(X_train, y_train)

    # Apply the Classifier we trained to the test data (which, remember, it has never seen before)
    y_pred = grid_search.best_estimator_.predict(X_test)

    # Balanced accuracy
    from sklearn.metrics import balanced_accuracy_score

    bac = balanced_accuracy_score(y_test, y_pred)
    balanced_acc.append(bac)

    print("Best params: ", grid_search.best_params_)

    print("Balanced accuracy: ", bac)


# Print mean and std of balanced accuracy
print("Mean balanced accuracy: ", np.mean(balanced_acc))
print("Std balanced accuracy: ", np.std(balanced_acc))

# Classification report of last fold
from sklearn.metrics import classification_report

print(classification_report(y_test, y_pred, target_names=le.classes_))

# %%
