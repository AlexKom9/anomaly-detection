import pandas as pd
import streamlit as st
import altair as alt
from adtk.data import validate_series
from adtk.detector import AutoregressionAD, SeasonalAD, VolatilityShiftAD

def _draw_chart(df: pd.DataFrame):
    chart = (
        alt.Chart(df.reset_index())
        .mark_circle()
        .encode(
            x=alt.X("Timestamp", title="Timestamp"),
            y=alt.Y("BatteryVoltage", title="Battery voltage"),
            color=alt.condition(
                alt.datum.isAnomaly, alt.value("red"), alt.value("#0160ff")
            ),
            size=alt.condition(alt.datum.isAnomaly, alt.value(20), alt.value(2)),
        )
        .interactive(bind_y=False)
    )

    st.altair_chart(chart, use_container_width=True)

def analyze_voltage_autoregression(df: pd.DataFrame, serial_number: str):
    st.subheader(f"Battery voltage (autoregression) {serial_number}")

    _df = validate_series(df)

    # TODO: adjust params
    autoregression_ad = AutoregressionAD(n_steps=24, step_size=24, c=3.0)
    autoregression_anomalies = autoregression_ad.fit_detect(_df)

    autoregression_anomalies = autoregression_anomalies.rename(
        columns={"BatteryVoltage": "isAnomaly"}
    )

    # st.write(autoregression_anomalies.head())

    _df = pd.merge(_df, autoregression_anomalies, on="Timestamp")

    _draw_chart(_df)

def analyze_voltage_seasonal(df: pd.DataFrame, serial_number: str):
    st.subheader(f"Battery voltage (seasonal) {serial_number}")
    _df = validate_series(df)

    _df = _df.resample("H").mean().interpolate()

    seasonal_ad = SeasonalAD(freq=24)

    anomalies_df = seasonal_ad.fit_detect(_df)
    anomalies_df = anomalies_df.rename(columns={"BatteryVoltage": "isAnomaly"})

    _df = pd.merge(_df, anomalies_df, on="Timestamp")

    _draw_chart(_df)

def analyze_voltage_volatility_shift(df: pd.DataFrame, serial_number: str):
    st.subheader(f"Battery voltage (volatility shift in 24h) {serial_number}")
    _df = validate_series(df)

    _df = _df.resample("H").mean().interpolate()

    volatility_shift_ad = VolatilityShiftAD(window='24h', c=12.0)

    anomalies_df = volatility_shift_ad.fit_detect(_df)
    anomalies_df = anomalies_df.rename(columns={"BatteryVoltage": "isAnomaly"})

    _df = pd.merge(_df, anomalies_df, on="Timestamp")

    _draw_chart(_df)
