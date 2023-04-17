import pandas as pd
import os
from dotenv import load_dotenv
import pyodbc


def fetch_data(select_top=100):
    load_dotenv()

    server = os.environ.get('DB_SERVER')
    catalog = os.environ.get('DB_CATALOG')
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')

    connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};Server={server};Initial Catalog={catalog};Persist Security Info=False;UID={username};PWD={password};MultipleActiveResultSets=True;Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"

    connection = pyodbc.connect(connection_string)

    cursor = connection.cursor()

    query = f"""SELECT TOP ({select_top}) [Id]
          ,[Wm6_DeviceSettingId]
          ,[WaterLevel]
          ,[BatteryVoltage]
          ,[Timestamp]
      FROM [{catalog}].[dbo].[SensorData]"""

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


def write_csv():

    data = fetch_data(10000)

    ids, device_ids, water_levels, battery_voltages, timestamps = zip(*data)

    df = pd.DataFrame({
        'Id': ids,
        'Wm6_DeviceSettingId': device_ids,
        'WaterLevel': water_levels,
        'BatteryVoltage': battery_voltages,
        'Timestamp': timestamps
    })

    df.to_csv('data/data.csv', index=False)


write_csv()
