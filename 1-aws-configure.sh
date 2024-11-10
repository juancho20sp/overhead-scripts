#!/bin/bash

# TODO: Get these credentials from env vars or secure files
AWS_ACCESS_KEY_ID="AKIAXL7YH6JQSQGSCWO7"
AWS_SECRET_ACCESS_KEY="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"
AWS_REGION="us-east-1"
AWS_OUTPUT_FORMAT="json"

# Create the folder
mkdir -p ~/.aws

# Save the credentials into the specific files
cat <<EOL > ~/.aws/credentials
[default]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY
EOL

# Escribir la configuración en el archivo de configuración de AWS
cat <<EOL > ~/.aws/config
[default]
region = $AWS_REGION
output = $AWS_OUTPUT_FORMAT
EOL
