import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor as LOF
import sys
import os


def get_scores(distance_matrix):
    scores = np.zeros(distance_matrix.shape[0])
    distance_matrix = distance_matrix.replace(
        [np.inf], np.finfo(np.float64).max)
    for i in range(10, 40, 5):
        clf = LOF(n_neighbors=i, metric="precomputed")
        clf.fit(distance_matrix)
        scores = np.maximum(scores, clf.negative_outlier_factor_ * -1)
    return scores


def handle_sensor(sensor):
    windows = {w: pd.read_csv(sensor + '/' + w, parse_dates=True, index_col=0)
               for w in os.listdir(sensor)}
    scores = {w: get_scores(d) for w, d in windows.items()}
    # extract hour offset from filename
    def offset(w): return w[:-4].split('-')[-1]
    scores1 = [pd.Series(s, index=windows[w].index +
                         pd.Timedelta(offset(w)+'h')) for w, s in scores.items()]
    if len(scores1) == 0:
        print("skipping", sensor)
        return pd.Series(dtype=float)
    else:
        return pd.concat(scores1)


if __name__ == "__main__":
    # target_dir should be of the form
    # distances/{metric}/
    # e.g. distances/euclidean/
    target_dir = sys.argv[1]
    metric = target_dir.split("/")[1]
    intersections = [target_dir + t for t in os.listdir(target_dir)]
    try:
        os.mkdir('LOF')
        print("Created directory: LOF")
    except Exception:
        pass
    try:
        os.mkdir('LOF/'+metric)
        print("Created directory: LOF/{}".format(metric))
    except Exception:
        pass
    for i in intersections:
        sensors = {s[-3:]: handle_sensor(i + '/' + s) for s in os.listdir(i)}
        pd.concat(sensors, axis=1).to_csv(
            "LOF/{}/{}.csv".format(metric, i[-3:]))
