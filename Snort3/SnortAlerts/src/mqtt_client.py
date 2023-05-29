import sys
import json
import random

import paho.mqtt.client as mqtt


class MqttClient(object):
    """
    Object representation for a MQTT Client
    """

    def __init__(self, config: dict):
        self.host = config['host']
        self.port = config['port']
        self.username = config['username']
        self.password = config['password']
        self.topic = config['topic']
        self.client = self.get_mqtt_client()

    def get_mqtt_client(self, client_id=random.randint(0, 1000)) -> mqtt:
        """
        Initialize MQTT client.

        Args:
            client_id (string or int, optional): MQTT subscribes require a
            unique client id. Defaults to random.randint(0, 1000).

        Returns:
            mqtt: MQTT Client object.
        """
        mqtt_c = mqtt.Client(client_id=str(__name__ + str(client_id)),
                             clean_session=True, userdata=None,
                             protocol=mqtt.MQTTv311, transport="tcp")
        mqtt_c.username_pw_set(self.username, self.password)
        mqtt_c.on_connect = self.on_connect
        return mqtt_c

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


class MqttConsumer(MqttClient):

    def __init__(self, config: dict, lock, output_q):
        super().__init__(config)
        self.client.on_message = self.on_message
        self.lock = lock
        self.output_q = output_q

    def acquire_lock(self):
        if self.lock:
            self.lock.acquire()

    def release_lock(self):
        if self.lock:
            self.lock.release()

    def connect_to_broker(self):
        """
        Connect to MQTT broker
        """
        print("Connecting to broker...")
        self.client.connect(self.host, self.port, 10)
        # method blocks the program, handles reconnects, etc.
        # Since we are listening for published messages to the
        # YoLink broker topic, we need to run indefinitely.
        # If you need to do other things, than call loop_start()
        # instead.
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        """
        Callback for broker published events

        Args:
            client (): MQTT client id.
            userdata (): MQTT client metadata.
            msg (json): JSON payload containing MQTT data.
        """
        payload = json.loads(msg.payload.decode('utf-8'))
        self.acquire_lock()
        self.output_q.put(payload)
        self.release_lock()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for connection to broker.
        """
        print("Connected with result code %s" % rc)

        if (rc == 0):
            print(("Successfully connected to broker {}").format(
                self.host
            ))
        else:
            print("Connection with result code %s" % rc)
            self.restart_mqtt()

        print("Subscribing to topic: %s" % rc)
        self.client.subscribe(self.topic)


class MqttProducer(MqttClient):

    def __init__(self, config: dict):
        super().__init__(config)
        self.connect_to_broker()

    def connect_to_broker(self):
        """
        Connect to MQTT broker
        """
        print("Connecting to broker...")
        self.client.connect(self.host, self.port, 10)
        # Spins a thread that will call the loop method at
        # regular intervals and handle re-connects.
        self.client.loop_start()

    def publish(self, data: str):
        return self._publish(self.topic, data)

    def _publish(self, topic: str, data: str):
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
