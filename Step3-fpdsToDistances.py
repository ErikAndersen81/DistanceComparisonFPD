import sys
import os
import pandas as pd
import numpy as np
from scipy.stats import wasserstein_distance


def squared_euclidian(A, B):
    return ((A.subtract(B, fill_value=0))**2).sum()


def BC(A, B):
    return (np.sqrt(A.multiply(B, fill_value=0))).sum()


def bhattacharyya(A, B):
    return -np.log(BC(A, B))


def hellinger(A, B):
    return np.sqrt(1-BC(A, B))


def EMD(A, B):
    return wasserstein_distance(A.index.values,
                                B.index.values,
                                u_weights=A.values,
                                v_weights=B.values)


def KL(A, B):
    return A.multiply(np.log(2 * A.divide(A.add(B, fill_value=0)).dropna())).sum()


def handle_sensor(df, dist, path, window='all'):
    weekdays = df.index.levels[0]
    hours = df.index.levels[1]
    if window != 'all':
        weekdays = [window[0]]
        hours = [window[1]]
    for w in weekdays:
        for h in hours:
            dates = df.loc[w, h].index.get_level_values(0).unique()
            n = len(dates)
            dists = np.zeros((n, n))
            for i in range(n):
                for j in range(i+1, n):
                    A = df.loc[w, h, dates[i]]
                    B = df.loc[w, h, dates[j]]
                    dists[i, j] = dists[j, i] = dist(A, B)
            dists = pd.DataFrame(dists, index=dates, columns=dates)
            dists.to_csv(path + "window-{}-{}.csv".format(w, h))
            return dists


metrics = {
    's': ('euclidean', squared_euclidian),
    'b': ('bhattacharyya', bhattacharyya),
    'h': ('hellinger', hellinger),
    'e': ('emd', EMD),
    'k': ('KL', KL)
}

if __name__ == "__main__":
    target = sys.argv[1]
    intersection = target.split('/')[-2]
    metric, dist = metrics[sys.argv[2]]
    window = 'all'
    try:
        weekday = int(sys.argv[3])
        hour = int(sys.argv[4])
        window = (weekday, hour)
        print("calculating for window {},{}".format(weekday, hour))
    except Exception:
        print("Applying to all windows... This may take some time.")
    try:
        os.mkdir("distances")
        print("created directory: distances")
    except Exception:
        pass

    df = pd.read_csv(target, index_col=[0, 1, 2, 3])
    sensor = df.columns[0]
    try:
        os.mkdir("distances/" + metric)
        print("created directory: distances/{}".format(metric))
    except Exception:
        pass
    try:
        os.mkdir("distances/{}/{}".format(metric, intersection))
        print("created directory: distances/{}/{}".format(metric, intersection))
    except Exception:
        pass
    try:
        os.mkdir("distances/{}/{}/{}".format(metric, intersection, sensor))
        print("created directory: distances/{}/{}/{}".format(metric, intersection, sensor))
    except Exception:
        pass
    path = "distances/{}/{}/{}/".format(metric, intersection, sensor)
    for col in df.columns:
        handle_sensor(df[col], dist, path, window)
