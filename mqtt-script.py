from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

def get_serial_number():
    try:
        # Lee el número de serie de la Raspberry Pi desde /proc/cpuinfo
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    # Extrae el número de serie, eliminando espacios en blanco y la etiqueta 'Serial :'
                    serial_number = line.strip().split(": ")[1]
                    return serial_number
    except FileNotFoundError:
        print("No se pudo encontrar el archivo /proc/cpuinfo. Asegúrate de estar en una Raspberry Pi.")
    except Exception as e:
        print(f"Error al obtener el número de serie: {e}")

# Obtiene el número de serie para usarlo como nombre del Thing
serial_number = get_serial_number()

# Configura el cliente MQTT de AWS IoT
client = AWSIoTMQTTClient(serial_number)
client.configureEndpoint("a396ubkvp0pdet-ats.iot.us-east-1.amazonaws.com", 8883)
client.configureCredentials("rootCA.pem", "privateKey.pem.key", "deviceCert.pem.crt")

# Conéctate al servicio
client.connect()

# Publica un mensaje
client.publish("topic/test", "Hello from Raspberry Pi!", 0)
