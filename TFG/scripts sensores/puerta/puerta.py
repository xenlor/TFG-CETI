import paho.mqtt.client as mqtt
import time
import random

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/puerta"

client = mqtt.Client("sim_puerta")
client.connect(BROKER, 1883, 60)

print("🚀 Iniciando simulación benigna de puerta...")
estado = "CERRADO"
while True:
    client.publish(TOPIC, estado)
    print(f"[puerta] {estado}")
    estado = "ABIERTO" if estado == "CERRADO" else "CERRADO"
    time.sleep(random.randint(30,80))  # 5 segundos entre cambios
