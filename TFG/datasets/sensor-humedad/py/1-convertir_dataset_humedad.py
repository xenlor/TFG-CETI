import pandas as pd
from datetime import datetime

# 📂 Ruta de tu CSV original
input_path = "../csv/logs_suricata_sensor_humedad.csv"
output_path = "../csv/logs_suricata_sensor_humedad_convertido.csv"

# 🟢 Cargar el CSV
df = pd.read_csv(input_path)

# 🟢 Función para convertir timestamp al formato deseado
def convertir_fecha(ts):
    dt = datetime.strptime(ts, "%b %d, %Y @ %H:%M:%S.%f")
    return dt.strftime("%d-%b-%y"), dt.strftime("%H:%M:%S")

# 🟢 Aplicar la conversión de timestamp
df[["date", "time"]] = df["@timestamp"].apply(lambda x: pd.Series(convertir_fecha(x)))

# 🟢 El valor de humedad es el mensaje publicado (puede ser numérico o string)
df["humidity"] = df["mqtt.publish.message"]

# 🟢 Etiquetar todo como benigno
df["label"] = 0
df["type"] = "normal"

# 🟢 Seleccionar las columnas en el orden que quieres
df = df[["date", "time", "humidity", "label", "type"]]

# 💾 Guardar el CSV convertido
df.to_csv(output_path, index=False)
print(f"✅ Dataset de humedad convertido y guardado como '{output_path}'")
