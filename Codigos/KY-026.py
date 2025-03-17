import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky026"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "gds0653/ky-026"

# Configuración del sensor KY-026 (sensor de flama)
flame_sensor = ADC(Pin(34))  # Utiliza el pin 34 para la entrada analógica (ajustar si es necesario)
flame_sensor.atten(ADC.ATTN_0DB)  # Rango de entrada de 0 a 1V, si usas otro sensor ajusta el rango.

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

# Leer el sensor de flama (con filtrado)
def leer_sensor():
    valor = flame_sensor.read()  # Leer el valor analógico del sensor
    print(f"[INFO] Valor Sensor de Flama: {valor}")  # Muestra el valor de lectura para monitoreo

    # Definir umbral para detectar flama
    umbral = 500  # Ajustar este valor según la sensibilidad deseada
    if valor > umbral:
        return 1  # Flama detectada
    else:
        return 0  # No se detectó flama

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
        
        # Leer el estado del sensor de flama
        flama_detectada = leer_sensor()
        print(f"[INFO] Flama Detectada: {flama_detectada}")
        
        client.publish(MQTT_TOPIC, str(flama_detectada))
        time.sleep(2)  # Enviar datos cada 2 segundos
    
    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
        time.sleep(5)
