import paho.mqtt.client as mqtt
import time
import random

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/movimiento"

client = mqtt.Client("sim_movimiento")
client.connect(BROKER, 1883, 60)

print("🚀 Iniciando simulación benigna de movimiento...")
estado = "OFF"
while True:
    client.publish(TOPIC, estado)
    print(f"[movimiento] {estado}")
    estado = "ON" if estado == "OFF" else "OFF"
    time.sleep(random.randint(30,60))  # 1 segundo entre eventos
