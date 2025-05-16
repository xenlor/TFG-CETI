import pandas as pd
from datetime import datetime

# 🟢 Rutas de los archivos
archivo_entrada = "../csv/logs_suricata_puerta.csv"
archivo_salida = "../csv/logs_convertidos_TON_IoT.csv"

# 🟢 Cargar el CSV exportado desde Suricata
df = pd.read_csv(archivo_entrada)

# 🟢 Función para convertir el timestamp al formato de TON_IoT
def convertir_fecha(ts):
    try:
        dt = datetime.strptime(ts, "%b %d, %Y @ %H:%M:%S.%f")
        fecha = dt.strftime("%d-%b-%y")  # Ej: 23-Apr-25
        hora = dt.strftime("%H:%M:%S")   # Ej: 05:03:27
        return fecha, hora
    except Exception as e:
        print(f"Error al convertir timestamp: {e}")
        return None, None

# 🟢 Aplicar la conversión de fecha y hora
df[["date", "time"]] = df["@timestamp"].apply(lambda x: pd.Series(convertir_fecha(x)))

# 🟢 Mapear el estado (ABIERTO / CERRADO)
def mapear_estado(msg):
    msg = str(msg).strip().upper()
    if msg == "ABIERTO":
        return "open"
    elif msg == "CERRADO":
        return "closed"
    else:
        return "unknown"

df["door_state"] = df["mqtt.publish.message"].apply(mapear_estado)

# 🟢 Añadir las columnas extra del formato TON_IoT
df["sphone_signal"] = 0
df["label"] = 0  # Todo tu tráfico es benigno
df["type"] = "normal"

# 🟢 EXTRAER hour, minute, second
df["hour"] = pd.to_datetime(df["time"], format="%H:%M:%S").dt.hour
df["minute"] = pd.to_datetime(df["time"], format="%H:%M:%S").dt.minute
df["second"] = pd.to_datetime(df["time"], format="%H:%M:%S").dt.second

# 🟠 CALCULAR delta_time (ordenando por fecha y hora)
df = df.sort_values(by=["date", "time"]).reset_index(drop=True)
# Combinar 'date' y 'time' para hacer el datetime completo:
df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"], format="%d-%b-%y %H:%M:%S")

# Calcular diferencia entre cada fila y la anterior (en segundos)
df["delta_time"] = df["datetime"].diff().dt.total_seconds()
# Poner -1 en el primer registro (porque no hay anterior)
df["delta_time"] = df["delta_time"].fillna(-1)

# 🗑️ Eliminar 'datetime' si no quieres que aparezca en el CSV final
df = df.drop(columns=["datetime"])

# 🟢 Guardar el resultado final
df_final = df[["date", "time", "door_state", "sphone_signal", "label", "type", "hour", "minute", "second", "delta_time"]]
df_final.to_csv(archivo_salida, index=False)
print(f"✅ Archivo convertido y guardado como: {archivo_salida}")

