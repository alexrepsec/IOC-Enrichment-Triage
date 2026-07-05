### urlhaus_feeder.py
 
```python
import requests
import time
import re
import urllib3
 
urllib3.disable_warnings()
 
WEBHOOK = "https://<YOUR_SHUFFLE_IP>:3443/api/v1/hooks/<YOUR_WEBHOOK_ID>"
 
 
def get_urlhaus_ips():
    """Fetch recent malicious IPs from URLhaus feed."""
    r = requests.get(
        "https://urlhaus.abuse.ch/downloads/csv_recent/",
        verify=False
    )
    ips = set()
    for line in r.text.splitlines():
        if line.startswith("#"):
            continue
        match = re.search(r'https?://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
        if match:
            ips.add(match.group(1))
    return ips
 
 
def send_to_shuffle(ip):
    """Send a single IP to the Shuffle SOAR webhook."""
    try:
        response = requests.post(
            WEBHOOK,
            json={"ip": ip},
            verify=False,
            timeout=10
        )
        print(f"Sent: {ip} — Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending {ip}: {e}")
 
 
def main():
    while True:
        print("Fetching URLhaus feed...")
        ips = get_urlhaus_ips()
        print(f"Found {len(ips)} unique IPs")
 
        for ip in list(ips)[:10]:  # Max 10 IPs per run to stay within API limits
            send_to_shuffle(ip)
            time.sleep(5)  # 5 seconds between requests
 
        print("Sleeping 1 hour...")
        time.sleep(3600)
 
 
if __name__ == "__main__":
    main()
```
