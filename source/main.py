import numpy as np
import pandas as pd
import os
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from data_cleaning import *
from plotting import *
from sklearn.model_selection import StratifiedKFold
from sklearn.base import clone


def my_cross_val(model, x_train, y_train):
    skfolds = StratifiedKFold(n_splits=6, shuffle=True)
    threshold = 0.18
    avg_f1 = 0

    for train_index, test_index in skfolds.split(x_train, y_train):
        clone_model = clone(model)
        x_train_folds = x_train.iloc[train_index]
        y_train_folds = y_train.iloc[train_index]
        x_test_fold = x_train.iloc[test_index]
        y_test_fold = y_train.iloc[test_index]

        clone_model.fit(x_train_folds, y_train_folds)
        y_pred = clone_model.predict_proba(x_test_fold)

        y_pred = [1 if x >= threshold else 0 for x in y_pred[:, 1]]

        f1 = sklearn.metrics.f1_score(y_test_fold, y_pred, average="macro")

        avg_f1 += f1

    avg_f1 /= 6
    return avg_f1


def roc_evaluate(clf, x, y_true, label=None):
    y_proba = sklearn.model_selection.cross_val_predict(clf, x, y_true, cv=3, method="predict_proba")
    y_score = y_proba[:, 1]
    fpr, tpr, thresholds = sklearn.metrics.roc_curve(y_true, y_score)
    plot_roc_curve(tpr, fpr, label)


def backward_stepwise_selection(x_train, y_train, x_test, y_test):
    model = LogisticRegression(random_state=0, max_iter=10000)
    length = len(x_train.columns) - 1

    f1_scores = []

    for j in range(length):
        clone_model = clone(model)
        x_step = x_train.drop(x_train.columns[0], axis=1)
        worst_feature = x_train.columns[0]
        highest_f1 = my_cross_val(clone_model, x_step, y_train)

        for i in range(1, len(x_train.columns)):
            clone_model = clone(model)
            x_step = x_train.drop(x_train.columns[i], axis=1)
            f1 = my_cross_val(clone_model, x_step, y_train)

            if f1 > highest_f1:
                worst_feature = x_train.columns[i]

        print("Permanent removing " + str(worst_feature))
        x_train.drop(worst_feature, axis=1, inplace=True)
        x_test.drop(worst_feature, axis=1, inplace=True)
        clone_model = clone(model)

        f1 = my_cross_val(clone_model, x_train, y_train)
        f1_scores.append(f1)
        print("F1: " + str(f1))

        clone_model.fit(x_train, y_train)
        precision_recall_plot(clone_model, x_test, y_test)

    plt.plot(list(reversed(f1_scores)))
    plt.xlabel("Number of features")
    plt.ylabel("F1 Score")
    plt.show()


def tmp(x_train, y_train, x_test, y_test):
    model = LogisticRegression(random_state=0, max_iter=10000)
    model.fit(x_train, y_train)
    print("-" * 20 + "logistic regiression" + "-" * 20)
    y_pred = model.predict(x_test)
    arg_test = {"y_true": y_test, "y_pred": y_pred}
    print(sklearn.metrics.confusion_matrix(**arg_test))
    print(sklearn.metrics.classification_report(**arg_test))


def one_feature(x_train, y_train, x_test, y_test):
    x_train = x_train[["hypertension"]]
    x_test = x_test[["hypertension"]]
    model = LogisticRegression(random_state=0, max_iter=10000)
    model.fit(x_train, y_train)
    y_pred = model.predict_proba(x_test)
    y_pred = [1 if x >= 0.18 else 0 for x in y_pred[:, 1]]
    f1 = sklearn.metrics.f1_score(y_test, y_pred, average="macro")
    print("F1: " + str(f1))


def main():
    dataframe = pd.read_csv("dataset.csv")

    dataframe = clean_data(dataframe)
    x_train, y_train, x_test, y_test = split_data(dataframe)
    #tmp(x_train, y_train, x_test, y_test)

    one_feature(x_train, y_train, x_test, y_test)
    #backward_stepwise_selection(x_train, y_train, x_test, y_test)
    #my_cross_val(lr_clf, x_train, y_train)
    '''
    lr_clf = LogisticRegression(random_state=0, max_iter=10000)
    forest_clf = RandomForestClassifier(random_state=42)
    
    lr_clf.fit(x_train, y_train)
    forest_clf.fit(x_train, y_train)

    precision_recall_evaluate(forest_clf, x_train, y_train, "Random Forest")
    precision_recall_evaluate(lr_clf, x_train, y_train, "Logistic Regression")

    roc_evaluate(forest_clf, x_train, y_train, "Random Forest")
    roc_evaluate(lr_clf, x_train, y_train, "Logistic Regression")
    plt.show()

    score = sklearn.model_selection.cross_val_score()
    '''


if __name__ == '__main__':
    main()
