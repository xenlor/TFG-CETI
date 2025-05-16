#!/usr/bin/env python3
import json
import joblib
import pandas as pd
from datetime import datetime
import time
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
    kb = {
        "inline_keyboard": [[
            {"text":"✅ Bloquear",    "callback_data":f"confirm_block:{ip}"},
            {"text":"❌ Cancelar",     "callback_data":f"cancel_block:{ip}"}
        ]]
    }
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": (
            f"🚨 Se han detectado *{UMBRAL} ataques consecutivos* "
            f"desde la IP *{ip}* en el sensor PUERTA.\n¿Deseas bloquearla?"
        ),
        "parse_mode": "Markdown",
        "reply_markup": kb
    }
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json=payload
    )

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
def preprocesar_evento(evt: dict) -> pd.DataFrame | int | None:
    """
    Devuelve un DataFrame con las features si es mensaje válido,
    o el entero 1 para forzar ataque en mensaje inválido,
    o None si no nos interesa procesar el evento.
    """
    global ultimo_timestamp, ultimo_door_state

    if evt.get("event_type") != "mqtt":
        return None

    pub = evt.get("mqtt", {}).get("publish")
    if not pub or pub.get("topic") != "iot/sensor/puerta":
        return None

    msg = pub.get("message", "").upper()
    ip  = evt.get("src_ip", "-")

    # Si payload inválido, lo contamos como un ataque forzado
    if msg not in ("ABIERTO", "CERRADO"):
        print(f"⚠️ Mensaje inválido en PUERTA ('{msg}'). Contando como ataque (IP {ip}).")
        return 1  # señal de ataque

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

    df = pd.DataFrame(
        [[door_state_encoded, hour, minute, second, weekday, delta_time]],
        columns=["door_state_encoded","hour","minute","second","weekday","delta_time"]
    )
    return df

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

        resultado = preprocesar_evento(evt)
        if resultado is None:
            continue

        ip = evt.get("src_ip", "-")

        # Si preprocesar_evento devolvió un int => ataque forzado
        if isinstance(resultado, int):
            pred = 1
            val  = -1         # valor marcador para ataque forzado
            dt   = -1.0
        else:
            # Resultado es un DataFrame válido
            df_evt = resultado
            pred    = modelo.predict(df_evt)[0]
            val     = int(df_evt.at[0, "door_state_encoded"])
            dt      = df_evt.at[0, "delta_time"]

        icon = "🚨 ATAQUE" if pred == 1 else "✅ Normal"
        print(f"{icon} → Puerta: {val}, Δt={dt:.3f}s (IP {ip})")

        # Indexar en ELK
        enviar_alerta_elastic(
            "puerta",
            pred,
            val if val is not None else -1,
            dt if dt is not None else -1,
            ip
        )

        # Lógica de bloqueo tras UMBRAL ataques consecutivos
        if pred == 1:
            contador_ataques += 1
            if contador_ataques >= UMBRAL:
                send_block_prompt(ip)
                contador_ataques = 0
        else:
            contador_ataques = 0
