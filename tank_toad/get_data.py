import os
import pandas as pd
import pyodbc
from adtk.data import validate_series
from functools import reduce


#
# Apply DeviceSettings for WaterLevel, BatteryVoltage, GCOM_Packages
# Return normalized data
#
def _normalize_data(Data):
    if Data == None:
        return None

    DB_Data = Data[0]
    GCOM_Packages = Data[1]
    DeviceSettings = Data[2]

    DataConversionConstantA = DeviceSettings["DataConversionConstantA"]
    DataConversionConstantB = DeviceSettings["DataConversionConstantB"]

    BatteryVoltageConstant = 0.0041503906

    #
    # Getting values ​​from a series
    #
    WaterLevel = DB_Data["WaterLevel"].values
    BatteryVoltage = DB_Data["BatteryVoltage"].values

    def prettifyNumber(value):
        return round(value, 2)

    #
    # Converting values
    #
    WaterLevel = [
        prettifyNumber(
            DataConversionConstantA * float(iterable - DataConversionConstantB)
        )
        for iterable in WaterLevel
    ]

    BatteryVoltage = [
        prettifyNumber(iterable * BatteryVoltageConstant) for iterable in BatteryVoltage
    ]

    DB_Data["WaterLevel"] = WaterLevel
    DB_Data["BatteryVoltage"] = BatteryVoltage

    return [DB_Data, GCOM_Packages, DeviceSettings]


def get_data(device_id):
    if device_id == "" or device_id == None:
        return None

    server = os.environ.get("DB_SERVER")
    catalog = os.environ.get("DB_CATALOG")
    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")

    connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};Server={server};Initial Catalog={catalog};Persist Security Info=False;UID={username};PWD={password};MultipleActiveResultSets=True;Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"

    db_connection = pyodbc.connect(connection_string)

    device_settings = pd.read_sql(
        """
    SELECT *
    FROM tanktoad_crm_test.dbo.DeviceSettings
    WHERE Id ="""
        + str(device_id)
        + """;
    """,
        db_connection,
    )

    if device_settings["Id"].values[0] == "" or device_settings["Id"].values[0] == None:
        return None

    serial_num = device_settings["SerialNumber"].values[0]
    IMEI = device_settings["IMEI"].values[0]

    data_conversion_constant_a = device_settings["DataConversionConstantA"].values[0]
    data_conversion_constant_b = device_settings["DataConversionConstantB"].values[0]

    connection_type = device_settings["ConnectionType"].values[0]

    data = pd.read_sql(
        """
    SELECT WaterLevel, BatteryVoltage, Timestamp
    FROM tanktoad_crm_test.dbo.SensorData
    WHERE Wm6_DeviceSettingId ="""
        + str(device_id)
        + """;
    """,
        db_connection,
    )

    for i in range(len(data["Timestamp"].values)):
        timestamp = pd.Timestamp(data["Timestamp"].values[i])
        timestamp = timestamp.round(freq="H")

        data["Timestamp"].values[i] = timestamp

    data = pd.DataFrame(data).set_index("Timestamp")
    data = validate_series(data)

    # Get stats GCOM Packages
    def get_statistic_satellite_device():
        HistoriesLogs = pd.read_sql(
            """
        SELECT *
        FROM tanktoad_crm_test.dbo.Histories
        WHERE Wm6_DeviceSettingId ="""
            + str(device_id)
            + """;
        """,
            db_connection,
        )

        def sum_bytes(series):
            return len(reduce(lambda x, y: x + y, series))

        SentBytesArr = HistoriesLogs[
            HistoriesLogs["From"].str.contains("Server")
        ].fillna("")
        ReceivedBytesArr = HistoriesLogs[
            HistoriesLogs["From"].str.contains("Rock7")
        ].fillna("")

        ReceivedBytesArr["DateReceive"] = pd.to_datetime(
            ReceivedBytesArr["DateReceive"]
        ).dt.date
        SentBytesArr["DateReceive"] = pd.to_datetime(
            SentBytesArr["DateReceive"]
        ).dt.date

        ReceivedBytesArr = (
            ReceivedBytesArr.groupby([ReceivedBytesArr["DateReceive"]])
            .agg({"Body": sum_bytes})
            .fillna(0)
        )

        SentBytesArr = (
            SentBytesArr.groupby([SentBytesArr["DateReceive"]])
            .agg({"Body": sum_bytes})
            .fillna(0)
        )

        DataFrame = (
            (ReceivedBytesArr + SentBytesArr)
            .fillna(ReceivedBytesArr)
            .fillna(SentBytesArr)
        )
        DataFrame.rename(columns={"Body": "TotalBytes"}, inplace=True)
        DataFrame.index.names = ["Timestamp"]

        return DataFrame

    def get_statistic_cellular_device():
        cutie_logs = pd.read_sql(
            """
        SELECT *
        FROM tanktoad_crm_test.dbo.CutieLog
        WHERE Wm6_DeviceSettingId ="""
            + str(device_id)
            + """;
        """,
            db_connection,
        )

        filter = cutie_logs["Type"] == 2
        SentBytesArr = cutie_logs.where(filter).dropna()

        filter = cutie_logs["Type"] == 1
        ReceivedBytesArr = cutie_logs.where(filter).dropna()

        ReceivedBytesArr["Date"] = pd.to_datetime(ReceivedBytesArr["Date"]).dt.date
        SentBytesArr["Date"] = pd.to_datetime(SentBytesArr["Date"]).dt.date

        def sum_bytes(series):
            return len(reduce(lambda x, y: x + y, series))

        ReceivedBytesArr = ReceivedBytesArr.groupby([ReceivedBytesArr["Date"]]).agg(
            {"Message": sum_bytes}
        )
        SentBytesArr = SentBytesArr.groupby([SentBytesArr["Date"]]).agg(
            {"Message": sum_bytes}
        )

        DataFrame = (
            (ReceivedBytesArr + SentBytesArr)
            .fillna(ReceivedBytesArr)
            .fillna(SentBytesArr)
        )

        DataFrame.rename(columns={"Message": "TotalBytes"}, inplace=True)
        DataFrame.index.names = ["Timestamp"]

        return DataFrame

    def get_GCOM_data():
        # Satellite
        if connection_type == 0:
            return get_statistic_satellite_device()

        # Cellular
        if connection_type == 1:
            return get_statistic_cellular_device()

    GCOM_PACKAGES = get_GCOM_data()

    return _normalize_data(
        [
            data,
            GCOM_PACKAGES,
            {
                "SerialNumber": serial_num,
                "IMEI": IMEI,
                "DataConversionConstantA": data_conversion_constant_a,
                "DataConversionConstantB": data_conversion_constant_b,
            },
        ]
    )

