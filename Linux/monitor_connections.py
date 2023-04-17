import datetime
import pyshark
# import os

from ip2geotools.databases.noncommercial import DbIpCity

WHITE_LIST_IPS = {
    '164.92.117.235'
}


# Set up a capture filter to monitor traffic on the specified port
def main():
    capture_filter = ("dst host 164.92.117.235 and tcp[tcpflags] == tcp-syn")

    # Start the capture
    print(capture_filter)
    capture = \
        pyshark.LiveCapture(interface="eth0",
                            capture_filter=capture_filter)

    # Check for incoming connections and notify the user
    for packet in capture.sniff_continuously():
        if 'TCP' in packet:
            tcp_flags = packet['TCP'].flags
            # print(tcp_flags)
            if tcp_flags == '0x0002':
                if 'IP' not in packet:
                    continue

                src_ip = packet['IP'].src
                if not (src_ip in WHITE_LIST_IPS):
                    now = datetime.datetime.now()
                    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{timestamp_str}] Connection established from {src_ip}")
                    # Get geolocation information for IP address
                    response = DbIpCity.get(src_ip, api_key='free')
                    print(("{},{}: {}, {} [{}]").format(
                        response.latitude,
                        response.longitude,
                        response.city,
                        response.country,
                        response.region
                    ))


if __name__ == "__main__":
    main()
