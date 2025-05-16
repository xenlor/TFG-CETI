#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import random

BROKER = "192.168.1.10"
TOPIC  = "iot/sensor/temperatura"
BURST_SIZE = 25      # número de paquetes en la ráfaga
INTERVAL = 0.005       # intervalo entre mensajes (en segundos)

def main():
    client = mqtt.Client()
    client.connect(BROKER, 1883, 60)

    print("→ Lanzando ráfaga única de ataque MQTT (temperatura)")
    for i in range(BURST_SIZE):
        val = random.uniform(40.0, 100.0)       # rango 40-100 °C
        payload = f"{val:.2f}"
        client.publish(TOPIC, payload)
        print(f"📡 [{i+1}/{BURST_SIZE}] → {payload} °C")
        time.sleep(INTERVAL)

    print("→ Ráfaga completada. Saliendo.")
    client.disconnect()

if __name__ == "__main__":
    main()
