import streamlit as st
from pandas import DataFrame


from .get_data import get_data
from .analyze_water_level import (
    analyze_water_level_threshold,
    analyze_water_level_rolling_aggregate,
    analyze_water_level_autoregression,
)
from .analyze_voltage import (
    analyze_voltage_autoregression,
    analyze_voltage_seasonal,
    analyze_voltage_volatility_shift,
    analyze_voltage_suod,
)

st.title("Tank toad anomaly detection")


def _inspect_device(device_id):
    data = get_data(device_id)

    if data == None or len(data) == 0 or data == "":
        return None

    df_device, _df_gcom_packages, device_settings = data
    serial_number = device_settings["serial_number"]

    voltage_df = df_device.loc[:, ["BatteryVoltage"]]
    water_lvl_df = df_device.loc[:, ["WaterLevel"]]

    st.title(f"Device {serial_number}")

    # Water level anomaly detection
    analyze_water_level_threshold(water_lvl_df, serial_number)
    # analyze_water_level_rolling_aggregate(water_lvl_df, serial_number)
    analyze_water_level_autoregression(water_lvl_df, serial_number)

    # Battery voltage anomaly detection
    analyze_voltage_autoregression(voltage_df, serial_number)
    analyze_voltage_seasonal(voltage_df, serial_number)
    analyze_voltage_volatility_shift(voltage_df, serial_number)
    # analyze_voltage_suod(voltage_df, serial_number)


def main():
    # 8296, 2175, 8260
    device_ids = [8296, 2175, 8260, 8273]

    for device_id in device_ids:
        _inspect_device(device_id)
