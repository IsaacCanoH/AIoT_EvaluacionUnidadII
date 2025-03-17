import time
import network
from machine import ADC, Pin
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# 🌐 Configuración MQTT
MQTT_CLIENT_ID = "esp32_mq9_sensor"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "gds0653/mq-9"

# 🚀 Configuración del sensor MQ-9
sensor_pin = ADC(Pin(34))  # Asegúrate de que el pin sea el correcto para tu configuración
sensor_pin.width(ADC.WIDTH_10BIT)  # Definimos la resolución de 10 bits
sensor_pin.atten(ADC.ATTN_11DB)  # Configuración de atenuación para que el sensor lea más voltaje

# 🚨 Umbral de detección (ajustado para CO y CH4)
UMBRAL_CO = 600  # Umbral para detectar CO (puede ajustarse)
UMBRAL_CH4 = 500  # Umbral para detectar CH4 (puede ajustarse)

estado_anterior = None

# 🔌 Función para conectar a WiFi
def conectar_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(20):  # Intentar conexión durante 10 segundos
        if sta_if.isconnected():
            return True
        time.sleep(0.5)
    return False

# 🔄 Función para conectar a MQTT
def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        return None

# 🏁 Bucle principal
if conectar_wifi():
    client = conectar_mqtt()
else:
    client = None

while True:
    try:
        if not network.WLAN(network.STA_IF).isconnected():  # Si se desconectó WiFi
            if conectar_wifi():
                client = conectar_mqtt()

        sensor_value = sensor_pin.read()  # Leer el valor del sensor

        # 🌟 Lógica para detección de gases
        if sensor_value > UMBRAL_CO:  # Si el valor es mayor que el umbral para CO
            estado_actual = "ALTO CO (PELIGRO)"
        elif sensor_value > UMBRAL_CH4:  # Si el valor es mayor que el umbral para CH4
            estado_actual = "ALTO CH4 (PELIGRO)"
        else:
            estado_actual = "GASES NORMALES"

        # Publicar solo si el estado cambió
        if estado_actual != estado_anterior:
            if client:  # Si hay conexión MQTT
                client.publish(MQTT_TOPIC, estado_actual.encode())  # Publicar el estado
            print(estado_actual)  # Mostrar estado en consola

            estado_anterior = estado_actual  # Actualizar el estado

        time.sleep(2)  # Esperar 2 segundos antes de la siguiente lectura

    except Exception as e:
        print(f"[ERROR] Error en el bucle principal: {e}")
        client = None
        time.sleep(5)
