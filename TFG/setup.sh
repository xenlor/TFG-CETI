#!/usr/bin/env bash
set -euo pipefail

# Variables
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/iot-env"
REQ_FILE="$PROJECT_DIR/requirements.txt"
PASSWORD_FILE="$PROJECT_DIR/credenciales_elk.txt"

# Ficheros de configuración en .config
CONFIG_DIR="$PROJECT_DIR/.config"
SURICATA_CONF_SRC="$CONFIG_DIR/suricata.yaml"
LOGSTASH_PIPELINES_LIST_SRC="$CONFIG_DIR/pipelines.yml"
LOGSTASH_PIPELINE_SRC="$CONFIG_DIR/suricata.conf"
KIBANA_CONF_SRC="$CONFIG_DIR/kibana.yml"

# Destinos estándar
SURICATA_CONF_DST="/etc/suricata/suricata.yaml"
LOGSTASH_PIPELINES_LIST_DST="/etc/logstash/pipelines.yml"
LOGSTASH_PIPELINE_CONF_DST="/etc/logstash/conf.d/suricata.conf"
KIBANA_CONF_DST="/etc/kibana/kibana.yml"

echo "1) Actualizando apt y paquetes base..."
sudo apt update
sudo apt install -y python3 python3-venv python-is-python3 wget gpg

echo "2) Creando entorno virtual y pip install..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
if [[ -f "$REQ_FILE" ]]; then
  pip install -r "$REQ_FILE"
fi

echo "3) Añadiendo repositorio Elastic..."
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch \
  | sudo gpg --dearmor -o /usr/share/keyrings/elastic-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/elastic-archive-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" \
  | sudo tee /etc/apt/sources.list.d/elastic-8.x.list

sudo apt update

echo "4) Instalando Suricata y ELK..."
sudo apt install -y suricata elasticsearch logstash kibana

echo "5) Copiando ficheros de configuración desde .config..."
sudo cp "$SURICATA_CONF_SRC"          "$SURICATA_CONF_DST"
sudo cp "$LOGSTASH_PIPELINES_LIST_SRC" "$LOGSTASH_PIPELINES_LIST_DST"
sudo cp "$LOGSTASH_PIPELINE_SRC"       "$LOGSTASH_PIPELINE_CONF_DST"
sudo cp "$KIBANA_CONF_SRC"             "$KIBANA_CONF_DST"

echo "6) Habilitando y arrancando servicios..."
sudo systemctl enable elasticsearch logstash kibana
sudo systemctl start   elasticsearch logstash kibana

echo "7) Generando contraseñas de usuarios internos..."
: > "$PASSWORD_FILE"
for USER in elastic kibana_system; do
  echo "---- $USER ----" >> "$PASSWORD_FILE"
  printf 'y\n' | sudo /usr/share/elasticsearch/bin/elasticsearch-reset-password \
    -u "$USER" --batch -f >> "$PASSWORD_FILE" 2>&1
  echo >> "$PASSWORD_FILE"
done
chmod 600 "$PASSWORD_FILE"
echo "Contraseñas guardadas en $PASSWORD_FILE"

echo
echo "¡Setup completado!"
echo "IMPORTANTE: Debes actualizar las credenciales en los ficheros de configuración:"
echo "  • Usuario 'kibana_system' en /etc/kibana/kibana.yml"
echo "  • Usuario 'elastic' en /etc/logstash/conf.d/suricata.conf"
echo "  Consulta las nuevas credenciales en: $PASSWORD_FILE"
