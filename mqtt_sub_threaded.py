import paho.mqtt.client as mqtt
import datetime
import time
import webbrowser
import json
import threading
from asos_scraper import search_product  

BROKER_ADDRESS = "172.20.10.2"
PORT = 1883
TOPIC = "expo/test"
RECONNECT_INTERVAL = 5

def process_message(client, msg):
    payload = msg.payload.decode("utf-8")
    topic = msg.topic
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Topic: {topic} | Message: {payload}")

    # if payload.startswith("Open:"):
    #     url = payload[5:]
    #     print(f"Opening URL: {url}")
    #     webbrowser.open(url)
    #     client.publish("expo/result", f"Opened URL: {url}")

    if payload.startswith("Asos:"):
        query = payload[1:]
        print(f"Searching for product: {query}")
        try:
            result = search_product(query)
            if 'url_content' in result:
                webbrowser.open(result['url_content'])
            client.publish("expo/result", json.dumps(result))
        except Exception as e:
            error_msg = f"ASOS search error: {e}"
            print(error_msg)
            client.publish("expo/result", json.dumps({"error": error_msg}))
    else:
        print(f"Unhandled message: {payload}")
        client.publish("expo/result", f"Received: {payload}")

def handle_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Connected to broker at {BROKER_ADDRESS}")
        client.subscribe(TOPIC)
        client.publish("expo/status", "Backend connected")
    else:
        print(f"Failed to connect. Code: {rc}")

def handle_disconnect(client, userdata, rc, properties=None):
    if rc != 0:
        print("Disconnected. Attempting to reconnect...")
        time.sleep(RECONNECT_INTERVAL)
        try:
            client.reconnect()
        except Exception as err:
            print(f"Reconnection failed: {err}")

def handle_message(client, userdata, msg):
    threading.Thread(target=process_message, args=(client, msg), daemon=True).start()

def create_mqtt_client():
    try:
        client = mqtt.Client(client_id="ProductClient", callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
    except (AttributeError, ValueError):
        client = mqtt.Client("ProductClient")
    
    client.on_connect = handle_connect
    client.on_message = handle_message
    client.on_disconnect = handle_disconnect
    client.will_set("expo/status", "Backend disconnected", qos=1, retain=False)
    return client

def main():
    client = create_mqtt_client()
    try:
        print(f"Connecting to broker {BROKER_ADDRESS}:{PORT}")
        client.connect(BROKER_ADDRESS, PORT, 60)
        client.loop_forever()
    except Exception as err:
        print("Connection failed:", err)

if __name__ == "__main__":
    main()
