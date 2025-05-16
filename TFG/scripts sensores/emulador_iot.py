import paho.mqtt.client as mqtt
import time
import random
import threading

BROKER = "192.168.1.10"

def sensor_temperatura():
    try:
        client = mqtt.Client("sensor_temp")
        client.connect(BROKER, 1883, 60)
        print("✅ Sensor temperatura iniciado")
        while True:
            temp = round(random.uniform(18.0, 30.0), 2)
            client.publish("iot/sensor/temperatura", str(temp))
            print(f"[temperatura] {temp} ºC")
            time.sleep(random.randint(20, 40))
    except Exception as e:
        print(f"❌ Error en sensor temperatura: {e}")

def sensor_humedad():
    try:
        client = mqtt.Client("sensor_humedad")
        client.connect(BROKER, 1883, 60)
        print("✅ Sensor humedad iniciado")
        while True:
            humedad = random.randint(40, 80)
            client.publish("iot/sensor/humedad", str(humedad))
            print(f"[humedad] {humedad}%")
            time.sleep(random.randint(30, 60))
    except Exception as e:
        print(f"❌ Error en sensor humedad: {e}")

def sensor_movimiento():
    try:
        client = mqtt.Client("sensor_movimiento")
        client.connect(BROKER, 1883, 60)
        print("✅ Sensor movimiento iniciado")
        while True:
            estado = random.choice(["ON", "OFF"])
            client.publish("iot/sensor/movimiento", estado)
            print(f"[movimiento] {estado}")
            time.sleep(random.randint(30, 60))
    except Exception as e:
        print(f"❌ Error en sensor movimiento: {e}")

def sensor_puerta():
    try:
        client = mqtt.Client("sensor_puerta")
        client.connect(BROKER, 1883, 60)
        print("✅ Sensor puerta iniciado")
        while True:
            hora_actual = time.localtime().tm_hour
            if 1 <= hora_actual <= 5:
                estado = "CERRADO"
            else:
                estado = random.choice(["ABIERTO", "CERRADO"])
            client.publish("iot/sensor/puerta", estado)
            print(f"[puerta] {estado} (hora: {hora_actual})")
            time.sleep(random.randint(30, 80))
    except Exception as e:
        print(f"❌ Error en sensor puerta: {e}")

# -----------------------
# Lanzar los hilos
# -----------------------
threads = [
    threading.Thread(target=sensor_temperatura),
    threading.Thread(target=sensor_humedad),
    threading.Thread(target=sensor_movimiento),
    threading.Thread(target=sensor_puerta)
]

for t in threads:
    t.start()

for t in threads:
    t.join()
