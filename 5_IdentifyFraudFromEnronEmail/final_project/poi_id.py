#!/usr/bin/python


# Functions to be used in this project
# We use SVM classifier and tune the parameters
def build_model_svm(features_std, param_grid):
    # the input features should be standardized already
    x_train, x_test, y_train, y_test = train_test_split(features_std, labels, test_size=0.2, random_state=0)
    cv_svm = StratifiedShuffleSplit(n_splits=5, test_size=0.3, random_state=99)
    grid = GridSearchCV(svm.SVC(), cv=cv_svm, n_jobs=1, param_grid=param_grid, scoring='precision')
    grid.fit(x_train, y_train)
    return grid


def calc_ratio(value, total):
    if total == 0:
        return 0
    else:
        return float(float(value) / float(total))


def visualize_features(features):
    for i in range(1, len(features.columns)):
        plt.hist(features.iloc[:, i - 1], 100, facecolor='green', alpha=0.75)
        plt.xlabel(features_list[i])
        plt.savefig('./plot/hist_{}.png'.format(features_list[i]))


def visualize_mutual_info(kscores):
    ind = np.arange(len(kscores['score']))
    width = 0.35  # define width of the bars
    plt.bar(ind, kscores['score'], width, color='r')
    plt.xticks(ind + width / 2, list(kscores.index), rotation="vertical")
    plt.title('Mutual information score for each feature')
    plt.tight_layout()
    plt.show()


def visualize_outliers(df_plot):
    c_map = {1: 'r', 0: 'b'}
    plt.scatter(df_plot['total_stock_value'], df_plot['total_payments'],
                c=[c_map.get(c, 'yellow') for c in df_plot.POI], alpha=0.5)
    plt.title('Scatter plot of total stock value and total payments')
    plt.xlabel('Total stock value')
    plt.ylabel('Total payments')
    plt.show()


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import pickle
    import sys

    from sklearn.feature_selection import mutual_info_classif, SelectKBest, VarianceThreshold
    from sklearn.model_selection import cross_val_score, GridSearchCV, StratifiedShuffleSplit, train_test_split
    from sklearn import naive_bayes, tree, svm
    from sklearn import preprocessing

    sys.path.append("../tools/")

    from feature_format import featureFormat, targetFeatureSplit
    from tester import dump_classifier_and_data, test_classifier

    # Task 1: Select what features you'll use.
    # features_list is a list of strings, each of which is a feature name.
    # The first feature must be "poi".
    features_list = ['poi', 'salary', 'to_messages', 'deferral_payments', 'total_payments',
                     'exercised_stock_options', 'bonus', 'restricted_stock', 'shared_receipt_with_poi',
                     'restricted_stock_deferred', 'total_stock_value', 'expenses', 'loan_advances',
                     'from_messages', 'other', 'from_this_person_to_poi', 'director_fees', 'deferred_income',
                     'long_term_incentive', 'from_poi_to_this_person']  # 'email_address' is excluded

    # Load the dictionary containing the dataset
    with open("final_project_dataset.pkl", "r") as data_file:
        data_dict = pickle.load(data_file)

    # Store to my_dataset for easy export below.
    my_dataset = data_dict

    # Extract features and labels from dataset for local testing
    data = featureFormat(dictionary=my_dataset,
                         features=features_list,
                         remove_NaN=True,
                         remove_all_zeroes=True,
                         remove_any_zeroes=False,
                         sort_keys=False)

    labels, features = targetFeatureSplit(data)

    # Convert to pandas data frame for easier pre-processing and visualization
    features = pd.DataFrame(features)
    features.columns = features_list[1:]

    # Task 2: Remove outliers
    # plot total payments vs. total stock value
    df_plot = features
    df_plot['POI'] = labels
    # visualize_outliers(df_plot)

    # outlier removal
    df_plot = df_plot[df_plot.total_stock_value <= 100000000]
    df_plot = df_plot[df_plot.total_payments <= 100000000]
    labels = list(df_plot['POI'])
    features = df_plot.drop(['POI'], axis=1)

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
    # print features.describe()

    # Task 4: Try a variety of classifiers
    # Please name your classifier clf for easy export below.
    # Note that if you want to do PCA or other multi-stage operations,
    # you'll need to use Pipelines. For more info:
    # http://scikit-learn.org/stable/modules/pipeline.html

    # Feature elimination using VarianceThreshold
    features_scaled = preprocessing.minmax_scale(features)
    fs_var = VarianceThreshold(threshold=0)
    fs_var.fit(features_scaled)
    # print "The variances after min-max scaling are: ", fs_var.variances_

    # Feature selection using K-best
    fs_kbest = SelectKBest(score_func=mutual_info_classif, k=15)
    features_kbest = fs_kbest.fit(features, labels)
    kscores = pd.DataFrame(fs_kbest.scores_, columns=['score'], index=features.columns.values)
    kscores = kscores.sort_values('score', ascending=0)
    # print "Mutual information for each feature: ", kscores

    # Define list of selected features
    selected_feature_names = ['bonus', 'deferred_income', 'exercised_stock_ratio',
                              'expenses', 'from_this_person_to_poi',
                              'from_this_person_to_poi_fraction', 'from_poi_to_this_person_fraction',
                              'other', 'restricted_stock', 'restricted_stock_deferred',
                              'salary', 'shared_receipt_with_poi', 'total_stock_value']
    selected_features = features[selected_feature_names]
    # print 'Pearson correlation between feature pairs: ', selected_features.corr(method='pearson')

    n_samples = selected_features.shape[0]
    cv = StratifiedShuffleSplit(n_splits=5, test_size=0.3, random_state=99)

    # SVM classifier
    features_std_svm = preprocessing.scale(selected_features)
    clf_svm = svm.SVC(class_weight={0: 0.124, 1: 0.876})
    cv_scores = cross_val_score(clf_svm, features_std_svm, labels, cv=cv, scoring='f1')
    # print "Support Vector Machine: F1 scores after cross validation are: ", cv_scores

    # Naive Bayes classifier
    selected_feature_names_nb = ['exercised_stock_ratio', 'from_this_person_to_poi',
                                 'from_this_person_to_poi_fraction',
                                 'from_poi_to_this_person_fraction',
                                 'restricted_stock_deferred', 'shared_receipt_with_poi']
    features_nb = selected_features[selected_feature_names_nb]
    features_std_nb = preprocessing.scale(features_nb)
    clf_nb = naive_bayes.GaussianNB()
    cv_scores = cross_val_score(clf_nb, features_std_nb, labels, cv=cv, scoring='f1')
    # print "Naive Bayes: F1 scores after cross validation are: ", cv_scores

    param_grid_1 = [
        {'C': [1, 100],
         'gamma': [0.001, 0.0001],
         'kernel': ['rbf'],
         'class_weight': [{0: 0.1}, {0: 0.2}, {0: 0.5}, {0: 0.8}]
         }
    ]
    param_grid_2 = [
        {'C': [100],
         'gamma': [0.1, 0.01, 0.001, 0.0001],
         'kernel': ['rbf'],
         'class_weight': [{0: 0.2}]
        }
    ]

    grid_results_1 = build_model_svm(features_std_svm, param_grid_1)
    grid_results_2 = build_model_svm(features_std_svm, param_grid_2)
    # print grid_results_2.best_params_

    # Task 5: Tune your classifier to achieve better than .3 precision and recall
    # using our testing script. Check the tester.py script in the final project
    # folder for details on the evaluation method, especially the test_classifier
    # function. Because of the small size of the dataset, the script uses
    # stratified shuffle split cross validation. For more info:
    # http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html
    clf = svm.SVC(kernel='rbf', C=100, gamma=0.01, class_weight={0: 0.2, 1: 0.8})

    features_list = ['poi'] + selected_feature_names
    my_dataset = {}
    for i in range(features_std_svm.shape[0]):
        row = [labels[i]] + list(features_std_svm[i, ])
        my_dataset[i] = dict(zip(features_list, row))

    # # Task 6: Dump your classifier, dataset, and features_list so anyone can
    # # check your results. You do not need to change anything below, but make sure
    # # that the version of poi_id.py that you submit can be run on its own and
    # # generates the necessary .pkl files for validating your results.
    dump_classifier_and_data(clf, my_dataset, features_list)