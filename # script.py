import paho.mqtt.client as mqtt
import json
import random
import time
from web3 import Web3

import sys
print("Python executable:", sys.executable)

# Configurare conexiune blockchain
GANACHE_URL = "http://127.0.0.1:7545"
ACCOUNT = "0xe1172B85eEA46230D64CB5772d57bf7C6c295b9D"  # expeditor
PRIVATE_KEY = "0x344a29b390767f5391920ec6b65514af62456da2d78196d22cc295b299ac2a5a"
TO_ADDRESS = "0xc632925229317da8AC26D133970296Ff380E1950"

# Inițializare conexiune blockchain
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
print("Blockchain connected:", web3.is_connected())

# Configurare MQTT
broker = "mqtt.beia-telemetrie.ro"
topic = "training/device/Popa-Nicoleta"

client = mqtt.Client()
client.connect(broker)

print("Sending sensor data to MQTT broker and Blockchain...")

while True:
    # Generare date randomizate
    heart_rate = random.randint(50, 200)
    systolic = random.randint(80, 200)
    diastolic = random.randint(30, 99)
    spo2 = random.randint(70, 100)

    # Pregătire date pentru MQTT și Blockchain
    data = {
        "heart_rate": heart_rate,
        "systolic": systolic,
        "diastolic": diastolic,
        "spo2": spo2
    }
    payload = json.dumps(data)

    # Trimitere date prin MQTT
    client.publish(topic, payload)
    print("Sent via MQTT:", payload)

    try:
        # Trimitere date pe blockchain
        nonce = web3.eth.get_transaction_count(ACCOUNT)

        tx = {
            'nonce': nonce,
            'to': TO_ADDRESS,
            'value': 0,
            'gas': 2000000,
            'gasPrice': web3.to_wei('50', 'gwei'),
            'data': web3.to_hex(text=json.dumps(data))
        }

        signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print("Sent to Blockchain. Tx hash:", web3.to_hex(tx_hash))

    except Exception as e:
        print(f"Blockchain error: {e}")

    time.sleep(3)
