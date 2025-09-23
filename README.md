# Implementación y Análisis de Seguridad en una Red IoT Simulada utilizando ML (RandomTree)

![status](https://img.shields.io/badge/status-active-brightgreen)
![license](https://img.shields.io/badge/license-MIT-blue)
![docker](https://img.shields.io/badge/docker-ready-blue)
![python](https://img.shields.io/badge/python-3.11%2B-yellow)

## 📌 Descripción del Proyecto

Este repositorio contiene el Trabajo de Fin de Grado de **Esteban Castillo Loren**, cuyo objetivo es **implementar y analizar la seguridad en una red IoT simulada utilizando Raspberry Pi y técnicas de Machine Learning**.  
El proyecto reproduce un entorno que emula dispositivos IoT, captura tráfico de red y detecta anomalías mediante un pipeline basado en Suricata, ELK Stack y modelos de aprendizaje automático.

## 🎯 Objetivos

- Simular una red IoT doméstica con dispositivos reales y emulados.
- Capturar tráfico de red y eventos de seguridad con **Suricata**.
- Integrar los logs en **Elasticsearch + Kibana** para su visualización.
- Entrenar y desplegar modelos de **Machine Learning** para clasificación de tráfico.
- Documentar arquitectura, metodología y resultados de la detección.

## 🏗️ Arquitectura del Proyecto

El entorno está compuesto por:

- **Broker MQTT (Mosquitto)** – Comunicación entre dispositivos IoT.
- **Suricata IDS** – Captura de tráfico y generación de eventos.
- **ELK Stack (Elasticsearch, Logstash, Kibana)** – Centralización y visualización de datos.
- **Modelos ML (scikit-learn/TensorFlow)** – Clasificación de tráfico en tiempo real.
- **Dashboards en Kibana** – Análisis visual de actividad IoT y alertas.

Consulta el diagrama de arquitectura en la carpeta `docs/`.

## 🛠️ Tecnologías Utilizadas

- **Hardware:** Raspberry Pi 4B/5, switch gestionable TP-Link con port mirroring.
- **Software:** Docker, Suricata, ELK, Mosquitto, Python 3.11
- **Librerías ML:** scikit-learn, pandas, numpy, matplotlib
- **Dataset:** TON_IoT (Train_Test_datasets)

## 📂 Estructura del Repositorio

```bash
TFG-CETI-main/
├── .gitattributes
├── README.md
├── TFG/
│   ├── requirements.txt
│   ├── setup.sh
│   ├── .config/
│   │   ├── kibana.yml
│   │   ├── pipelines.yml
│   │   ├── remote.conf
│   │   ├── suricata.conf
│   │   └── suricata.yaml
│   ├── datasets/
│   │   ├── Train_Test_IoT_dataset/
│   │   │   ├── Train_Test_IoT_Fridge.csv
│   │   │   ├── Train_Test_IoT_GPS_Tracker.csv
│   │   │   ├── Train_Test_IoT_Modbus.csv
│   │   │   ├── Train_Test_IoT_Motion_Light.csv
│   │   │   ├── Train_Test_IoT_Thermostat.csv
│   │   │   └── Train_Test_IoT_Weather.csv
│   │   ├── ejecutar_modelo/
│   │   │   ├── 4-ejecutar_modelo_humedad.py
│   │   │   ├── 4-ejecutar_modelo_movimiento.py
│   │   │   ├── 4-ejecutar_modelo_puerta.py
│   │   │   ├── 4-ejecutar_modelo_temperatura.py
│   │   │   ├── bot-telegram.py
│   │   │   └── ejecutar_modelos.sh
│   │   ├── modelos/
│   │   │   ├── modelo_humedad.pkl
│   │   │   ├── modelo_movimiento.pkl
│   │   │   ├── modelo_puerta.pkl
│   │   │   └── modelo_temperatura.pkl
│   │   ├── sensor-humedad/
│   │   │   ├── csv/
│   │   │   │   ├── dataset_combinado_humedad_sin_duplicados.csv
│   │   │   │   ├── logs_suricata_sensor_humedad.csv
│   │   │   │   ├── logs_suricata_sensor_humedad_convertido.csv
│   │   │   │   └── Train_Test_IoT_Weather.csv
│   │   │   ├── modelos/
│   │   │   │   └── modelo_humedad.pkl
│   │   │   └── py/
│   │   │       ├── 1-convertir_dataset_humedad.py
│   │   │       ├── 2-combinar_dataset_humedad.py
│   │   │       ├── 3-entrenar_modelo_humedad.py
│   │   │       ├── 4-ejecutar_modelo_humedad.py
│   │   │       └── bot.log
│   │   └── sensor-movimiento/...
└── docs/  # Diagramas y documentación técnica
````

## 🚀 Instalación y Ejecución

1. **Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/tfg-ciberseguridad.git
cd tfg-ciberseguridad/TFG
```

2. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

3. **Configurar Suricata**
   Edita `TFG/.config/suricata.yaml` para ajustar las redes monitorizadas.

4. **Entrenar modelos (opcional)**

```bash
python datasets/sensor-humedad/py/3-entrenar_modelo_humedad.py
python datasets/sensor-movimiento/py/3-entrenar_modelo_movimiento.py
# (repite para puerta y temperatura)
```

Cada script genera un `modelo_*.pkl` en la carpeta correspondiente.

5. **Ejecución en tiempo real**

```bash
cd datasets/ejecutar_modelo
sudo ./ejecutar_modelos.sh start   # inicia los 4 modelos y el pipeline
./ejecutar_modelos.sh stop         # detiene todo
```

## 📊 Resultados

* Dashboards en Kibana para visualizar tráfico IoT y alertas de Suricata.
* Métricas de precisión, recall y F1-score de los modelos entrenados.
* Comparativa entre tráfico normal y anómalo en entornos simulados.


## 📜 Licencia

Este proyecto está bajo licencia **MIT** – consulta [LICENSE](LICENSE) para más detalles.

```
