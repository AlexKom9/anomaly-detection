import streamlit as st
from pandas import DataFrame


from .anomaly_detection import anomaly_detection
from .get_data import get_data
from .analyze_water_level import analyze_water_level
from .analyze_voltage import analyze_voltage_autoregression, analyze_voltage_seasonal, analyze_voltage_volatility_shift

st.title("Tank toad anomaly detection")

def _inspect_device(device_id):
    data = get_data(device_id)

    if data == None or len(data) == 0 or data == "":
        return None
    

    df_device, df_gcom_packages, device_settings = data
    serial_number = device_settings["serial_number"]

    voltage_df = df_device.loc[:,['BatteryVoltage']]
    water_lvl_df = df_device.loc[:, ['WaterLevel']]

    st.title(f"Device {serial_number}")

    # st.write(df_device.head())
    # st.write(df_voltage.head())
    # st.write(df_water_lvl.head())
    # st.write(df_gcom_packages.head())


    # Water level anomaly detection  
    analyze_water_level(water_lvl_df, serial_number)

    # Battery voltage anomaly detection  
    analyze_voltage_autoregression(voltage_df, serial_number)
    analyze_voltage_seasonal(voltage_df, serial_number)
    analyze_voltage_volatility_shift(voltage_df, serial_number)

def main():
    # 8296, 2175
    device_ids = [8260]

    for device_id in device_ids:
        _inspect_device(device_id)

