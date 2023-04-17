from IPython.display import display
import os
import pandas as pd


def get_csv_data():
    df = pd.read_csv(
        "data/data.csv", low_memory=False)
    print(f'data.csv : {df.shape}')

    display(df.head(3))

    return df
