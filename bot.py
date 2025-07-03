import json
import threading
from datetime import datetime

import paho.mqtt.client as mqtt
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from web3 import Web3

# === CONFIG ===
BOT_TOKEN = "7966683376:AAHtGnj4fPxeKz2F671lrepH1W4d4aKY8yM"
MQTT_BROKER = "mqtt.beia-telemetrie.ro"
MQTT_TOPIC = "training/device/Popa-Nicoleta"

GANACHE_URL = "http://127.0.0.1:7545"
ACCOUNT = "0xe1172B85eEA46230D64CB5772d57bf7C6c295b9D"
PRIVATE_KEY = "0x344a29b390767f5391920ec6b65514af62456da2d78196d22cc295b299ac2a5a"
TO_ADDRESS = "0xc632925229317da8AC26D133970296Ff380E1950"

# === GLOBAL DATA ===
latest_data = {"message": "No data received yet."}

# === Blockchain init ===
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
print("Blockchain connected:", web3.is_connected())

# === MQTT CALLBACKS ===
def on_connect(client, userdata, flags, rc):
    print("✅ Connected to MQTT broker.")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global latest_data
    try:
        payload = json.loads(msg.payload.decode())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Salvează în variabilă globală
        latest_data = {
            "message": (
                f"📡 Ultimele date primite:\n"
                f"❤️ Puls: {payload['heart_rate']} bpm\n"
                f"🩸 Tensiune: {payload['systolic']}/{payload['diastolic']} mmHg\n"
                f"🫁 SpO2: {payload['spo2']}%\n"
                f"⏰ Timp: {timestamp}"
            ),
            "raw": payload
        }
        print("MQTT received:", latest_data["message"])

        # Trimitere pe blockchain
        nonce = web3.eth.get_transaction_count(ACCOUNT)
        tx = {
            'nonce': nonce,
            'to': TO_ADDRESS,
            'value': 0,
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),
            'data': web3.to_hex(text=json.dumps(payload))
        }
        signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print("🔗 Sent to blockchain. Tx hash:", web3.to_hex(tx_hash))

    except Exception as e:
        print("❌ Error in MQTT/Blockchain:", e)

# === MQTT THREAD ===
def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER)
    client.loop_forever()

# === TELEGRAM COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bun venit! Trimite /latest pentru ultimele date.")

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(latest_data["message"])

# === MAIN ===
def main():
    # Start MQTT în fundal
    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Pornește Telegram bot
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))

    print("🤖 Botul Telegram rulează...")
    app.run_polling()

if __name__ == "__main__":
    main()

