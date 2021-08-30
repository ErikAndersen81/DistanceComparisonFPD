from os import listdir
import sys
import pandas as pd


def drop_df():
    """ For some sensors LOF could not be determined, so we
    exclude these in the calculation of performance for all metrics, 
    since a lower amount of sensors result in a higher performance value"""
    sensors = [pd.DataFrame([pd.read_csv("LOF/{}/{}".format(m, i), index_col=0)
                             .isna()
                             .all()
                             for i in listdir("LOF/{}/".format(m))],
                            index=listdir("LOF/{}/".format(m))).fillna(False)
               for m in listdir("LOF/")]
    drop = sensors.pop()
    for s in sensors:
        drop = drop | s
    return drop


def clean_sensors(df, intersection, drop):
    idx = intersection[-7:]
    cols = drop.columns[drop.loc[idx]]
    return df.drop(cols, axis=1)


def performance(intersection, drop):
    df = pd.read_csv(intersection, index_col=0)
    df = clean_sensors(df, intersection, drop)
    # find the minimum number of valid FPD-LOFs
    # per sensor in the intersection (max_k).
    max_k = (~df.isna()).sum().min()
    print(intersection)
    performance = 0
    for k in range(1, max_k):
        top_k = [set(df.nlargest(k, s).index) for s in df]
        common = top_k.pop()
        for s in top_k:
            common = common.intersection(s)
        performance += len(common)/k
    return performance/max_k


def handle_metric(metric, drop):
    intersections = [metric+i for i in listdir(metric)]
    return pd.Series([performance(i, drop) for i in intersections],
                     index=listdir(metric))


if __name__ == '__main__':
    drop = drop_df()
    metrics = listdir("LOF")
    perf = pd.concat([handle_metric("LOF/{}/".format(m), drop)
                     for m in metrics], axis=1, keys=metrics)
    perf.to_csv("performance.csv")
