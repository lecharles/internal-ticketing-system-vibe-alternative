#!/bin/bash

# Configuration
DOMAIN="internal-jira.example.com"
COUNTRY="US"
STATE="California"
LOCALITY="San Francisco"
ORGANIZATION="Internal Jira"
ORGANIZATIONAL_UNIT="IT"
EMAIL="admin@internal-jira.example.com"
DAYS_VALID=365

# Create SSL directory if it doesn't exist
mkdir -p config/ssl

# Generate private key
openssl genrsa -out config/ssl/internal-jira.key 2048

# Generate CSR
openssl req -new -key config/ssl/internal-jira.key -out config/ssl/internal-jira.csr \
    -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORGANIZATION/OU=$ORGANIZATIONAL_UNIT/CN=$DOMAIN/emailAddress=$EMAIL"

# Generate self-signed certificate
openssl x509 -req -days $DAYS_VALID \
    -in config/ssl/internal-jira.csr \
    -signkey config/ssl/internal-jira.key \
    -out config/ssl/internal-jira.crt

# Set proper permissions
chmod 600 config/ssl/internal-jira.key
chmod 644 config/ssl/internal-jira.crt

echo "SSL certificate generated successfully!"
echo "Certificate: config/ssl/internal-jira.crt"
echo "Private Key: config/ssl/internal-jira.key"
echo ""
echo "Note: This is a self-signed certificate for development/testing."
echo "For production, please use a certificate from a trusted CA." 