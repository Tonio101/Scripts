import sys

import paho.mqtt.client as mqtt


class MqttClient(object):
    """
    Object representation for a MQTT Client
    """

    def __init__(self, config: dict):
        self.host = config['host']
        self.port = config['port']

        self.client = mqtt.Client(client_id=__name__, clean_session=True,
                                  userdata=None, protocol=mqtt.MQTTv311,
                                  transport="tcp")
        self.client.username_pw_set(config['username'], config['password'])
        self.client.on_connect = self.on_connect

    def connect_to_broker(self):
        """
        Connect to MQTT broker
        """
        print("Connecting to broker...")
        self.client.connect(self.host, self.port, 10)
        # Spins a thread that will call the loop method at
        # regular intervals and handle re-connects.
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for broker connection event
        """
        print("Connected with result code %s" % rc)

        if (rc == 0):
            print("Successfully connected to broker %s" % self.host)
        else:
            print("Connection with result code %s" % rc)
            sys.exit(2)

    def publish(self, topic: str, data):
        """
        Publish events to topic
        """
        rc = self.client.publish(topic, data)
        if rc[0] == 0:
            print("Successfully published event to topic {0}".format(
                topic
            ))
        else:
            print("Failed to publish {0} to topic {1}".format(
                data, topic
            ))

        return rc[0]
