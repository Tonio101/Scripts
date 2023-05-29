import json
import sys
import time
import base64
# import os

from threading import Thread
from scapy.all import DNSQR, DNS


class Snort3Alerts(Thread):

    def __init__(self, alert_json_file: str,
                 lock,
                 output_q,
                 batch_size=50,
                 processing_interval=1):
        """

        Args:
            alert_json_file (str): Snort3 alert json file.
            batch_size (int): Number of lines to read and
                              process in each batch.
            processing_interval (int): Time interval in seconds
                                       between processing batches.
        """
        super().__init__(daemon=True)
        self.lock = lock
        self.output_q = output_q
        self.alert_json_file = alert_json_file
        self.batch_size = batch_size
        self.processing_interval = processing_interval

    def acquire_lock(self):
        if self.lock:
            self.lock.acquire()

    def release_lock(self):
        if self.lock:
            self.lock.release()

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

    def post_process(self, alert):
        if 'dns_name' not in alert:
            return
        if not self.output_q:
            print(alert)
            return

        self.acquire_lock()
        self.output_q.put(alert)
        self.release_lock()

    def process(self):
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
                            self.post_process(alert)
                    except json.decoder.JSONDecodeError:
                        continue

                    sys.stdout.flush()

                time.sleep(self.processing_interval)

    def run(self):
        try:
            self.process()
        except KeyboardInterrupt:
            print('Script interruption')
