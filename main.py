import streamlit as st

from tank_toad.anomaly_detection import anomaly_detection
from tank_toad.get_data import get_data

st.title("Tank toad anomaly detection")


def _anomalyDetectionHandler(data, fields_to_inspect, serial_number):
    if len(data) == 0 | len(fields_to_inspect) == 0:
        return None

    defaultFileData = data[0]
    fieldsDetection = fields_to_inspect

    # Detect anomalies in WaterLevel & BatteryVoltage
    for column_name in fieldsDetection:
        anomaly_detection(
            values=defaultFileData[[column_name]], column_name=column_name, serial_number=serial_number
        )

    # Detect anomalies in TotalBytes
    anomaly_detection(
        values=data[1], column_name="TotalBytes", serial_number=serial_number
    )


def inspect_device(device_id):
    data = get_data(device_id)

    if data == None or len(data) == 0 or data == "":
        return None

    # Specify the fields for which you want to detect anomalies
    fieldsAnomalies = ["WaterLevel", "BatteryVoltage"]
    device_data = data[0]
    GCOM_packages = data[1]
    device_settings = data[2]

    serial_number = device_settings["SerialNumber"]

    _anomalyDetectionHandler(
        data=[device_data, GCOM_packages],
        fields_to_inspect=fieldsAnomalies,
        serial_number=serial_number,
    )


def main():
    device_ids = [8296, 2175]

    for device_id in device_ids:
        inspect_device(device_id)


main()