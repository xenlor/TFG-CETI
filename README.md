# Implementación y Análisis de Seguridad en una Red IoT Simulada

![banner](https://img.shields.io/badge/status-active-brightgreen)
![license](https://img.shields.io/badge/license-MIT-blue)
![docker](https://img.shields.io/badge/docker-ready-blue)
![python](https://img.shields.io/badge/python-3.11%2B-yellow)

## 📌 Descripción del Proyecto

Este repositorio contiene mi Trabajo de Fin de Grado, cuyo objetivo es **implementar y analizar la seguridad en una red IoT simulada utilizando Raspberry Pi y técnicas de Machine Learning**.
El proyecto busca reproducir un entorno controlado que emule dispositivos IoT reales, analizar el tráfico de red y detectar comportamientos maliciosos mediante un pipeline de detección basado en Suricata, ELK Stack y modelos de aprendizaje automático.

## 🎯 Objetivos

* Simular una red IoT doméstica con dispositivos reales y emulados.
* Capturar tráfico de red y eventos de seguridad mediante **Suricata**.
* Integrar los logs en **Elasticsearch + Kibana** para su visualización.
* Entrenar y evaluar modelos de **Machine Learning** para clasificación de tráfico normal y malicioso.
* Documentar la arquitectura, metodología y resultados del análisis.

## 🏗️ Arquitectura del Proyecto

El proyecto está compuesto por los siguientes módulos:

* **Broker MQTT (Mosquitto)** – Gestiona la comunicación entre dispositivos IoT.
* **Suricata IDS** – Captura y genera eventos de seguridad.
* **ELK Stack (Elasticsearch, Logstash, Kibana)** – Centraliza y visualiza datos.
* **Modelo ML (scikit-learn/TensorFlow)** – Clasifica tráfico y detecta anomalías.
* **Dashboards personalizados** – Paneles en Kibana para análisis en tiempo real.

> Consulta el *diagrama de arquitectura* en la carpeta `docs/` para más detalles.

## 🛠️ Tecnologías Utilizadas

* **Hardware:** Raspberry Pi 4B/5, switch gestionable TP-Link (port mirroring)
* **Software:** Docker, Suricata, ELK Stack, Mosquitto, Python 3.11
* **Librerías ML:** scikit-learn, pandas, numpy, matplotlib
* **Dataset:** TON\_IoT (Train\_Test\_datasets)

## 📂 Estructura del Repositorio

```bash
├── docs/               # Diagramas, capturas y documentación técnica
├── src/                # Código fuente (scripts de análisis y modelos ML)
├── config/             # Archivos de configuración (Suricata, Logstash, Docker)
├── data/               # Datasets (TON_IoT y muestras capturadas)
├── dashboards/         # Exportaciones de visualizaciones de Kibana
└── README.md           # Este archivo
```

## 🚀 Instalación y Ejecución

1. **Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/tfg-ciberseguridad.git
cd tfg-ciberseguridad
```

2. **Levantar el entorno con Docker**

```bash
docker compose up -d
```

3. **Configurar Suricata**

Editar el archivo `config/suricata.yaml` para ajustar las redes monitoreadas.

4. **Entrenar y ejecutar el modelo ML**

```bash
cd src/ml
python train_model.py
python detect.py
```

## 📊 Resultados

El proyecto incluye:

* Dashboards de visualización de tráfico IoT y alertas de Suricata.
* Estadísticas de detección y métricas de rendimiento de los modelos ML.
* Conclusiones sobre la efectividad de la solución en un entorno IoT simulado.

## 📜 Licencia

Este proyecto está bajo la licencia **MIT** – ver el archivo [LICENSE](LICENSE) para más información.

---

¿Quieres que lo prepare **en formato real de Markdown** (`README.md`) con el diagrama de arquitectura que aparece en tu memoria exportado como imagen? Así podría generar el archivo directamente para que lo subas al repositorio.
