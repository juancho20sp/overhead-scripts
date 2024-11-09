from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import boto3

# Replace with your endpoint and region
endpoint = "a396ubkvp0pdet-ats.iot.us-east-1.amazonaws.com"
region = "us-east-1"

# Initialize AWS IoT client
client = boto3.client('iot', region_name=region)

# Create a new certificate for the device
response = client.create_keys_and_certificate(setAsActive=True)

# Save certificate and key on the device
with open("deviceCert.pem.crt", "w") as cert_file:
    cert_file.write(response["certificatePem"])

with open("privateKey.pem.key", "w") as key_file:
    key_file.write(response["keyPair"]["PrivateKey"])

# Attach IoT policy to the certificate
client.attach_policy(
    policyName="juan-raspberry",
    target=response["certificateArn"]
)

# Register the device as a new IoT Thing
# thing_name = "overhead-rasperry-" + response["certificateId"]
thing_name = "overhead-rasperry-1" 
client.create_thing(thingName=thing_name)

print("Device successfully provisioned with Thing name:", thing_name)
