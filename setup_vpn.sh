#!/bin/bash

# Update package list and install OpenVPN and unzip
apt-get update
apt-get install -y openvpn unzip

# Navigate to OpenVPN directory
cd /etc/openvpn

# Download the Surfshark configuration files
wget https://my.surfshark.com/vpn/api/v1/server/configurations -O configurations.zip

# Unzip the downloaded configuration files
unzip configurations.zip

# Start OpenVPN using the specific configuration file
openvpn --config de-ber.prod.surfshark.com_tcp.ovpn --auth-user-pass /etc/openvpn/auth.txt
