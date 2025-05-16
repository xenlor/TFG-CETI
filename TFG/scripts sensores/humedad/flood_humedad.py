#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import random

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/humedad"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

print("→ Iniciando Flood Humedad MQTT")
while True:
    for _ in range(60):
        val = random.uniform(30, 80)
        client.publish(TOPIC, f"{val:.2f}")
        print(f"📡 Flood HUM → {val:.2f}")
        time.sleep(0.005)
    time.sleep(1)
