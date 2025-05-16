import paho.mqtt.client as mqtt
import time
import random

BROKER = "192.168.1.10"
TOPIC = "iot/sensor/temperatura"

client = mqtt.Client("ext_temp")
client.connect(BROKER, 1883, 60)

print("🚀 Iniciando ataque de temperaturas extremas aleatorias (40–100 °C)…")
while True:
    # Genera un valor aleatorio entre 40.0 y 100.0
    temp = round(random.uniform(40.0, 100.0), 2)
    client.publish(TOPIC, str(temp))
    print(f"[ext_temp] enviado: {temp}°C")
    # Espera un intervalo aleatorio entre 20 y 40 segundos
    time.sleep(random.randint(20,40))
