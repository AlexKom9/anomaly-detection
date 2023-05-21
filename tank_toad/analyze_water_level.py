import pandas as pd
import streamlit as st
import altair as alt
from adtk.data import validate_series
from adtk.detector import ThresholdAD, AutoregressionAD
from adtk.transformer import RollingAggregate


def _draw_chart(df: pd.DataFrame):
    chart = (
        alt.Chart(df.reset_index())
        .mark_circle()
        .encode(
            x=alt.X("Timestamp", title="Timestamp"),
            y=alt.Y("WaterLevel", title="Water level"),
            color=alt.condition(
                alt.datum.isWaterLevelAnomaly, alt.value("red"), alt.value("#0160ff")
            ),
            size=alt.condition(
                alt.datum.isWaterLevelAnomaly, alt.value(5), alt.value(3)
            ),
        )
        .interactive(bind_y=False)
    )

    st.altair_chart(chart, use_container_width=True)


def analyze_water_level_threshold(df: pd.DataFrame, serial_number: str):
    st.subheader(f"Water level (threshold) {serial_number}")

    _df = validate_series(df).reset_index()

    threshold_ad = ThresholdAD(low=0)

    threshold_anomalies = threshold_ad.detect(df)
    threshold_anomalies = threshold_anomalies.rename(
        columns={"WaterLevel": "isWaterLevelAnomaly"}
    )

    _df = pd.merge(_df, threshold_anomalies, on="Timestamp")

    _draw_chart(_df)


def analyze_water_level_rolling_aggregate(df: pd.DataFrame, serial_number: str):
    st.subheader(f"Water level (rolling aggregate) {serial_number}")

    _df = validate_series(df)
    transformed = RollingAggregate(agg="count", window=5).transform(_df)

    _draw_chart(transformed)

def analyze_water_level_autoregression(df: pd.DataFrame, serial_number: str):
    st.subheader(f"Water level (autoregression) {serial_number}")

    _df = validate_series(df)

    # TODO: adjust params
    autoregression_ad = AutoregressionAD(n_steps=24, step_size=24, c=3.0)
    autoregression_anomalies = autoregression_ad.fit_detect(_df)

    autoregression_anomalies = autoregression_anomalies.rename(
        columns={"WaterLevel": "isAnomaly"}
    )

    # st.write(autoregression_anomalies.head())

    _df = pd.merge(_df, autoregression_anomalies, on="Timestamp")

    _draw_chart(_df)
