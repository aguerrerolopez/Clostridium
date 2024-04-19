import pandas as pd
import os
import numpy as np

# Read data from path
pathinitial = "data/maldi_processed/initial"
# Walk the path
listOfFiles = list()
id_list = list()
label_list = list()
for dirpath, dirnames, filenames in os.walk(pathinitial):
    for file in filenames:
        if file.endswith(".csv"):
            listOfFiles.append(os.path.join(dirpath, file))
            id_list.append(listOfFiles[-1].split("/")[-2].split("-")[1])
            label_list.append(listOfFiles[-1].split("/")[-2].split("-")[0])

# Second path
pathsecond = "data/maldi_processed/test/test"
# Walk the path
for dirpath, dirnames, filenames in os.walk(pathsecond):
    for file in filenames:
        if file.endswith(".csv"):
            listOfFiles.append(os.path.join(dirpath, file))
            id_list.append(file.split("_")[0])
            label_list.append(np.nan)


# Read todas_labels.xlsx
pathlabels = "data/todas_labels.xlsx"
df_labels = pd.read_excel(pathlabels, header=None)


# For all the nans in label_list, look they id in the df_labels to retrieve real label
for i in range(len(label_list)):
    if label_list[i] is np.nan:
        # Check if exists in df_labels
        if int(id_list[i]) in df_labels[1].values:
            label_list[i] = df_labels[df_labels[1] == int(id_list[i])][2].values[0]
        else:
            print("Error: id not found in df_labels")

# check if there is any nan in label_list
if np.nan in label_list:
    print("Error: there is nan in label_list")


import pandas as pd

columns = ["id", "label", "mz", "intensity"]
data_list = []

for i, file in enumerate(listOfFiles):
    print("Loading bar: ", i + 1, "/", len(listOfFiles))
    df_temp = pd.read_csv(file, header=None)
    id = id_list[i]
    label = label_list[i]
    mz = np.array(df_temp[0][1:].values).astype(float)
    intensity = np.array(df_temp[1][1:].values).astype(float)

    data_list.append({"id": id, "label": label, "mz": mz, "intensity": intensity})

df_final = pd.DataFrame(data_list, columns=columns)

# Let split the df_final in train and test.
# To do so, group by labels and then sample 80% of each label for train and 20% for test
df_train = pd.DataFrame(columns=columns)
df_test = pd.DataFrame(columns=columns)

# Split the df_final by label and id
# For each label, i want 80% of the ids for train and 20% for test

for label in df_final["label"].unique():
    # get the ids for each label
    ids = df_final[df_final["label"] == label]["id"].unique()
    # get the 80% of ids for train
    ids_train = np.random.choice(ids, int(0.8 * len(ids)), replace=False)
    # get the 20% of ids for test
    ids_test = np.setdiff1d(ids, ids_train)

    # Now, concat the ids_train and ids_test to df_train and df_test
    df_train = pd.concat([df_train, df_final[df_final["id"].isin(ids_train)]])
    df_test = pd.concat([df_test, df_final[df_final["id"].isin(ids_test)]])

# If a label is only in test and not in train, move it to train

# # Get the labels that are only in test
# labels_only_test = np.setdiff1d(df_test["label"].unique(), df_train["label"].unique())

# # For each label in labels_only_test, move it to train
# for label in labels_only_test:
#     # add it to the df_train
#     df_train = pd.concat([df_train, df_test[df_test["label"] == label]])
#     # remove it from df_test
#     df_test = df_test[df_test["label"] != label]


# Group by id, then print the value coutns of labels
print(df_train.groupby("id").first().reset_index()["label"].value_counts())
print(df_test.groupby("id").first().reset_index()["label"].value_counts())

# Check where is the sample with ID: 20413731
print(df_train[df_train["id"] == "20413731"])
print(df_test[df_test["id"] == "20413731"])


# save df_train and df_test
df_train.to_pickle("data/df_train_exp2.pkl")
df_test.to_pickle("data/df_test_exp2.pkl")

# save them too as csv
df_train.to_csv("data/df_train_exp2.csv", index=False)
df_test.to_csv("data/df_test_exp2.csv", index=False)
