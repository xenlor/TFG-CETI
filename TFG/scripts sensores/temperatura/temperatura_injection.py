#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/temperatura"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

payloads = ["hot", "cold", "error", "{}"]

print("→ Iniciando Injection Temperatura MQTT")
for p in payloads:
    client.publish(TOPIC, p)
    print(f"📡 Injection TMP → {p}")
    time.sleep(0.5)
