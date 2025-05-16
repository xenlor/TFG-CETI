#!/usr/bin/env python3
import json
import joblib
import pandas as pd
from datetime import datetime
import time
import math
import requests
from elasticsearch import Elasticsearch

# ——————————————————————————————
# CONFIGURACIÓN
# ——————————————————————————————
TELEGRAM_TOKEN = "8138414918:AAGGOE8XpikbdooB9Cvgp5HnD14WWMr-a30"
CHAT_ID       = "6577106924"
ES_URL        = "https://localhost:9200"
ES_USER       = "elastic"
ES_PASS       = "s71i2Hvh=gnd2*n1MlP3"
INDICE        = "iot-ml-alerts"
UMBRAL        = 3

# ——————————————————————————————
# CLIENTE ELASTICSEARCH
# ——————————————————————————————
es = Elasticsearch(ES_URL, basic_auth=(ES_USER, ES_PASS), verify_certs=False)

# ——————————————————————————————
# HELPER TELEGRAM
# ——————————————————————————————
def send_block_prompt(ip: str):
    kb = {
      "inline_keyboard": [
        [
          {"text":"✅ Bloquear", "callback_data":f"confirm_block:{ip}"},
          {"text":"❌ Cancelar",  "callback_data":f"cancel_block:{ip}"}
        ]
      ]
    }
    payload = {
      "chat_id": CHAT_ID,
      "text": f"🚨 Se han detectado *{UMBRAL} ataques consecutivos* desde la IP *{ip}* en el sensor MOVIMIENTO.\n¿Deseas bloquearla?",
      "parse_mode": "Markdown",
      "reply_markup": kb
    }
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json=payload)

# ——————————————————————————————
# INDEXAR EN ELASTICSEARCH
# ——————————————————————————————
def indexar_elastic(sensor: str, pred: int, valor: int, delta_time: float, src_ip: str):
    doc = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "sensor": sensor,
        "resultado": "ataque" if pred == 1 else "normal",
        "valor": valor,
        "delta_time": delta_time,
        "src_ip": src_ip
    }
    es.index(index=INDICE, document=doc)

# ——————————————————————————————
# CARGAR MODELO
# ——————————————————————————————
modelo = joblib.load("../modelos/modelo_movimiento.pkl")
print("✅ Modelo de movimiento cargado correctamente.")

# ——————————————————————————————
# VARIABLES GLOBALES
# ——————————————————————————————
EVE_LOG       = "/var/log/suricata/eve.json"
ultimo_ts     = None
ultimo_status = None
cont_ataques  = 0

# ——————————————————————————————
# PREPROCESAMIENTO
# ——————————————————————————————
def preprocesar_evento(evt: dict):
    global ultimo_ts, ultimo_status
    if evt.get("event_type") != "mqtt":
        return None
    pub = evt.get("mqtt",{}).get("publish")
    if not pub or pub.get("topic") != "iot/sensor/movimiento":
        return None

    msg = pub.get("message","").upper()
    if msg == "ON":
        status = 1
    elif msg == "OFF":
        status = 0
    else:
        status = -1

    ts = datetime.strptime(evt["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z") - pd.Timedelta(hours=2)
    if ultimo_ts is None:
        dt = 10.0
    else:
        dt = (ts - ultimo_ts).total_seconds()
        if dt < 0.01 and status == ultimo_status:
            return None

    ultimo_ts     = ts
    ultimo_status = status
    return pd.DataFrame([[status, dt]], columns=["motion_status","delta_time"])

# ——————————————————————————————
# BUCLE PRINCIPAL
# ——————————————————————————————
with open(EVE_LOG, "r") as f:
    f.seek(0, 2)
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.1)
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue

        df_evt = preprocesar_evento(evt)
        if df_evt is None:
            continue

        pred = modelo.predict(df_evt)[0]
        val  = df_evt.at[0,"motion_status"]
        dt   = df_evt.at[0,"delta_time"]
        ip   = evt.get("src_ip","-")
        icon = "🚨 ATAQUE" if pred == 1 else "✅ Normal"
        print(f"{icon} → Motion={val}, Δt={dt:.3f}s (IP {ip})")

        # indexar
        indexar_elastic("movimiento", pred, val, dt, ip)

        if pred == 1:
            cont_ataques += 1
            if cont_ataques >= UMBRAL:
                send_block_prompt(ip)
                cont_ataques = 0
        else:
            cont_ataques = 0
