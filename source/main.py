import numpy as np
import pandas as pd
import os
import sklearn
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from data_handling import *
from evaluation import *


def main():
    dataframe = pd.read_csv("dataset.csv")
    train_data, test_data, val_data = split_data(dataframe)

    X = train_data.drop("stroke", axis=1)

    y = train_data["stroke"]
    clf = LogisticRegression(random_state=0, max_iter=1000).fit(X, y)

    x_new = val_data.drop("stroke", axis=1)
    y_new = val_data[["stroke"]]
    y_predict = clf.predict_proba(x_new)

    precision_recall_values(y_predict, y_new, threshold=0.2)
    precision_recall_plot(y_predict, y_new)


if __name__ == '__main__':
    main()