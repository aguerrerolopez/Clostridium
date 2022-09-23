import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ir = pd.read_csv('data/IR/PeakMatrix_IR.csv')
maldi = pd.read_csv('data/MALDI/PeakMatrix_MALDI.csv')

ids = pd.read_excel('data/CepasClostridiumAlex.xlsx')
ids['Cepa'] = ids['Cepa'].astype('str')
ids_str = [str(ide) for ide in ids['Cepa'].tolist()]
ids_str[ids_str.index('79305')] = '79308'
ids_str.sort()

# ======================= Organize MALDI DATA =======================
mid = maldi.keys().to_list()[1:]

midc = [m.split(' ')[-1] for m in mid]
midcc = [m.split('_')[0] for m in midc]

midr = []
midr_indexes = []
midn = []
midn_indexes = []
c = 0
for m in midcc:
    if len(m)<=6:
        midr.append(m)
        midr_indexes.append(c)
    else:
        midn.append(m) 
        midn_indexes.append(c)
    c+=1

midnf = []
for m in midn:
    sp = m.split('-')
    if len(sp[0])>3:
        midnf.append(sp[0])
    else:
        midnf.append(sp[1])


maldi_ids = midr + midnf
maldi_indexes = midr_indexes + midn_indexes
aux = pd.DataFrame(data=np.array([maldi_indexes, maldi_ids]).T)
aux.sort_values(1, inplace=True)
maldi_indexes_final = [int(i) for i in aux.iloc[:,0].values]

# ======================= Organize IR DATA =======================
irid = ir.keys().to_list()[1:]

iridc = []
for i in irid:
    if i.split('_')[1]=='difficile':
        iridc.append(i.split('_')[2])
    else:
        iridc.append(i.split('_')[1])

iridr = []
iridr_indexes = []
iridn = []
iridn_indexes = []
c=0
for i in iridc:
    if len(i)<=6:
        iridr.append(i)
        iridr_indexes.append(c)
    else:
        iridn.append(i)
        iridn_indexes.append(c)
    c+=1

iridnf = [i.split('-')[0] for i in iridn]

ir_ids = iridr + iridnf
ir_indexes = iridr_indexes + iridn_indexes
ir_ids[ir_ids.index('11-022')]= '11-023'
ir_ids[ir_ids.index('79305')]= '79308'

aux2 = pd.DataFrame(data=np.array([ir_indexes, ir_ids]).T)
aux2.sort_values(1, inplace=True)
ir_indexes_final = [int(i) for i in aux2.iloc[:,0].values]

# ======================= Check that data matches =======================
print("Every index in IR matches in MALDIs?")
print(all(aux.iloc[:,1].values == aux2.iloc[:,1].values))


# ======================= Matching final data =======================
maldi_df = maldi.iloc[:, 1:].iloc[:, maldi_indexes_final].T
ir_df = ir.iloc[:, 1:].iloc[:, ir_indexes_final].T

labels = []
for z in range(len(aux[1])):
    if aux[1].values[z]=='79308':
        label = ids['Ribotipo'][ids['Cepa']=='79305'].values[0]
    else:
        label = ids['Ribotipo'][ids['Cepa']==aux[1].values[z]].values[0]
    labels.append(label)

labels = np.array(labels)

final_dataset = {'maldi': maldi_df, 'ir': ir_df, 'ribotype': labels}

import pickle
with open('data/clover_proccesed_fulldataset.pkl', 'wb') as handle:
    pickle.dump(final_dataset, handle, protocol=pickle.HIGHEST_PROTOCOL)





# ======================= Only using MALDITOF =======================
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
import seaborn as sns
from sklearn.metrics import balanced_accuracy_score

y3 = np.arange(275)
y3[np.where(labels==27)[0]]=27
y3[np.where(labels==181)[0]]=181
y3[np.where((labels!=181) & (labels!=27))[0]]=3

x_train, x_test, y_train, y_test = train_test_split(maldi_df, y3, train_size=0.7, random_state=0)


max_depth=[2, 8, 16]
n_estimators = [64, 128, 256]
param_grid = dict(max_depth=max_depth, n_estimators=n_estimators)

# Build the grid search
dfrst = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
grid = GridSearchCV(estimator=dfrst, param_grid=param_grid, scoring='balanced_accuracy', cv = 5, verbose=2)
grid_results = grid.fit(x_train, y_train)

# Summarize the results in a readable format
best_clf = grid_results.best_estimator_
y_pred = best_clf.predict(x_test)

acc = balanced_accuracy_score(y_test, y_pred)

# ======================= Only using IR =======================
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
import seaborn as sns
from sklearn.metrics import balanced_accuracy_score

y3 = np.arange(275)
y3[np.where(labels==27)[0]]=27
y3[np.where(labels==181)[0]]=181
y3[np.where((labels!=181) & (labels!=27))[0]]=3

x_train, x_test, y_train, y_test = train_test_split(ir_df, y3, train_size=0.7, random_state=0)


max_depth=[2, 8, 16]
n_estimators = [64, 128, 256]
param_grid = dict(max_depth=max_depth, n_estimators=n_estimators)

# Build the grid search
dfrst = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
grid = GridSearchCV(estimator=dfrst, param_grid=param_grid, scoring='balanced_accuracy', cv = 5, verbose=2)
grid_results = grid.fit(x_train, y_train)

# Summarize the results in a readable format
best_clf = grid_results.best_estimator_
y_pred = best_clf.predict(x_test)

acc = balanced_accuracy_score(y_test, y_pred)
