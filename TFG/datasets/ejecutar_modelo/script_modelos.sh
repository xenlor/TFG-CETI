#!/bin/bash

# Script para iniciar o detener todos los modelos
# Uso: ./gestionar_modelos.sh start  --> Para lanzar todos
#       ./gestionar_modelos.sh stop   --> Para detener todos

if [ "$1" == "start" ]; then
    echo "🚀 Lanzando todos los modelos en segundo plano..."

    nohup python -u 4-ejecutar_modelo_movimiento.py > .movimiento.log 2>&1 &
    nohup python -u 4-ejecutar_modelo_puerta.py > .puerta.log 2>&1 &
    nohup python -u 4-ejecutar_modelo_humedad.py > .humedad.log 2>&1 &
    nohup python -u 4-ejecutar_modelo_temperatura.py > .temperatura.log 2>&1 &
    sudo nohup ../../iot-env/bin/python bot-telegram.py > .bot-telegram.log   2>&1 &

    echo "✅ Todos los modelos están ejecutándose."
    echo "Puedes revisar los logs con 'tail -f nombre.log' (por ejemplo, tail -f movimiento.log)"

elif [ "$1" == "stop" ]; then
    echo "🛑 Deteniendo todos los modelos..."

    pkill -f 4-ejecutar_modelo_movimiento.py
    pkill -f 4-ejecutar_modelo_puerta.py
    pkill -f 4-ejecutar_modelo_humedad.py
    pkill -f 4-ejecutar_modelo_temperatura.py
    sudo pkill -f bot-telegram.py

    echo "✅ Todos los modelos han sido detenidos."

else
    echo "❌ Opción no válida. Usa:"
    echo "   ./gestionar_modelos.sh start   → Para lanzar todos los modelos"
    echo "   ./gestionar_modelos.sh stop    → Para detenerlos"
fi
