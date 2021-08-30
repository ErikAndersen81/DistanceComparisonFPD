import pandas as pd
from os import listdir


def m_hol_corr(metric):
    hol = pd.read_csv("OriginalData/holidays.csv",
                      index_col=0, parse_dates=True)
    any_hol = hol['any_holiday'] = hol.school_holiday | hol.other_holidays
    any_hol.index = any_hol.index + pd.Timedelta("8h")
    any_hol = any_hol[any_hol == 1]
    corrs = []
    for f in listdir(metric):
        df = pd.read_csv(metric+f, parse_dates=True, index_col=0)
        outlier_dates = df[(df > 1.3).any(axis=1)].index
        corrs.append(
            len(any_hol.loc[any_hol.index.isin(outlier_dates)]))
    return pd.Series(corrs, index=["K" + f[:3] for f in listdir(metric)])


def holidays_correlation():
    metrics = listdir("LOF")
    return pd.concat([m_hol_corr("LOF/{}/".format(m)) for m in metrics],
                     keys=metrics,
                     axis=1)


def tweets_corr(metric, tw):
    corrs = []
    for f in listdir(metric):
        df = pd.read_csv(metric+f, parse_dates=True, index_col=0)
        outlier_dates = df[(df > 1.3).any(axis=1)].index
        corrs.append(
            len(tw.loc[tw.index.isin(outlier_dates)]))
    return pd.Series(corrs, index=["K" + f[:3] for f in listdir(metric)])


def tweets_correlation():
    metrics = listdir("LOF")
    tw1 = pd.read_csv("OriginalData/tweets_2018-2019.csv",
                      parse_dates=True,
                      index_col=1)
    tw1.index = tw1.index.round('1H')
    return pd.concat([tweets_corr("LOF/{}/".format(m), tw1) for m in metrics],
                     keys=metrics,
                     axis=1)


if __name__ == "__main__":
    df = holidays_correlation()
    df.to_csv("holidays_correlation.csv")
    df = tweets_correlation()
    df.to_csv("tweets_correlation.csv")
