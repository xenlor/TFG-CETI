import pandas as pd

# 🟢 Rutas de los archivos
logs_benignos = "../csv/logs_convertidos_TON_IoT.csv"
logs_ton = "../csv/Train_Test_IoT_Garage_Door.csv"
archivo_salida = "../csv/dataset_combinado_puerta.csv"

# 📂 Cargar los datasets
df_benignos = pd.read_csv(logs_benignos)
df_ton = pd.read_csv(logs_ton)

# ✨ LIMPIEZA: quitar espacios en columnas string (importante para evitar errores)
df_benignos = df_benignos.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
df_ton = df_ton.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# 🛠️ Corregir 'sphone_signal'
df_ton["sphone_signal"] = df_ton["sphone_signal"].replace({"true": 1, "false": 0}).astype(int)

# ⏱️ Extraer hora, minuto, segundo
df_benignos["hour"] = pd.to_datetime(df_benignos["time"], format="%H:%M:%S").dt.hour
df_benignos["minute"] = pd.to_datetime(df_benignos["time"], format="%H:%M:%S").dt.minute
df_benignos["second"] = pd.to_datetime(df_benignos["time"], format="%H:%M:%S").dt.second

df_ton["hour"] = pd.to_datetime(df_ton["time"], format="%H:%M:%S").dt.hour
df_ton["minute"] = pd.to_datetime(df_ton["time"], format="%H:%M:%S").dt.minute
df_ton["second"] = pd.to_datetime(df_ton["time"], format="%H:%M:%S").dt.second

# 📅 Extraer weekday
df_benignos["weekday"] = pd.to_datetime(df_benignos["date"], format="%d-%b-%y").dt.weekday
df_ton["weekday"] = pd.to_datetime(df_ton["date"], format="%d-%b-%y").dt.weekday

# 🟠 Calcular delta_time (diferencia entre eventos consecutivos por fecha y hora)
def calcular_delta(df):
    df = df.sort_values(by=["date", "time"]).reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"], format="%d-%b-%y %H:%M:%S")
    df["delta_time"] = df["datetime"].diff().dt.total_seconds().fillna(999)
    return df.drop(columns=["datetime"])

df_benignos = calcular_delta(df_benignos)
df_ton = calcular_delta(df_ton)

# 🟢 Combinar ambos datasets tal cual, sin tocar duplicados
df = pd.concat([df_benignos, df_ton], ignore_index=True)
print(f"📌 Total registros combinados (sin eliminar duplicados): {len(df)}")

# 🔢 Codificar 'door_state'
df["door_state_encoded"] = df["door_state"].map({"open": 1, "closed": 0})

# 🗑️ Eliminar columnas que ya no necesitas para el modelo
df = df.drop(columns=["date", "time", "sphone_signal"])

# 💾 Guardar dataset combinado y limpio (sin eliminar duplicados)
df.to_csv(archivo_salida, index=False)
print(f"✅ Dataset combinado y guardado como: {archivo_salida}")

