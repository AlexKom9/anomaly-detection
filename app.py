from IPython.display import HTML, display
from tabulate import tabulate
import shap
from sklearn.metrics import f1_score
import changefinder
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
import scipy.stats as stats
import os
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import holoviews as hv
from holoviews import opts

from fetch_data import fetch_data
from get_csv_data import get_csv_data
from data.anomaly_points import anomaly_point_ids

hv.extension('bokeh')
shap.initjs()

df = get_csv_data()

df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['anomaly'] = 0

for anomaly_point_id in anomaly_point_ids['device_6']:
    df.loc[df['Id'] == anomaly_point_id, 'anomaly'] = 1

df['year'] = df['Timestamp'].apply(lambda x: x.year)
df['month'] = df['Timestamp'].apply(lambda x: x.month)
df['day'] = df['Timestamp'].apply(lambda x: x.day)
df['hour'] = df['Timestamp'].apply(lambda x: x.hour)
df['minute'] = df['Timestamp'].apply(lambda x: x.minute)


df.index = df['Timestamp']
df.drop(['Timestamp'], axis=1, inplace=True)


# Basic analysis
count = hv.Bars(df.groupby(['year', 'month'])['BatteryVoltage'].count()).opts(
    ylabel="Count", title='Year/Month Count')
