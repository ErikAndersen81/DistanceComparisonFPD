import sys
import os
import numpy as np
import pandas as pd


def handle_sensor(series, sensor_name, intersection_name):
    sensor_fpds = dict()
    # The two for loops represents the windows for
    # which we calculate FPDs
    for day in range(7):
        for hour in range(24):
            s = series[(series.index.weekday == day)
                       & (series.index.hour == hour)]
            fpds = dict()
            dates = list(np.unique(s.index.date))
            for date in dates:
                # Calculate the FPD. Index will be the support points and
                # the actual values are the weights
                # Note that nan values are not counted, so if the sum is
                # less than 12 which is the number of measurements required
                # for a full hour of 5 min intervals, we do not include it.
                fpd = s[s.index.date == date].value_counts()
                if fpd.sum() == 12:
                    fpds[date] = fpd
            # we exclude sensor windows with less than 100 FPDs
            if len(fpds.keys()) > 100:
                try:
                    fpds = pd.concat(fpds, axis=0)
                    fpds = fpds/12
                    sensor_fpds[day, hour] = fpds
                except Exception:
                    print("not enough fpds for {}, day {}, hour {}".format(
                        sensor_name, day, hour))
    try:
        fpds = pd.concat(sensor_fpds)
        fpds.index.names = ['weekday', 'hour',
                            'date', 'measurement']
        fpds.to_csv("fpds/{}/{}.csv".format(intersection_name, sensor_name))
    except Exception:
        print("not enough sensor fpds for {}".format(sensor_name))


if __name__ == "__main__":
    target = sys.argv[1]
    try:
        os.mkdir("fpds")
        print("created directory: fpds")
    except Exception:
        pass

    df = pd.read_csv(target, parse_dates=True, index_col=0)
    try:
        os.mkdir("fpds/" + df.index.name)
        print("created directory: fpds/{}".format(df.index.name))
    except Exception:
        pass
    print("Handling sensors: ", end=" ")
    for col in df.columns:
        print(col, end=" ")
        handle_sensor(df[col],  sensor_name=col,
                      intersection_name=df.index.name)
