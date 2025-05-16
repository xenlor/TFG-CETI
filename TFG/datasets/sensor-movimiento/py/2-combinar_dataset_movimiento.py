import pandas as pd

# 📂 Rutas de los archivos
suricata_path = "../csv/logs_suricata_movimiento_convertido.csv"
ton_iot_path = "../csv/Train_Test_IoT_Motion_Light.csv"
output_path = "../csv/dataset_combinado_movimiento.csv"

# 🟢 Cargar los datasets
df_suricata = pd.read_csv(suricata_path)
df_ton = pd.read_csv(ton_iot_path)

print(f"✅ Dataset Suricata cargado: {len(df_suricata)} registros")
print(f"✅ Dataset TON_IoT cargado: {len(df_ton)} registros")

# 🟥 Filtrar TON_IoT (quitar label = 0 → dejar solo ataques)
df_ton = df_ton[df_ton["label"] == 1].reset_index(drop=True)

# 🟢 Renombrar columnas para que coincidan con Suricata
df_ton = df_ton.rename(columns={
    "motion_status": "motion_status",
    "light_status": "light_status",
    "label": "label",
    "type": "type",
    "time": "time",
    "date": "date"
})

df_ton = df_ton[["date", "time", "motion_status", "light_status", "label", "type"]]
df_suricata = df_suricata[["date", "time", "motion_status", "light_status", "label", "type"]]

# 🟢 Combinar los dos datasets
df_combinado = pd.concat([df_suricata, df_ton], ignore_index=True)
print(f"✅ Dataset combinado: {len(df_combinado)} registros")

# 🟥 Eliminar duplicados (por date, time y motion_status)
df_combinado = df_combinado.drop_duplicates(subset=["date", "time", "motion_status"]).copy()
print(f"✅ Registros después de eliminar duplicados: {len(df_combinado)}")

# 🟠 Limpiar espacios en 'time'
df_combinado.loc[:, "time"] = df_combinado["time"].astype(str).str.strip()

# 🟢 Calcular delta_time
df_combinado = df_combinado.sort_values(by=["date", "time"]).reset_index(drop=True)
df_combinado["datetime"] = pd.to_datetime(df_combinado["date"] + " " + df_combinado["time"], format="%d-%b-%y %H:%M:%S")
df_combinado["delta_time"] = df_combinado["datetime"].diff().dt.total_seconds().fillna(999)
df_combinado = df_combinado.drop(columns=["datetime"])

# 💾 Guardar el dataset combinado listo para entrenar
df_combinado.to_csv(output_path, index=False)
print(f"✅ Dataset combinado, filtrado y listo guardado como '{output_path}'")
