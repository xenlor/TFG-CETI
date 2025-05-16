import paho.mqtt.client as mqtt
import time
import random

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/temperatura"

client = mqtt.Client("sim_temperatura")
client.connect(BROKER, 1883, 60)

print("🚀 Iniciando simulación benigna de temperatura...")
while True:
    t = round(random.uniform(18.0, 30.0), 2)
    client.publish(TOPIC, str(t))
    print(f"[temperatura] {t}°C")
    time.sleep(random.randint(20,40))
