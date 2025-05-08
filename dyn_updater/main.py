import requests
import os
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge

# Prometheus metrics
ip_update_counter = Counter('duckdns_ip_update_total', 'Total successful IP updates to DuckDNS')
ip_current_gauge = Gauge('duckdns_current_ip', 'Current public IP (converted to numeric for monitoring)')
last_ip_change_time = Gauge('duckdns_last_ip_change_timestamp', 'Last IP change timestamp in Unix time')

# Helper to convert IP to numeric for gauge (simple version)
def ip_to_number(ip):
    try:
        parts = list(map(int, ip.split('.')))
        return sum(part << (8 * (3 - i)) for i, part in enumerate(parts))
    except:
        return 0

def get_public_ip():
    return requests.get("https://api.ipify.org").text.strip()

def update_duckdns(ip, token, domain):
    url = f"https://www.duckdns.org/update?domains={domain}&token={token}&ip={ip}"
    response = requests.get(url)
    return response.text.strip() == "OK"

def main():
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)

    token = os.getenv("DUCKDNS_TOKEN")
    domain = os.getenv("DUCKDNS_DOMAIN")

    # Create log file to persist last IP
    last_ip_path = "last_ip.txt"
    if not os.path.exists(last_ip_path):
        with open(last_ip_path, "w") as f:
            f.write("")

    with open(last_ip_path, "r") as f:
        last_ip = f.read().strip()

    current_ip = get_public_ip()

    if current_ip != last_ip:
        print(f"[{datetime.now()}] IP changed: {current_ip}")
        if update_duckdns(current_ip, token, domain):
            print("✅ DuckDNS updated successfully.")
            with open(last_ip_path, "w") as f:
                f.write(current_ip)

            # Update Prometheus metrics
            ip_update_counter.inc()
            ip_current_gauge.set(ip_to_number(current_ip))
            last_ip_change_time.set_to_current_time()
        else:
            print("❌ Failed to update DuckDNS.")
    else:
        print(f"[{datetime.now()}] IP unchanged: {current_ip}")

if __name__ == "__main__":
    main()
