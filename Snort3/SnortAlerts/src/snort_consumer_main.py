import argparse
import yaml

from time import sleep
from queue import Queue
from threading import Lock
from stats import DnsStatsConsumer, DisplayStats
from mqtt_client import MqttConsumer

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
    dns_map_lock = Lock()
    dns_map = dict()

    dns_stats = \
        DnsStatsConsumer(lock=lock,
                         input_q=snort_q,
                         dns_map_lock=dns_map_lock,
                         dns_map=dns_map)
    dns_stats.start()
    sleep(1)
    display_stats = \
        DisplayStats(dns_map_lock=dns_map_lock,
                     dns_map=dns_map)
    display_stats.start()
    sleep(1)

    mqtt_client = \
        MqttConsumer(config['mqtt'], lock, snort_q)
    mqtt_client.connect_to_broker()

    dns_stats.join()
    display_stats.join()


if __name__ == "__main__":
    main()
