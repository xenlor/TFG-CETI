#!/usr/bin/env python3
import subprocess
import time
import psutil
import json
from datetime import datetime

import paho.mqtt.client as mqtt
from elasticsearch import Elasticsearch, AuthenticationException, TransportError

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ——————————————————————————————
# CONFIG
# ——————————————————————————————
TELEGRAM_TOKEN = "8138414918:AAGGOE8XpikbdooB9Cvgp5HnD14WWMr-a30"
BROKER        = "192.168.1.10"
ES            = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "s71i2Hvh=gnd2*n1MlP3"),
    verify_certs=False,
)
INDICE        = "iot-ml-alerts"

# ——————————————————————————————
# HELPERS INFRA
# ——————————————————————————————
def check_mqtt() -> bool:
    client = mqtt.Client()
    try:
        client.connect(BROKER, 1883, 3)
        client.disconnect()
        return True
    except:
        return False

def service_status(name: str) -> str:
    res = subprocess.run(
        ["systemctl", "is-active", name],
        capture_output=True, text=True
    )
    return res.stdout.strip()

def fetch_last_alerts(sensor: str, n: int = 5):
    q = {
        "size": n,
        "sort": [{"timestamp": {"order": "desc"}}],
        "query": {"term": {"sensor.keyword": sensor}},
    }
    return ES.search(index=INDICE, body=q)

def block_ip(ip: str) -> bool:
    try:
        subprocess.run(
            ["sudo","iptables","-I","INPUT","-s",ip,"-j","DROP"],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def unblock_ip(ip: str) -> bool:
    try:
        subprocess.run(
            ["sudo","iptables","-D","INPUT","-s",ip,"-j","DROP"],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

# ——————————————————————————————
# COMMAND HANDLERS
# ——————————————————————————————
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔧 Diagnóstico", callback_data="diag")],
        [InlineKeyboardButton("📶 MQTT status", callback_data="mqttstatus")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🤖 *Comandos disponibles:*\n"
        "/help – Mostrar esta ayuda\n"
        "/mqttstatus – Estado del broker MQTT\n"
        "/diag – Diagnóstico rápido\n"
        "/lastalerts `<sensor>` `[N]` – Últimas N alertas de un sensor\n"
        "/unblock `<IP>` – Desbloquear manualmente una IP\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def mqttstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ok = check_mqtt()
    text = "🟢 MQTT broker OK" if ok else "🔴 MQTT broker NO responde"
    await update.message.reply_text(text)

async def diag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t0 = time.time()
    _ = check_mqtt()
    lat = (time.time() - t0) * 1000
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    mstat = service_status("mosquitto")
    sstat = service_status("suricata")
    msg = (
        "*Diagnóstico rápido:*\n"
        f"• Latencia MQTT: `{lat:.0f} ms`\n"
        f"• CPU RPi: `{cpu:.1f}%`\n"
        f"• Memoria: `{mem:.1f}%`\n"
        f"• mosquitto: `{mstat}`\n"
        f"• suricata: `{sstat}`"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def lastalerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        return await update.message.reply_text("Uso: /lastalerts <sensor> [N]")
    sensor = args[0]
    n = int(args[1]) if len(args) > 1 else 5

    try:
        resp = fetch_last_alerts(sensor, n)
    except AuthenticationException:
        return await update.message.reply_text(
            "❌ Error de autenticación con Elasticsearch."
        )
    except TransportError as e:
        return await update.message.reply_text(
            f"❌ Error al consultar Elasticsearch: {e.info.get('error','')}"
        )

    hits = resp.get("hits", {}).get("hits", [])
    if not hits:
        return await update.message.reply_text(
            f"No hay alertas para *{sensor}*.", parse_mode=ParseMode.MARKDOWN
        )

    lines = []
    for hit in hits:
        a = hit["_source"]
        ts = a["timestamp"].split("T")[1].split("+")[0]
        lines.append(
            f"`{ts}` • {a['resultado']} (Δt={a['delta_time']:.1f}s) IP={a.get('src_ip','-')}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

async def unblock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        return await update.message.reply_text("Uso: /unblock <IP>")
    ip = args[0]
    if unblock_ip(ip):
        await update.message.reply_text(f"✅ IP {ip} desbloqueada.")
    else:
        await update.message.reply_text(f"❌ No pude desbloquear la IP {ip}.")

# ——————————————————————————————
# CALLBACK-QUERY HANDLER (botones)
# ——————————————————————————————
async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "diag":
        # reutiliza diag
        t0 = time.time()
        _ = check_mqtt()
        lat = (time.time() - t0) * 1000
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        mstat = service_status("mosquitto")
        sstat = service_status("suricata")
        msg = (
            "*Diagnóstico rápido:*\n"
            f"• Latencia MQTT: `{lat:.0f} ms`\n"
            f"• CPU RPi: `{cpu:.1f}%`\n"
            f"• Memoria: `{mem:.1f}%`\n"
            f"• mosquitto: `{mstat}`\n"
            f"• suricata: `{sstat}`"
        )
        await query.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    elif data == "mqttstatus":
        ok = check_mqtt()
        text = "🟢 MQTT broker OK" if ok else "🔴 MQTT broker NO responde"
        await query.message.reply_text(text)

    elif data.startswith("confirm_block:"):
        ip = data.split(":",1)[1]
        ok = block_ip(ip)
        if ok:
            await query.edit_message_text(
                f"🛑 IP *{ip}* bloqueada ✅", parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                f"❌ No pude bloquear la IP *{ip}*", parse_mode=ParseMode.MARKDOWN
            )

    elif data.startswith("cancel_block:"):
        ip = data.split(":",1)[1]
        await query.edit_message_text(
            f"👍 Bloqueo de *{ip}* cancelado", parse_mode=ParseMode.MARKDOWN
        )

# ——————————————————————————————
# ARRANQUE DEL BOT
# ——————————————————————————————
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler(["help","start"], help_command))
    app.add_handler(CommandHandler("mqttstatus", mqttstatus))
    app.add_handler(CommandHandler("diag", diag))
    app.add_handler(CommandHandler("lastalerts", lastalerts))
    app.add_handler(CommandHandler("unblock", unblock_command))
    app.add_handler(CallbackQueryHandler(on_button))

    app.run_polling()
