# Script without fleet provisioning
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import boto3

# Run AWS configure
# curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
# unzip awscliv2.zip
# sudo ./aws/install

# Need the Access key ID and private and region

# Run this script

# Run the IoT Device client

# Replace with your endpoint and region
endpoint = "a396ubkvp0pdet-ats.iot.us-east-1.amazonaws.com"
region = "us-east-1"
policy= "basicPolicy"
thing_type_name="raspberry"
thing_group_name="raspberries"

# Función para obtener el número de serie de la Raspberry Pi
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
if not serial_number:
    raise Exception("No se pudo obtener el número de serie de la Raspberry Pi.")

thing_name = f"rb-{serial_number}"  # Nombre del Thing usando el serial

# Initialize AWS IoT client
client = boto3.client('iot', region_name=region)

# Create a new certificate for the device - JITP 1 device
response = client.create_keys_and_certificate(setAsActive=True)

# Save certificate and key on the device
with open("deviceCert.pem.crt", "w") as cert_file:
    cert_file.write(response["certificatePem"])

with open("privateKey.pem.key", "w") as key_file:
    key_file.write(response["keyPair"]["PrivateKey"])

# Guarda también el Amazon Root CA 1 para completar el set de certificados
root_ca_url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
root_ca_file = "rootCA.pem"
try:
    import requests
    root_ca_data = requests.get(root_ca_url).text
    with open(root_ca_file, "w") as root_file:
        root_file.write(root_ca_data)
except ImportError:
    print("Por favor instala el paquete requests con: pip install requests")

# Attach IoT policy to the certificate
client.attach_policy(
    policyName=policy, # * / *
    target=response["certificateArn"]
) # Juan's raspberry -> attach juan-raspberry (policy)

# Paso 3: Verifica si el Thing Type existe, si no, crea uno
try:
    client.describe_thing_type(thingTypeName=thing_type_name)
    print(f"El Thing Type '{thing_type_name}' ya existe.")
except client.exceptions.ResourceNotFoundException:
    print(f"El Thing Type '{thing_type_name}' no existe. Creando...")
    client.create_thing_type(thingTypeName=thing_type_name)

# Register the device as a new IoT Thing
# thing_name = "overhead-rasperry-" + response["certificateId"]
# Use serial number for naming
try:
    client.describe_thing(thingName=thing_name)

    # Uncomment this if we want to update our thing
    # Obtén todos los certificados (principals) asociados a este Thing
    attached_principals = client.list_thing_principals(thingName=thing_name)["principals"]
    
    # Desvincula todos los certificados (principals)
    for principal in attached_principals:
        print(f"Desvinculando el principal {principal} de '{thing_name}'...")
        client.detach_thing_principal(
            thingName=thing_name,
            principal=principal
        )
    print(f"Todos los certificados desvinculados de '{thing_name}'.")
    

    print(f"Certificado {response['certificateId']} desactivado.")
    
    # Elimina el Thing después de desvincular los certificados y desactivar el certificado
    client.delete_thing(thingName=thing_name)
    print(f"El Thing '{thing_name}' ha sido eliminado exitosamente.")

    print(f"El Thing '{thing_name}' ya existe.")

    client.create_thing(
        thingName=thing_name,
        thingTypeName=thing_type_name  )
except client.exceptions.ResourceNotFoundException:
    # Si no existe, lo creamos
    print(f"Creando el Thing '{thing_name}'...")
    client.create_thing(
        thingName=thing_name,
        thingTypeName=thing_type_name  # Asociar el Thing con el tipo especificado
)
    
# Attach certificate to thing
client.attach_thing_principal(
    thingName=thing_name,
    principal=response["certificateArn"]
)

    # Desactiva el certificado antes de eliminar el "Thing"
client.update_certificate(
    certificateId=response["certificateId"],
    newStatus="ACTIVE"
)

# Add thing to group
try:
    # Intentar describir el Thing Group para ver si ya existe
    client.describe_thing_group(thingGroupName=thing_group_name)
    print(f"El Thing Group '{thing_group_name}' ya existe.")
except client.exceptions.ResourceNotFoundException:
    # Si no existe, lo creamos
    print(f"El Thing Group '{thing_group_name}' no existe. Creando...")
    client.create_thing_group(
        thingGroupName=thing_group_name,
        thingGroupProperties={
            "thingGroupDescription": "Grupo para Raspberry Pi dispositivos"
        }
    )

# Paso 6: Agrega el Thing al Thing Group
client.add_thing_to_thing_group(
    thingName=thing_name,
    thingGroupName=thing_group_name
)


print("Device successfully provisioned with Thing name:", thing_name)

# ...
# nohup aws-iot-device-client &

# If we have certificates -> just run the device-client
# if the device-client fails due to XXX error -> refresh certificates and create a new thing (override)

# Store the certificates on a specfic folder
# After this script runs succesfully, do something to run the aws-iot-device-client on the background