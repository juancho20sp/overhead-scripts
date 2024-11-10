#!/bin/bash

# Install the AWS CLI for Raspberry IOs
curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install the AWS IoT Device Manager
git clone https://github.com/awslabs/aws-iot-device-client
cd aws-iot-device-client
mkdir build
cd build
cmake ../
cmake --build . --target aws-iot-device-client 

# Run the executable command
# TODO Get this variables from env vars
# Get the serial number
serial_number=$(grep -i 'Serial' /proc/cpuinfo | cut -d ' ' -f 2)

if [ -z "$serial_number" ]; then
    echo "Serial number not found."
    exit 1
else
    echo "Serial number: $serial_number"

    sudo nohup ./aws-iot-device-client --endpoint a396ubkvp0pdet-ats.iot.us-east-1.amazonaws.com --cert ./deviceCert.pem.crt --key ./privateKey.pem.key --thing-name "rb-$serial_number" --root-ca ../rootCA.pem
fi



