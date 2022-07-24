#!/bin/bash
# --network should match the network for HA container for the bridge connection.
# sudo mkdir -v .node-red
# sudo chown -R 1000:1000 .node-red/
sudo docker run -it -p 1880:1880 --network host -v /home/antonio/.node-red/:/data --name mynodered nodered/node-red
