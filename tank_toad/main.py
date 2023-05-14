import streamlit as st
from pandas import DataFrame


from .anomaly_detection import anomaly_detection
from .get_data import get_data
from .analyze_water_level import analyze_water_level
from .analyze_voltage import analyze_voltage

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



def _inspect_device(device_id):
    data = get_data(device_id)

    if data == None or len(data) == 0 or data == "":
        return None
    

    # Specify the fields for which you want to detect anomalies
    # fields_to_inspect = ["WaterLevel", "BatteryVoltage"]

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
    st.subheader(f'Water level {serial_number}')
    analyze_water_level(water_lvl_df)

    # Battery voltage anomaly detection  
    st.subheader(f'Battery voltage {serial_number}')
    analyze_voltage(voltage_df)




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

