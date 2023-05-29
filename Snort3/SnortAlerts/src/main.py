import argparse
import yaml

from time import sleep
from queue import Queue
from threading import Lock
from snort3_alerts import Snort3Alerts
from stats import DnsStats
from mqtt_client import MqttProducer

ALERT_FILE_JSON = '/var/log/snort/alert_json.txt'


def parse_config(file) -> dict:
    data = None
    with open(file, 'r') as f:
        data = yaml.safe_load(f)

    return data


def main():
    usage = ("{FILE} --config <config_file>.yaml").format(FILE=__file__)
    description = 'Snort 3 Alerts Proxy'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-c", "--config", help="Configuration file",
                        required=True)
    parser.add_argument("--debug", help="Enable verbose logging",
                        action='store_true', required=False)
    parser.set_defaults(debug=False)

    args = parser.parse_args()

    config = parse_config(args.config)

    snort_q = Queue()
    lock = Lock()

    snort3_alerts = \
        Snort3Alerts(alert_json_file=ALERT_FILE_JSON,
                     lock=lock,
                     output_q=snort_q)

    mqtt_client = \
        MqttProducer(config['mqtt'])
    sleep(1)

    dns_stats = \
        DnsStats(lock=lock,
                 input_q=snort_q)
    dns_stats.register_broker_client(mqtt_client)

    snort3_alerts.start()
    dns_stats.start()
    snort3_alerts.join()
    dns_stats.join()


if __name__ == "__main__":
    main()
