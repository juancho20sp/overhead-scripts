# Script for JITP
# from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from dotenv import load_dotenv
import boto3
import os

# Load env vars
load_dotenv()

# Replace with your endpoint and region
endpoint         = os.environ.get('AWS_IOT_ENDPOINT')
region           = os.environ.get('AWS_REGION')
policy           = os.environ.get('AWS_POLICY')
thing_type_name  = os.environ.get('AWS_THING_TYPE_NAME')
thing_group_name = os.environ.get('AWS_THING_GROUP_NAME')

# Get the raspberry pi serial number
def get_serial_number():
    try:
        # Read the serial number from /proc/cpuinfo
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    # Get just the serial name
                    serial_number = line.strip().split(": ")[1]
                    return serial_number
    except FileNotFoundError:
        print("Could not find file /proc/cpuinfo.")
    except Exception as e:
        print(f"Error on getting the serial number: {e}")


serial_number = get_serial_number()

if not serial_number:
    raise Exception("Could not find raspberry pi's serial number")

# Define the Thing name
thing_name = f"rb-{serial_number}" 

# Initialize AWS IoT client
client = boto3.client('iot', region_name=region)

# Create a new certificate for the device - JITP 
response = client.create_keys_and_certificate(setAsActive=True)

# Save certificate and key on the device
with open("deviceCert.pem.crt", "w") as cert_file:
    cert_file.write(response["certificatePem"])

with open("privateKey.pem.key", "w") as key_file:
    key_file.write(response["keyPair"]["PrivateKey"])

# Get the Amazon Root CA 1 for completing the set of certificates
root_ca_url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
root_ca_file = "rootCA.pem"
try:
    import requests
    root_ca_data = requests.get(root_ca_url).text
    with open(root_ca_file, "w") as root_file:
        root_file.write(root_ca_data)
except ImportError:
    print("Please install requests package: pip install requests")

# Attach IoT policy to the certificate
client.attach_policy(
    policyName=policy,
    target=response["certificateArn"]
)

# Verify if the thing name exists, if not, creates it
try:
    client.describe_thing_type(thingTypeName=thing_type_name)
    print(f"Thing Type '{thing_type_name}' exists, adding it")
except client.exceptions.ResourceNotFoundException:
    print(f"Thing Type '{thing_type_name}' does not exists. Creating it...")
    client.create_thing_type(thingTypeName=thing_type_name)

# Register the device as a new IoT Thing
try:
    client.describe_thing(thingName=thing_name)

    # Comment this from HERE if we do not want to override our AWS IoT Thing
    attached_principals = client.list_thing_principals(thingName=thing_name)["principals"]
    
    # Desvincula todos los certificados (principals)
    # Remove all certificates (principals) of the thing that we want to override
    for principal in attached_principals:
        print(f"Removing principal {principal} from '{thing_name}'...")
        client.detach_thing_principal(
            thingName=thing_name,
            principal=principal
        )
    print(f"All certificates removed from '{thing_name}'.")
    
    # Remove the thing after removing all certificates from it
    client.delete_thing(thingName=thing_name)
    
    print(f"Thing '{thing_name}' has been deleted successfully.")
    # UNTIL HERE


    client.create_thing(
        thingName=thing_name,
        thingTypeName=thing_type_name  
    )
except client.exceptions.ResourceNotFoundException:
    # If the thing does not exists, create it
    print(f"Creating thing named '{thing_name}'...")
    client.create_thing(
        thingName=thing_name,
        thingTypeName=thing_type_name
    )
    
# Attach certificate to thing
client.attach_thing_principal(
    thingName=thing_name,
    principal=response["certificateArn"]
)

# Make sure that the certificate is activate
client.update_certificate(
    certificateId=response["certificateId"],
    newStatus="ACTIVE"
)

# Add thing to group
try:
    # Check if group exists
    client.describe_thing_group(thingGroupName=thing_group_name)
    print(f"Thing Group '{thing_group_name}' exists.")

except client.exceptions.ResourceNotFoundException:
    # If group does not exists, create it
    print(f"Thing Group named '{thing_group_name}' does not exists. Creating it...")
    client.create_thing_group(
        thingGroupName=thing_group_name,
        thingGroupProperties={
            "thingGroupDescription": "Raspberry Pi Group"
        }
    )

# Add the Thing to the Thing Group
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