import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky005"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "gds0653/ky-005"

# Configuración del sensor KY-005 (Sensor Infrarrojo)
ir_sensor = Pin(34, Pin.IN)  # Utiliza el pin 34 para la entrada digital del sensor IR

# Conectar WiFi
def conectar_wifi():
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    timeout = 10
    while not sta_if.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1
    
    if sta_if.isconnected():
        print("\n[INFO] WiFi Conectada!")
        print(f"[INFO] Dirección IP: {sta_if.ifconfig()[0]}")
    else:
        print("\n[ERROR] No se pudo conectar a WiFi")

# Conectar a MQTT
def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        return None

# Leer el sensor infrarrojo
def leer_sensor():
    # El valor del sensor IR es 1 cuando hay señal IR y 0 cuando no hay señal
    signal_detected = ir_sensor.value()
    return signal_detected

# Iniciar conexiones
conectar_wifi()
client = conectar_mqtt()

while True:
    try:
        if not client:
            client = conectar_mqtt()
            if not client:
                time.sleep(5)
                continue
        
        # Leer el estado del sensor infrarrojo
        signal_detected = leer_sensor()
        print(f"[INFO] Señal IR Detectada: {signal_detected}")
        
        # Publicar el estado de la señal en el broker MQTT
        client.publish(MQTT_TOPIC, str(signal_detected))
        time.sleep(2)  # Enviar datos cada 2 segundos
    
    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
        time.sleep(5)
