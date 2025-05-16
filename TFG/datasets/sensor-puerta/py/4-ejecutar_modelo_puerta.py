#!/usr/bin/env python3
import json
import joblib
import pandas as pd
from datetime import datetime
import time
import math
from elasticsearch import Elasticsearch
import requests

# ------------------------------
# CONEXIÓN A ELASTICSEARCH
# ------------------------------
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "s71i2Hvh=gnd2*n1MlP3"),
    verify_certs=False
)
indice_alertas = "iot-ml-alerts"

# ------------------------------
# CONFIGURACIÓN TELEGRAM
# ------------------------------
TELEGRAM_TOKEN   = "8138414918:AAGGOE8XpikbdooB9Cvgp5HnD14WWMr-a30"
TELEGRAM_CHAT_ID = "6577106924"
UMBRAL           = 3  # ataques consecutivos para disparar prompt

def send_block_prompt(ip: str):
    """Envía a Telegram el prompt con botones para bloquear o cancelar."""
    kb = {
        "inline_keyboard": [[
            {"text":"✅ Bloquear",    "callback_data":f"confirm_block:{ip}"},
            {"text":"❌ Cancelar",     "callback_data":f"cancel_block:{ip}"}
        ]]
    }
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": (
            f"🚨 Se han detectado *{UMBRAL} ataques consecutivos* desde la IP *{ip}* "
            "en el sensor PUERTA.\n¿Deseas bloquearla?"
        ),
        "parse_mode": "Markdown",
        "reply_markup": kb
    }
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json=payload
    )

# ------------------------------
# INDEXAR ALERTA EN ELASTICSEARCH
# ------------------------------
def enviar_alerta_elastic(sensor: str, pred: int, valor: int, delta_time: float, src_ip: str):
    doc = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "sensor": sensor,
        "resultado": "ataque" if pred == 1 else "normal",
        "valor": valor,
        "delta_time": delta_time,
        "src_ip": src_ip
    }
    es.index(index=indice_alertas, document=doc)

# ------------------------------
# CARGAR MODELO
# ------------------------------
modelo = joblib.load("../modelos/modelo_puerta.pkl")
print("✅ Modelo de puerta cargado correctamente.")

# ------------------------------
# VARIABLES GLOBALES
# ------------------------------
eve_log          = "/var/log/suricata/eve.json"
ultimo_timestamp = None
ultimo_door_state= None
contador_ataques = 0

# ------------------------------
# PREPROCESAR EVENTO
# ------------------------------
def preprocesar_evento(evt: dict) -> pd.DataFrame | None:
    global ultimo_timestamp, ultimo_door_state

    if evt.get("event_type") != "mqtt":
        return None

    pub = evt.get("mqtt", {}).get("publish")
    if not pub or pub.get("topic") != "iot/sensor/puerta":
        return None

    msg = pub.get("message", "").upper()

    # cualquier otro texto → ataque directo (ya lo indexas en tu flujo si quieres)
    if msg not in ("ABIERTO", "CERRADO"):
        print(f"⚠️ Mensaje no reconocido en PUERTA: '{msg}' → forzando ATAQUE")
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"🚨 Mensaje inválido en sensor PUERTA: '{msg}' (IP {evt.get('src_ip','-')})"
            }
        )
        es.index(index=indice_alertas, document={
            "timestamp": datetime.now().astimezone().isoformat(),
            "sensor": "puerta",
            "resultado": "ataque",
            "payload": msg,
            "src_ip": evt.get("src_ip","-")
        })
        return None

    door_state_encoded = 1 if msg == "ABIERTO" else 0

    # parse timestamp y ajustar zona
    ts = datetime.strptime(evt["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z") - pd.Timedelta(hours=2)
    hour, minute, second, weekday = ts.hour, ts.minute, ts.second, ts.weekday()

    # delta_time + deduplicado
    if ultimo_timestamp is None:
        delta_time = 10.0
    else:
        delta_time = (ts - ultimo_timestamp).total_seconds()
        if delta_time < 0.01 and door_state_encoded == ultimo_door_state:
            return None

    ultimo_timestamp   = ts
    ultimo_door_state  = door_state_encoded

    # devolvemos exactamente las 6 features
    return pd.DataFrame(
        [[door_state_encoded, hour, minute, second, weekday, delta_time]],
        columns=["door_state_encoded","hour","minute","second","weekday","delta_time"]
    )

# ------------------------------
# BUCLE PRINCIPAL (tail -f)
# ------------------------------
with open(eve_log, "r") as f:
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
        val  = int(df_evt.at[0, "door_state_encoded"])
        dt   = df_evt.at[0, "delta_time"]
        ip   = evt.get("src_ip","-")
        icon= "🚨 ATAQUE" if pred == 1 else "✅ Normal"

        # 1) consola
        print(f"{icon} → Puerta: {val}, Δt={dt:.3f}s (IP {ip})")

        # 2) indexar en ELK
        enviar_alerta_elastic("puerta", pred, val, dt, ip)

        # 3) al umbral → prompt de bloqueo
        if pred == 1:
            contador_ataques += 1
            if contador_ataques >= UMBRAL:
                send_block_prompt(ip)
                contador_ataques = 0
        else:
            contador_ataques = 0
