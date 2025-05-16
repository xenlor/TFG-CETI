#!/usr/bin/env python3
import json
import joblib
import pandas as pd
from datetime import datetime
import time
import math
from sklearn.tree import export_graphviz
import graphviz
import os
import requests

# ——————————————————————————————
# CONFIGURACIÓN TELEGRAM
# ——————————————————————————————
TELEGRAM_TOKEN = "8138414918:AAGGOE8XpikbdooB9Cvgp5HnD14WWMr-a30"
CHAT_ID       = "6577106924"
UMBRAL        = 3  # ataques consecutivos para disparar prompt

# ——————————————————————————————
# CARGAR MODELO
# ——————————————————————————————
modelo = joblib.load("../modelos/modelo_humedad.pkl")
print("✅ Modelo de humedad cargado correctamente.")

# ——————————————————————————————
# FUNCIONES AUXILIARES
# ——————————————————————————————
def send_block_prompt(ip: str):
    """Envía el mensaje con botones al canal de Telegram para bloquear o cancelar."""
    keyboard = {
      "inline_keyboard": [
        [
          {"text":"✅ Bloquear",    "callback_data":f"confirm_block:{ip}"},
          {"text":"❌ Cancelar",     "callback_data":f"cancel_block:{ip}"}
        ]
      ]
    }
    payload = {
      "chat_id": CHAT_ID,
      "text": f"🚨 Se han detectado *{UMBRAL} ataques consecutivos* desde la IP *{ip}*.\n¿Deseas bloquearla?",
      "parse_mode": "Markdown",
      "reply_markup": keyboard
    }
    requests.post(
      f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
      json=payload
    )

# ——————————————————————————————
# LECTURA EN TIEMPO REAL Y DETECCIÓN
# ——————————————————————————————
EVE_LOG       = "/var/log/suricata/eve.json"
ultimo_ts     = None
ultimo_val    = None
cont_ataques  = 0

def preprocesar_evento(evt: dict):
    """Extrae humidity y delta_time o devuelve None si no aplica."""
    global ultimo_ts, ultimo_val

    if evt.get("event_type")!="mqtt":
        return None
    pub = evt.get("mqtt",{}).get("publish")
    if not pub or pub.get("topic")!="iot/sensor/humedad":
        return None

    # valor numérico o NaN
    msg = pub.get("message","")
    try:
        val = float(msg)
    except:
        val = float("nan")

    # timestamp y ajuste zona
    ts = datetime.strptime(evt["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")
    ts = ts - pd.Timedelta(hours=2)

    # delta_time + filtrado de duplicados
    if ultimo_ts is None:
        dt = 10.0
    else:
        dt = (ts-ultimo_ts).total_seconds()
        if dt<0.01 and val==ultimo_val:
            return None

    ultimo_ts = ts
    ultimo_val= val
    return pd.DataFrame([[val,dt]], columns=["humidity","delta_time"])

with open(EVE_LOG,"r") as f:
    f.seek(0,2)
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
        val  = df_evt.at[0,"humidity"]
        dt   = df_evt.at[0,"delta_time"]
        ip   = evt.get("src_ip","-")
        icon = "🚨 ATAQUE" if pred==1 else "✅ Normal"
        print(f"{icon} → Humedad={val:.2f}, Δt={dt:.3f}s (IP {ip})")

        # contador y, al umbral, prompt de bloqueo
        if pred==1:
            cont_ataques += 1
            if cont_ataques >= UMBRAL:
                send_block_prompt(ip)
                cont_ataques = 0
        else:
            cont_ataques = 0
