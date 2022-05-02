\[WIP\]
### Pihole Elastic Logstash Kibana (ELK) Ingestion

The guide in this document assumes that Pihole is
already configured and running.

I would highly recommend running ELK on a separate server other than
the raspberry pi that runs pihole. ELK is a resource hog.

Use Filebeats to forward the pihole log to the server running ELK.

## Install ELK/Filebeats

Follow the instructions to install Logstash, Elastic Search and Kibana:
https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elastic-stack-on-ubuntu-20-04

The instructions to install Filebeats should be done on the pihole.




