#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import sys

sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data


# Functions
def calc_ratio(value, total):
    if total == 0:
        return 0
    else:
        return float(value) / float(total)


# Task 1: Select what features you'll use.
# features_list is a list of strings, each of which is a feature name.
# The first feature must be "poi".
features_list = ['poi', 'salary', 'to_messages', 'deferral_payments', 'total_payments',
                 'exercised_stock_options', 'bonus', 'restricted_stock', 'shared_receipt_with_poi',
                 'restricted_stock_deferred', 'total_stock_value', 'expenses', 'loan_advances',
                 'from_messages', 'other', 'from_this_person_to_poi', 'director_fees', 'deferred_income',
                 'long_term_incentive', 'from_poi_to_this_person', 'email_address']  # 'email_address' is excluded

# Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

# Store to my_dataset for easy export below.
my_dataset = data_dict
print len(data_dict.keys())

# Extract features and labels from dataset for local testing
data = featureFormat(dictionary=my_dataset,
                     features=features_list,
                     remove_NaN=True,
                     remove_all_zeroes=True,
                     remove_any_zeroes=False,
                     sort_keys=False)
print data.shape
labels, features = targetFeatureSplit(data)

print len(features)

# Convert to pandas dataframe
features = pd.DataFrame(features)

# Explore and visualize statistics of each column to find outliers
# print features.describe()

# for i in range(1, len(features.columns)):
#     # fig = plt.figure()
#     # ax = fig.add_subplot(111)
#     # ax.boxplot(features.iloc[:, i - 1])
#     plt.hist(features.iloc[:, i - 1], 100, facecolor='green', alpha=0.75)
#     plt.xlabel(features_list[i])
#     plt.savefig('./plot/hist_{}.png'.format(features_list[i]))

# Task 2: Remove outliers


# Task 3: Create new feature(s)
features['from_this_person_to_poi_fraction'] = features.apply(lambda row: calc_ratio(row['from_this_person_to_poi'],
                                                                                     row['from_messages']),
                                                              axis=1)
features['from_poi_to_this_person_fraction'] = features.apply(lambda row: calc_ratio(row['from_poi_to_this_person'],
                                                                                     row['to_messages']),
                                                              axis=1)
features['bonus_over_payment_ratio'] = features.apply(lambda row: calc_ratio(row['bonus'],
                                                                             row['total_payments']),
                                                      axis=1)
features['exercised_stock_ratio'] = features.apply(lambda row: calc_ratio(row['exercised_stock_options'],
                                                                          row['total_stock_value']),
                                                   axis=1)
# Task 4: Try a variaty of classifiers
# Please name your classifier clf for easy export below.
# Note that if you want to do PCA or other multi-stage operations,
# you'll need to use Pipelines. For more info:
# http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
from sklearn.naive_bayes import GaussianNB

clf = GaussianNB()

# Task 5: Tune your classifier to achieve better than .3 precision and recall
# using our testing script. Check the tester.py script in the final project
# folder for details on the evaluation method, especially the test_classifier
# function. Because of the small size of the dataset, the script uses
# stratified shuffle split cross validation. For more info:
# http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!
from sklearn.cross_validation import train_test_split

features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)

# Task 6: Dump your classifier, dataset, and features_list so anyone can
# check your results. You do not need to change anything below, but make sure
# that the version of poi_id.py that you submit can be run on its own and
# generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)