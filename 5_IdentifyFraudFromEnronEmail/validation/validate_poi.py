#!/usr/bin/python


"""
    Starter code for the validation mini-project.
    The first step toward building your POI identifier!

    Start by loading/formatting the data

    After that, it's not our code anymore--it's yours!
"""

import pickle
import sys
sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit

data_dict = pickle.load(open("../final_project/final_project_dataset.pkl", "r") )

### first element is our labels, any added elements are predictor
### features. Keep this the same for the mini-project, but you'll
### have a different feature list when you do the final project.
features_list = ["poi", "salary"]

data = featureFormat(data_dict, features_list)
labels, features = targetFeatureSplit(data)



### it's all yours from here forward!  

from sklearn import tree
from sklearn import metrics
from sklearn.model_selection import train_test_split

clf = tree.DecisionTreeClassifier()
clf.fit(features, labels)
pred = clf.predict(features)
accuracy = metrics.accuracy_score(labels, pred)
print "The training data accuracy is : ", accuracy

x_train, x_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=42)
clf.fit(x_train, y_train)
pred_cv = clf.predict(x_test)
accuracy_cv = metrics.accuracy_score(y_test, pred_cv)
print "The test data accuracy is : ", accuracy_cv
