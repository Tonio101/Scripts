import json
import sys
import time
import base64
# import os

from scapy.all import DNSQR, DNS

ALERT_FILE_JSON = '/var/log/snort/alert_json.txt'
# TODO: Store in memory for now, move to
#       permanent storage later.
IP_DNS_QUERY_MAP = dict()


class Snort3Alerts(object):

    def __init__(self, alert_json_file: str, batch_size=50,
                 processing_interval=1):
        """

        Args:
            alert_json_file (str): Snort3 alert json file.
            batch_size (int): Number of lines to read and
                              process in each batch.
            processing_interval (int): Time interval in seconds
                                       between processing batches.
        """
        self.alert_json_file = alert_json_file
        self.batch_size = batch_size
        self.processing_interval = processing_interval

    def process_dns_payload(self, payload) -> str:
        dns_payload = DNS(payload)
        dns_name = dns_payload[DNSQR].qname.decode('utf-8')
        return dns_name

    def process_packet(self, type: str, alert):
        b64_data_decoded = \
            base64.b64decode(alert['b64_data'])
        if type == 'DNS':
            alert['dns_name'] = \
                self.process_dns_payload(b64_data_decoded)

    def update_ip_dns_map(self, alert):
        if 'dns_name' not in alert:
            return

        src_ip = alert['src_addr']
        if src_ip not in IP_DNS_QUERY_MAP:
            IP_DNS_QUERY_MAP[src_ip] = set()

        IP_DNS_QUERY_MAP[src_ip].add(alert['dns_name'])

    def process(self):
        try:
            with open(self.alert_json_file, 'r') as file:
                while True:
                    lines = []
                    for _ in range(self.batch_size):
                        line = file.readline()
                        if line:
                            lines.append(line.strip())

                    for line in lines:
                        try:
                            alert = json.loads(line)

                            if 'rule' in alert and \
                               alert['rule'] == '1:1000001:1' and \
                               alert['src_addr'] != '192.168.1.10':
                                self.process_packet('DNS', alert)
                                self.update_ip_dns_map(alert)
                                print("{}->{}".format(
                                    alert['src_addr'],
                                    IP_DNS_QUERY_MAP[alert['src_addr']]
                                ))

                        except json.decoder.JSONDecodeError:
                            continue

                        sys.stdout.flush()

                    time.sleep(self.processing_interval)

        except KeyboardInterrupt:
            print('Script interruption')


def main():
    snort3_alerts = Snort3Alerts(alert_json_file=ALERT_FILE_JSON)
    snort3_alerts.process()


if __name__ == "__main__":
    main()
