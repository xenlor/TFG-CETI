#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import random

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/puerta"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

print("→ Iniciando Flood Puerta MQTT")
while True:
    for _ in range(80):
        msg = random.choice(["ABIERTO","CERRADO"])
        client.publish(TOPIC, msg)
        print(f"📡 Flood PRT → {msg}")
        time.sleep(0.005)
    time.sleep(1)
