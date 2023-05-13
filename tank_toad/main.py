import streamlit as st
from pandas import DataFrame

from .anomaly_detection import anomaly_detection
from .get_data import get_data
from .analize_water_level import analyze_water_level

st.title("Tank toad anomaly detection")


def _anomalyDetectionHandler(data, fields_to_inspect, serial_number):
    if len(data) == 0 | len(fields_to_inspect) == 0:
        return None

    # defaultFileData = data[0]
    # fieldsDetection = fields_to_inspect

    st.table(data)

    # Detect anomalies in WaterLevel & BatteryVoltage
    # for column_name in fieldsDetection:
    #     anomaly_detection(
    #         values=defaultFileData[[column_name]], column_name=column_name, serial_number=serial_number
    #     )

    # Detect anomalies in TotalBytes
    # anomaly_detection(
    #     values=data[1], column_name="TotalBytes", serial_number=serial_number
    # )



def ad_handler(df: DataFrame, title: str):
    st.subheader(title)
    analyze_water_level(df)
    
    

def _inspect_device(device_id):
    data = get_data(device_id)

    if data == None or len(data) == 0 or data == "":
        return None

    # Specify the fields for which you want to detect anomalies
    # fields_to_inspect = ["WaterLevel", "BatteryVoltage"]

    df_device, df_gcom_packages, device_settings = data
    serial_number = device_settings["serial_number"]

    # voltage_data = 
    
    st.subheader(f"Data preview {serial_number}")


    df_voltage = df_device.loc[:,['BatteryVoltage']]
    df_water_lvl = df_device.loc[:, ['WaterLevel']]

    # st.write(df_device.head())
    st.write(df_voltage.head())
    st.write(df_water_lvl.head())
    st.write(df_gcom_packages.head())

    # Water level anomaly detection  
    ad_handler(df_water_lvl, f'Water level {serial_number}')



    # _anomalyDetectionHandler(
    #     data=[data_device, data_gcom_packages],
    #     fields_to_inspect=fields_to_inspect,
    #     serial_number=serial_number,
    # )


def main():
    # 8296, 2175
    device_ids = [8296]

    for device_id in device_ids:
        _inspect_device(device_id)

