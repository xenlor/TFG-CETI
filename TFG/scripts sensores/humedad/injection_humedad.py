#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/humedad"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

payloads = ["abc", "--", "NULL", "{}"]

print("→ Iniciando Injection Humedad MQTT")
for p in payloads:
    client.publish(TOPIC, p)
    print(f"📡 Injection HUM → {p}")
    time.sleep(0.5)
