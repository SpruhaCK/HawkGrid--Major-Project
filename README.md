# 🦅 HawkGrid: Next-Gen Autonomous SOC

[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/)
[![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

**HawkGrid** is an advanced, fully autonomous Security Operations Center (SOC) designed to detect, mitigate, and cryptographically record cyber threats in real-time across multi-cloud environments. 

Moving beyond traditional, reactive SIEMs, HawkGrid utilizes a **Random Forest ML Engine** to analyze network traffic and an automated orchestration layer to execute Layer 4 firewall blocks in seconds, all while logging the forensic evidence to an **Immutable Blockchain Ledger**.

---

## ✨ Unfair Advantages (Unique Features)

* 🧠 **Global Hive Mind:** HawkGrid isn't isolated. If a threat is detected on an AWS node, the orchestrator proactively pushes identical block rules to Azure nodes, instantly securing the entire multi-cloud perimeter.
* 🔗 **Immutable Blockchain Forensics:** Traditional logs can be deleted by intruders. HawkGrid cryptographically chains every detected incident and mitigation action into a tamper-proof blockchain ledger, ensuring absolute audit integrity.
* ⚡ **Fully Autonomous MTTR:** Zero human intervention required. From initial packet ingestion to ML classification and API-driven cloud firewall mitigation, Mean Time To Respond (MTTR) is reduced from hours to mere seconds.
* 🗺️ **Real-Time Attack Topology:** A dynamic, React-based dashboard visualizes live network flows, translating raw logs into flowing animations that snap to "Secure" the millisecond a cloud firewall rule propagates.
* 🛡️ **HawkGrid Shield:** A self-aware defense mechanism that dynamically auto-discovers and whitelists authorized administrator IPs, preventing the automated system from locking out the security team during live testing.

---

## 🛠️ Tech Stack

* **Frontend:** React, TypeScript, Tailwind CSS, Vite
* **Backend:** Python, FastAPI
* **Machine Learning:** Scikit-Learn (Random Forest Engine), Scapy (Packet Analysis)
* **Cloud Targets:** Amazon Web Services (AWS EC2), Microsoft Azure (VMs)
* **DevOps & IaC:** Docker, Docker Compose, Terraform
* **Security:** Custom Cryptographic Blockchain Ledger

---

## 🏗️ Architecture: How It Works

1. **Ingestion:** Live network traffic hits the cloud instances and is forwarded to the Python Backend.
2. **Analysis:** The Random Forest model inspects the payload and assigns a risk anomaly score.
3. **Orchestration:** If the score exceeds critical thresholds, the system flags the IP.
4. **Execution:** The backend autonomously interfaces with AWS/Azure APIs to inject inbound block rules.
5. **Ledger Update:** The entire transaction is hashed and appended to the blockchain.
6. **UI Sync:** The React frontend polls the API, immediately reflecting the block on the live topology map.

---

## 🚀 Installation & Quick Start

Booting a multi-cloud SOC requires a specific sequence: authenticating the cloud, building the infrastructure, starting the containerized services, and launching the ML pipeline.

### Phase 1: Get the Code
1. Click the **Fork** button at the top right of this repository to create your own copy.
2. Clone your forked repository to your local machine:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/HawkGrid.git](https://github.com/YOUR_USERNAME/HawkGrid.git)
   cd HawkGrid