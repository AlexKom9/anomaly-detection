import pandas as pd
import streamlit as st
import altair as alt
from adtk.data import validate_series
from adtk.detector import ThresholdAD

def _draw_chart(df: pd.DataFrame):
    chart = (
        alt.Chart(df)
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


def analyze_water_level(df: pd.DataFrame, serial_number: str):
    st.subheader(f"Water level {serial_number}")

    _df = validate_series(df).reset_index()

    # st.write(_df.head())

    # Anomaly detections
    threshold_ad = ThresholdAD(low=0)

    threshold_anomalies = threshold_ad.detect(df)
    threshold_anomalies = threshold_anomalies.rename(
        columns={"WaterLevel": "isWaterLevelAnomaly"}
    )

    _df = pd.merge(_df, threshold_anomalies, on="Timestamp")

    # st.write("_df with anomalies")
    # st.write(_df.head())
    _draw_chart(_df)

