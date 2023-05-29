from time import sleep
from threading import Thread


class DnsStats(Thread):

    def __init__(self, lock, input_q):
        super().__init__(daemon=True)
        self.lock = lock
        self.input_q = input_q
        # self.ip_dns_map = dict()
        self.batch_size = 50
        self.mqtt_client = None

    def acquire_lock(self):
        if self.lock:
            self.lock.acquire()

    def release_lock(self):
        if self.lock:
            self.lock.release()

    def register_broker_client(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def process(self):
        if self.input_q and \
           self.input_q.qsize() < 50:
            return

        alerts = []
        self.acquire_lock()
        for _ in range(self.batch_size):
            if not self.input_q.empty():
                alerts.append(self.input_q.get())
        self.release_lock()

        for alert in alerts:
            src_ip = alert['src_addr']
            dns_name = alert['dns_name']
            # if src_ip not in self.ip_dns_map:
            #     self.ip_dns_map[src_ip] = set()

            # self.ip_dns_map[src_ip].add(dns_name)
            if not self.mqtt_client:
                print("{} -> {}".format(
                    src_ip, dns_name
                ))
                continue
            self.mqtt_client.publish(alert)

    def run(self):
        try:
            while True:
                self.process()
                sleep(2)
        except Exception as ex:
            print(ex)


class DnsStatsConsumer(Thread):

    def __init__(self, lock, input_q):
        super().__init__(daemon=True)
        self.lock = lock
        self.input_q = input_q
        self.ip_dns_map = dict()

    def acquire_lock(self):
        if self.lock:
            self.lock.acquire()

    def release_lock(self):
        if self.lock:
            self.lock.release()

    def process(self):

        while not self.input_q.empty():
            self.acquire_lock()
            alert = self.input_q.get()
            self.release_lock()

            src_ip = alert['src_addr']
            dns_name = alert['dns_name']
            if src_ip not in self.ip_dns_map:
                self.ip_dns_map[src_ip] = set()

            self.ip_dns_map[src_ip].add(dns_name)

    def run(self):
        try:
            while True:
                self.process()
                sleep(2)
        except Exception as ex:
            print(ex)
