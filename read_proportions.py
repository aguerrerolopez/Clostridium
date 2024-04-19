import pandas


# Read df_test_exp2.pkl and df_train_exp2.pkl and extract which ids are in the test set
df_test = pandas.read_pickle("data/df_test_exp2.pkl")
df_train = pandas.read_pickle("data/df_train_exp2.pkl")

# Group by id, get first label and reset index
df_test = df_test.groupby("id").first().reset_index()
df_train = df_train.groupby("id").first().reset_index()

# Get value counts of labels for each df
print(df_test["label"].value_counts())
print(df_train["label"].value_counts())
