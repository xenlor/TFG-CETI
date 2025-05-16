import pandas as pd
from datetime import datetime

# 📂 Dataset de Suricata
suricata_path = "../csv/logs_suricata_movimiento.csv"
output_path = "../csv/logs_suricata_movimiento_convertido.csv"

# 🟢 Cargar el CSV
df = pd.read_csv(suricata_path)

# 🟢 Función para convertir timestamp al formato deseado
def convertir_fecha(ts):
    dt = datetime.strptime(ts, "%b %d, %Y @ %H:%M:%S.%f")
    return dt.strftime("%d-%b-%y"), dt.strftime("%H:%M:%S")

# 🟢 Procesar dataset
df[["date", "time"]] = df["@timestamp"].apply(lambda x: pd.Series(convertir_fecha(x)))
df["motion_status"] = df["mqtt.publish.message"].apply(lambda x: 1 if x.strip().upper() == "ON" else 0)
df["light_status"] = "off"
df["label"] = 0  # Todo es benigno
df["type"] = "normal"

# 🟢 Seleccionar las columnas necesarias
df = df[["date", "time", "motion_status", "light_status", "label", "type"]]

# 💾 Guardar el CSV convertido
df.to_csv(output_path, index=False)
print(f"✅ Dataset convertido y guardado como '{output_path}'")
