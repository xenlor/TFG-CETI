
import paho.mqtt.client as mqtt
import time
import random

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/humedad"

client = mqtt.Client("cliente_ataque")
client.connect(BROKER, 1883, 60)

print("🚀 Iniciando simulación benigna de humedad...")
while True:
    h = round(random.uniform(40.0, 80.0), 2)
    client.publish(TOPIC, str(h))
    print(f"[humedad] {h}%")
    time.sleep(random.randint(30,60))  # 2 segundos entre lecturas
