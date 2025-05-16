import pandas as pd
from datetime import datetime

# 📂 Ruta del dataset del sensor de temperatura (Suricata)
input_path = "../csv/logs_suricata_sensor_temperatura.csv"
output_path = "../csv/logs_suricata_sensor_temperatura_convertido.csv"

# 🟢 Cargar el CSV
df = pd.read_csv(input_path)

# 🟢 Función para convertir timestamp al formato deseado
def convertir_fecha(ts):
    dt = datetime.strptime(ts, "%b %d, %Y @ %H:%M:%S.%f")
    return dt.strftime("%d-%b-%y"), dt.strftime("%H:%M:%S")

# 🟢 Procesar dataset: extraer fecha y hora
df[["date", "time"]] = df["@timestamp"].apply(lambda x: pd.Series(convertir_fecha(x)))

# 🟢 Extraer la temperatura desde el mensaje publicado
df["temperature"] = df["mqtt.publish.message"].apply(lambda x: float(str(x).strip()))

# 🟢 Etiquetar todo como benigno
df["label"] = 0
df["type"] = "normal"

# 🟢 Seleccionar las columnas necesarias en el orden del TON_IoT
df = df[["date", "time", "temperature", "label", "type"]]

# 💾 Guardar el CSV convertido
df.to_csv(output_path, index=False)
print(f"✅ Dataset de temperatura convertido y guardado como '{output_path}'")
