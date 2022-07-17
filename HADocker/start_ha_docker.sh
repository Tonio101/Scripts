#!/bin/bash
# Update HA
# https://www.home-assistant.io/installation/raspberrypi
# To update:
# sudo docker stop homeassistant
# sudo docker pull ghcr.io/home-assistant/home-assistant:stable

echo -n "Update or start Home Assistant Docker Image? [start/update] "
read RESPONSE

case $RESPONSE in

    "update")
        echo -n "Updating Home Assistant."
        echo -n "Stop Home Assistant."
        sudo docker stop homeassistant
        sudo docker pull ghcr.io/home-assistant/home-assistant:stable
    ;;
    "start")
        echo -n "Starting Home Assistant."
        sudo docker run -d --name homeassistant --privileged --restart=unless-stopped -e TZ=America/Los_Angeles -v /home/antonio/HADocker:/config --network=host ghcr.io/home-assistant/home-assistant:stable
    ;;
    *)
        echo -n "Invalid input."
        exit 1
    ;;
esac
