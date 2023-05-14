import pandas as pd
import streamlit as st
import altair as alt
from adtk.data import validate_series
from adtk.detector import ThresholdAD


def analyze_voltage(df: pd.DataFrame):
    _df = validate_series(df).reset_index()

    st.write(_df.head())

    # Anomaly detections
    threshold_ad = ThresholdAD(low=0)

    threshold_anomalies = threshold_ad.detect(df)
    threshold_anomalies = threshold_anomalies.rename(
        columns={"BatteryVoltage": "isAnomaly"}
    )

    _df = pd.merge(_df, threshold_anomalies, on="Timestamp")

    st.write("_df with anomalies")
    st.write(_df.head())

    chart = (
        alt.Chart(_df)
        .mark_circle(interpolate="basis", color="#0160ff", size=5)
        .encode(
            x=alt.X("Timestamp", title="Timestamp"),
            y=alt.Y("BatteryVoltage", title="Battery voltage"),
            color=alt.condition(
                alt.datum.isAnomaly, alt.value("red"), alt.value("#0160ff")
            ),
            size=alt.condition(
                alt.datum.isAnomaly, alt.value(20), alt.value(5)
            ),
        )
        .interactive(bind_y=False)
    )

    st.altair_chart(chart, use_container_width=True)
