import requests
import os
from datetime import datetime

def get_public_ip():
    return requests.get("https://api.ipify.org").text.strip()

def update_duckdns(ip, token, domain):
    url = f"https://www.duckdns.org/update?domains={domain}&token={token}&ip={ip}"
    response = requests.get(url)
    return response.text == "OK"

def main():
    token = os.getenv("DUCKDNS_TOKEN")
    domain = os.getenv("DUCKDNS_DOMAIN")

    with open("last_ip.txt", "a+") as f:
        f.seek(0)
        last_ip = f.read().strip()

    current_ip = get_public_ip()

    if current_ip != last_ip:
        print(f"[{datetime.now()}] IP changed: {current_ip}")
        if update_duckdns(current_ip, token, domain):
            print("DuckDNS updated.")
            with open("last_ip.txt", "w") as f:
                f.write(current_ip)
        else:
            print("Failed to update DuckDNS.")
    else:
        print(f"[{datetime.now()}] IP unchanged: {current_ip}")

if __name__ == "__main__":
    main()
