import json
import joblib
import pandas as pd
from datetime import datetime
import time
import math
from elasticsearch import Elasticsearch
import requests

# ------------------------------
# ELASTIC
# ------------------------------
es = Elasticsearch("https://localhost:9200",
                   basic_auth=("elastic","s71i2Hvh=gnd2*n1MlP3"),
                   verify_certs=False)
indice_alertas = "iot-ml-alerts"

# ------------------------------
# TELEGRAM
# ------------------------------
TELEGRAM_TOKEN   = "8138414918:AAGGOE8XpikbdooB9Cvgp5HnD14WWMr-a30"
TELEGRAM_CHAT_ID = "6577106924"
def enviar_alerta_telegram(mensaje: str):
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                 params={"chat_id": TELEGRAM_CHAT_ID,"text":mensaje})

# ------------------------------
# MODELO
# ------------------------------
modelo = joblib.load("../modelos/modelo_temperatura.pkl")
print("✅ Modelo de temperatura cargado correctamente.")

# ------------------------------
# GLOBALES
# ------------------------------
eve_log          = "/var/log/suricata/eve.json"
ultimo_timestamp = None
ultimo_temp      = None
contador_ataques = 0
UMBRAL           = 3

# ------------------------------
# ALERTA ELASTIC
# ------------------------------
def enviar_alerta_elastic(sensor: str, pred: int, valor: float, delta_time: float, src_ip: str):
    doc = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "sensor": sensor,
        "resultado": "ataque" if pred==1 else "normal",
        "valor": valor if not (isinstance(valor,float) and math.isnan(valor)) else -1,
        "delta_time": delta_time,
        "src_ip": src_ip
    }
    es.index(index=indice_alertas, document=doc)

# ------------------------------
# PREPROC EVENTO
# ------------------------------
def preprocesar_evento(evento: dict)->pd.DataFrame|None:
    global ultimo_timestamp, ultimo_temp

    mqtt_pub = evento.get("mqtt",{}).get("publish")
    if not mqtt_pub or mqtt_pub.get("topic")!="iot/sensor/temperatura":
        return None

    msg = mqtt_pub.get("message","")
    try:
        temp = float(msg)
    except ValueError:
        print(f"⚠️ Payload inválido TEMPERATURA: '{msg}' → ataque")
        enviar_alerta_telegram(f"🚨 Invalid payload TEMPERATURA: '{msg}' (IP {evento.get('src_ip','-')})")
        es.index(index=indice_alertas, document={
            "timestamp": datetime.now().astimezone().isoformat(),
            "sensor":"temperatura",
            "resultado":"ataque",
            "payload": msg,
            "src_ip": evento.get("src_ip","")
        })
        return None

    ts = datetime.strptime(evento["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z") - pd.Timedelta(hours=2)
    if ultimo_timestamp:
        dt = (ts-ultimo_timestamp).total_seconds()
        if dt<0.01 and temp==ultimo_temp:
            return None
    else:
        dt = 10.0

    ultimo_timestamp, ultimo_temp = ts, temp
    return pd.DataFrame([[temp,dt]],columns=["temperature","delta_time"])

# ------------------------------
# BUCLE PRINCIPAL
# ------------------------------
with open(eve_log,"r") as f:
    f.seek(0,2)
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.1); continue
        try: evento = json.loads(line)
        except: continue
        if evento.get("event_type")!="mqtt":
            continue

        src_ip = evento.get("src_ip","")
        X = preprocesar_evento(evento)
        if X is None:
            continue

        pred    = modelo.predict(X)[0]
        val     = X.at[0,"temperature"]
        dt_act  = X.at[0,"delta_time"]
        icono   = "🚨 ATAQUE" if pred==1 else "✅ Normal"

        print(f"{icono} → Temp: {val}, Δt: {dt_act:.3f}s (IP {src_ip})")
        enviar_alerta_elastic("temperatura",pred,val,dt_act,src_ip)

        if pred==1:
            contador_ataques+=1
            if contador_ataques>=UMBRAL:
                enviar_alerta_telegram(f"🚨 ¡{UMBRAL} ataques seguidos TEMPERATURA! IP: {src_ip}")
                contador_ataques=0
        else:
            contador_ataques=0
