import json

from time import sleep
from threading import Thread
import plotly.graph_objects as go


class DnsStats(Thread):

    def __init__(self, lock, input_q):
        super().__init__(daemon=True)
        self.lock = lock
        self.input_q = input_q
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
            if not self.mqtt_client:
                print("{} -> {}".format(
                    src_ip, dns_name
                ))
                continue
            self.mqtt_client.publish(json.dumps(alert))

    def run(self):
        try:
            while True:
                self.process()
                sleep(2)
        except Exception as ex:
            print(ex)


class DnsStatsConsumer(Thread):

    def __init__(self, lock, input_q,
                 dns_map_lock, dns_map):
        super().__init__(daemon=True)
        self.lock = lock
        self.input_q = input_q
        self.dns_map_lock = dns_map_lock
        self.dns_map = dns_map

    def acquire_lock(self, type='mqtt'):
        if type == 'mqtt':
            if self.lock:
                self.lock.acquire()
        elif type == 'dns_map':
            if self.dns_map_lock:
                self.dns_map_lock.acquire()

    def release_lock(self, type='mqtt'):
        if type == 'mqtt':
            if self.lock:
                self.lock.release()
        elif type == 'dns_map':
            if self.dns_map_lock:
                self.dns_map_lock.release()

    def process(self):

        while not self.input_q.empty():
            self.acquire_lock()
            alert = self.input_q.get()
            self.release_lock()

            src_ip = alert['src_addr']
            dns_name = alert['dns_name']
            self.acquire_lock(type='dns_map')
            if src_ip not in self.dns_map:
                self.dns_map[src_ip] = set()

            self.dns_map[src_ip].add(dns_name)
            self.release_lock(type='dns_map')
            # print("{} -> {}".format(
            #     src_ip, self.dns_map[src_ip]
            # ))

    def run(self):
        try:
            while True:
                self.process()
                sleep(2)
        except Exception as ex:
            print(ex)


class DisplayStats(Thread):

    def __init__(self, dns_map_lock, dns_map):
        super().__init__(daemon=True)
        self.dns_map_lock = dns_map_lock
        self.dns_map = dns_map

    def acquire_lock(self):
        if self.dns_map_lock:
            self.dns_map_lock.acquire()

    def release_lock(self):
        if self.dns_map_lock:
            self.dns_map_lock.release()

    def process(self):
        print("Process DNS Map, size: {}".format(
            len(self.dns_map)
        ))
        self.acquire_lock()
        source_ips = list(self.dns_map.keys())
        remote_urls = list(
            set(
                url
                for urls in self.dns_map.values()
                for url in urls
            )
        )

        # Create source and target lists for Sankey diagram
        sources = []
        targets = []

        # Generate source-target pairs for each source IP and remote URL
        for ip, urls in self.dns_map.items():
            for url in urls:
                sources.append(source_ips.index(ip))
                targets.append(len(source_ips) + remote_urls.index(url))
        self.release_lock()

        node_labels = source_ips + remote_urls

        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='black', width=0.5),
                label=node_labels,
            ),
            link=dict(
                source=sources,
                target=targets,
                value=[1] * len(sources),  # Assuming equal value for each link
            ),
        )])

        # Customize layout and display the chart
        fig.update_layout(title_text="Source IP to Remote URLs",
                          font=dict(size=10))
        fig.write_html("sankey_chart.html")

    def run(self):
        try:
            while True:
                self.process()
                sleep(60)
        except Exception as ex:
            print(ex)
