'''
This script trains Random Forest Classifier model using CDC Diabetes Health Indicators
dataset from UCI Machine Learning Repository and saves it as a FHE Model.
'''

from concrete.ml.sklearn import RandomForestClassifier
from concrete.ml.deployment import FHEModelDev
from ucimlrepo import fetch_ucirepo
from sklearn.preprocessing import LabelEncoder

fhe_directory = '/tmp/diabetes_fhe_files/'

model = RandomForestClassifier(n_estimators=10, max_depth=5)

uci_ds = fetch_ucirepo(id=891)
X = uci_ds.data.features
y = uci_ds.data.targets
le = LabelEncoder()
y = le.fit_transform(y.values.ravel())

model.fit(X, y)
model.compile(X)

dev = FHEModelDev(path_dir=fhe_directory, model=model)
dev.save()