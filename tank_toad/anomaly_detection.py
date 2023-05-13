import streamlit as st
import pandas as pd
from pandas import DataFrame
import numpy as np
import altair as alt
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_blobs

# IForest Detector
def _iforest_detector(values):
    iforest = IsolationForest(
        max_samples=20000,
        random_state=0,
        contamination=0.035,
        max_features=1,
        n_estimators=2000,
        bootstrap=False,
        verbose=1,
        n_jobs=-1,
    )

    iforest.fit(values)
    y_pred = iforest.predict(values)
    y_pred_adjusted = ["yes" if x == -1 else "no" for x in y_pred]

    return y_pred_adjusted


def _dbscan_detector(values, column_name):
    determineAnomalies = values[column_name].values
    X1 = np.arange(len(determineAnomalies))

    x, _ = make_blobs(
        n_samples=len(determineAnomalies),
        centers=1,
        cluster_std=0.5,
        center_box=(0, np.amax(determineAnomalies)),
    )

    dbscan = DBSCAN(
        eps=0.3, min_samples=5 * 5, algorithm="ball_tree", metric="haversine"
    )
    pred = dbscan.fit_predict(x)

    anomaly_index = np.where(pred == -1)
    x_anomaly_index = X1[anomaly_index[0]]

    return x_anomaly_index


def anomaly_detection(values: DataFrame, column_name, serial_number):
    # Fill NaN values in pd.Series
    values = values.fillna(
        dict.fromkeys(values.columns.tolist(), values[column_name].ffill())
    )

    # Initial graph & added draw all selection values
    x = values[column_name].index
    y = values[column_name].values

    val = pd.DataFrame({"x": x, "y": y})

    _chart = (
        alt.Chart(val)
        .mark_circle(interpolate="basis", color="#0160ff")
        .encode(
            x=alt.X("x", title="Date"),
            y=alt.Y("y", title="Values"),
        )
        .interactive(bind_y=False)
    )

    anomaly_points_x = []
    anomaly_points_y = []

    # IForest algorithm
    if column_name == "BatteryVoltage":
        _iforest = _iforest_detector(values)

        for i in range(len(_iforest)):
            if _iforest[i] == "yes":
                anomaly_points_x.append(x[i])
                anomaly_points_y.append(y[i])

    # DBSCAN, IForest algorithms
    elif column_name == "WaterLevel" or "TotalBytes":
        _iforest = _iforest_detector(values)
        _dbscan = _dbscan_detector(values, column_name)

        for i in range(len(_iforest)):
            if _iforest[i] == "yes":
                anomaly_points_x.append(x[i])
                anomaly_points_y.append(y[i])

        for i in _dbscan:
            anomaly_points_x.append(x[i])
            anomaly_points_y.append(y[i])

    # Draw anomaly data
    val = pd.DataFrame({"x": anomaly_points_x, "y": anomaly_points_y})

    _chart += (
        alt.Chart(val)
        .mark_circle(interpolate="basis", color="red")
        .encode(x=alt.X("x", title="Date"), y=alt.Y("y", title="Values"))
        .interactive(bind_y=False)
    )

    st.write(column_name + " " + serial_number)
    st.altair_chart(_chart, use_container_width=True)
