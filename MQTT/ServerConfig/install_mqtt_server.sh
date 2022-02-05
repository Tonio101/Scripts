#!/bin/bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo mv myconfig.conf /etc/mosquitto/conf.d/myconfig.conf
sudo service mosquitto restart

read -p "MQTT Server Username" uservar
sudo mosquitto_passwd -c /etc/mosquitto/passwd $uservar

echo "enter this username in acl file."
echo "then run the following commands:"
echo "sudo mv acl /etc/mosquitto/acl"
echo "sudo service mosquitto restart"
