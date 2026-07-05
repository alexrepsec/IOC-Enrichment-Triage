# IOC-Enrichment-Triage SOAR
 
✅ **Objective**
 
This project demonstrates the deployment of an automated **IOC (Indicator of Compromise) Enrichment and Triage pipeline** built on Shuffle SOAR in a home lab environment. The pipeline receives IP addresses via webhook or automated feed, enriches them with threat intelligence from VirusTotal and AbuseIPDB, evaluates their threat level, and delivers real-time alerts to a Discord channel — with smart filtering to suppress false positives.
 
---
 
## Skills Learned
 
- Deploying and configuring Shuffle SOAR using Docker Compose on Ubuntu 24.04
- Designing multi-node SOAR workflows with parallel API enrichment
- Integrating threat intelligence APIs (VirusTotal v3, AbuseIPDB v2) into automated pipelines
- Implementing conditional branching in SOAR workflows for triage logic
- Building automated IOC ingestion from URLhaus threat feeds using Python
- Sending real-time enriched security alerts to Discord via webhook
- Troubleshooting variable scoping, API authentication, and workflow execution in Shuffle
---
 
## 🧰 Technologies Used
 
| Tool | Purpose |
|---|---|
| Shuffle SOAR | Workflow orchestration platform |
| VirusTotal API v3 | IP reputation — malicious engine detections |
| AbuseIPDB API v2 | IP abuse confidence scoring |
| URLhaus (abuse.ch) | Automated malicious IP feed |
| Discord Webhook | Real-time alert delivery |
| Python 3 | URLhaus feed automation script |
| Docker Compose | Shuffle deployment |
| Ubuntu 24.04 LTS | VM host OS |
| VMware Workstation | Virtualization platform |
 
---
 
## ⚙️ Environment Setup
 
### Virtual Machine Specifications
 
| Parameter | Value |
|---|---|
| OS | Ubuntu 24.04 LTS |
| RAM | 4 GB |
| CPU | 2 cores |
| Network | VMware NAT — Static IP |
| IP Address | 192.168.253.128 |
| Shuffle URL | https://192.168.253.128:3443 |
 
### Prerequisites
 
- VMware Workstation installed
- Ubuntu 24.04 LTS ISO
- Docker and Docker Compose installed
- VirusTotal API key (free tier)
- AbuseIPDB API key (free tier)
- Discord server with a webhook-enabled channel
---
 
## 🏗️ Lab Architecture
 
```
┌─────────────────────────────────────────────────────────────────┐
│                        HOST MACHINE                              │
│                      Windows 11 Pro                              │
│                                                                  │
│   ┌──────────────────┐         ┌──────────────────────────────┐ │
│   │  Manual Testing  │         │   Discord — #soar channel    │ │
│   │  curl / webhook  │         │   Real-time IOC alerts       │ │
│   └────────┬─────────┘         └──────────────────────────────┘ │
│            │                                    ▲                │
│            ▼              VMware NAT             │                │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │               VMware Virtual Machine                      │  │
│   │               Ubuntu 24.04 LTS                            │  │
│   │               IP: 192.168.253.128                         │  │
│   │                                                            │  │
│   │   ┌────────────────────────────────────────────────────┐  │  │
│   │   │              Shuffle SOAR (Docker)                  │  │  │
│   │   │                                                      │  │  │
│   │   │  Webhook → get ip → VirusTotal ──┐                  │  │  │
│   │   │                  → AbuseIPDB  ──► Evaluate ──► Discord│  │  │
│   │   └────────────────────────────────────────────────────┘  │  │
│   │                                                            │  │
│   │   ┌──────────────────────────────────┐                    │  │
│   │   │  urlhaus_feeder.py (Python)       │                    │  │
│   │   │  Fetches URLhaus feed every hour  │                    │  │
│   │   │  Sends IPs to Shuffle webhook     │                    │  │
│   │   └──────────────────────────────────┘                    │  │
│   └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```
 
---
 
## 🔁 Workflow Design
 
### Node Structure
 
| Node | Type | Role |
|---|---|---|
| Webhook 1 | Trigger | Receives `{"ip": "x.x.x.x"}` payload |
| get ip | Shuffle Tools | Extracts IP from webhook payload via `$exec.ip` |
| Virustotal v3 1 | VirusTotal App | Queries IP report — returns malicious engine count |
| Http 1 | HTTP GET | Queries AbuseIPDB — returns abuse confidence score |
| Evaluate Threat | Shuffle Tools | Aggregates VT detections + AbuseIPDB score |
| Discord Aert | HTTP POST | Sends enriched alert to Discord webhook |
 
### Triage Condition
 
Alerts are only sent when:
```
VirusTotal malicious detections > 3
```
 
This filters out benign IPs like 8.8.8.8 and reduces noise.
 
---
 
## 🚀 Step 1 — Shuffle Deployment
 
Shuffle was deployed using Docker Compose on Ubuntu 24.04. Memory settings were tuned to fit within a 4GB VM:
 
```bash
cd ~/Shuffle
# Edit docker-compose.yml — set OpenSearch heap to 512MB
# OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m
 
# Set required kernel parameter
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
 
sudo docker compose up -d
```
 
---
 
## 🔁 Step 2 — Workflow Canvas
 
The complete IOC-Enrichment-Triage workflow in Shuffle SOAR:
 
![Workflow Canvas](screenshots/workflow-canvas.png)
 
---
 
## 🦠 Step 3 — VirusTotal Enrichment
 
VirusTotal v3 API queries the IP and returns the full analysis report including malicious engine detections:
 
![VirusTotal Success](screenshots/virustotal-success.png)
 
---
 
## 🔴 Step 4 — AbuseIPDB Enrichment
 
AbuseIPDB v2 is queried via a generic HTTP node with the API key passed as a header (`Key: YOUR_API_KEY`):
 
![AbuseIPDB Success](screenshots/abuseipdb-success.png)
 
> **Note:** The native AbuseIPDB v2 Shuffle app returns status 422 due to incorrect header handling. Using a generic HTTP node resolves this.
 
---
 
## ⚖️ Step 5 — Threat Evaluation
 
The Evaluate Threat node aggregates both API results into a single output for triage:
 
![Evaluate Threat](screenshots/evaluate-threat.png)
 
For IP `185.220.101.1` (known Tor exit node):
- **VirusTotal:** 14 malicious detections
- **AbuseIPDB Score:** 100/100
---
 
## 🔔 Step 6 — Discord Alerts
 
### Initial Alert
 
First working alert delivered to Discord:
 
![Discord Alert Simple](screenshots/discord-alert-simple.png)
 
### Enriched Alert
 
Full enriched alert with country, ISP, usage type, and VT report link:
 
![Discord Alert Enriched](screenshots/discord-alert-enriched.png)
 
Alert format:
```
🚨 IP MALICIOSA DETECTADA
🌐 IP: 185.220.101.1
🦠 VirusTotal: 14 detecciones maliciosas
📊 AbuseIPDB Score: 100/100
🏳️ País: DE
🏢 ISP: Artikel10 e.V.
📋 Tipo de uso: Commercial
🔗 VT Report: https://www.virustotal.com/gui/ip-address/185.220.101.1
```
 
---
 
## 🚦 Step 7 — Triage Filtering
 
The conditional branch between Evaluate Threat and Discord Alert suppresses alerts for benign IPs:
 
![Condition Setup](screenshots/condition-setup.png)
 
![Discord Filter](screenshots/discord-filter.png)
 
When `8.8.8.8` is submitted — VT: 0, AbuseIPDB: 0 — Discord Alert is **SKIPPED**:
 
```
Status SKIPPED
"Minimum of one branch's conditions must be correct to continue. Total: 0 of 1"
```
 
---
 
## 🌐 Step 8 — Full Pipeline Debug
 
Complete successful execution for `185.220.101.1` showing all nodes green:
 
![Shuffle Debug Full](screenshots/shuffle-debug-full.png)
 
Execution summary:
- **get ip** → Result: `185.220.101.1` ✅
- **Http 1 (AbuseIPDB)** → status 200 ✅
- **Virustotal v3 1** → status 200 ✅
- **Evaluate Threat** → `14 / 100` ✅
- **Discord Aert** → status 204 ✅
---
 
## 🤖 Step 9 — Automated URLhaus Feed
 
A Python script fetches the URLhaus malicious IP feed every hour and sends each IP through the Shuffle pipeline automatically:
 
![URLhaus Terminal](screenshots/urlhaus-terminal.png)
 
```python
# urlhaus_feeder.py — runs on the VM
# Fetches https://urlhaus.abuse.ch/downloads/csv_recent/
# Extracts IPs from malicious URLs
# Posts each IP to Shuffle webhook
# Processes up to 10 IPs per hour to stay within API limits
```
 
Run the feeder:
```bash
python3 ~/urlhaus_feeder.py &
```
 
---
 
## 📁 Project Structure
 
```
IOC-Enrichment-Triage/
├── screenshots/
│   ├── workflow-canvas.png
│   ├── virustotal-success.png
│   ├── abuseipdb-success.png
│   ├── evaluate-threat.png
│   ├── discord-alert-simple.png
│   ├── discord-alert-enriched.png
│   ├── discord-filter.png
│   ├── shuffle-debug-full.png
│   ├── condition-setup.png
│   └── urlhaus-terminal.png
├── urlhaus_feeder.py
└── README.md
```
 
---
 
## 🔑 Key Technical Challenges Solved
 
| Challenge | Solution |
|---|---|
| AbuseIPDB app returns 422 | Replaced with generic HTTP node using `Key:` header |
| Variable `$exec.ip` not propagating to child nodes | Used `get ip` Shuffle Tools node as startnode; child nodes reference `$get_ip` |
| Shuffle Tools node skipped | Ensured startnode is correctly set and all nodes are under its execution tree |
| URLhaus API requires auth | Used public CSV endpoint instead: `/downloads/csv_recent/` |
| Alert noise from benign IPs | Added conditional branch: VirusTotal detections > 3 |
 
---
 
## 👤 Author
 
**alexrepsec**
Cybersecurity enthusiast | Home Lab Builder | SOAR Developer
 
This project was built as part of a cybersecurity portfolio to demonstrate practical SOAR deployment, threat intelligence integration, and automated IOC triage skills.
