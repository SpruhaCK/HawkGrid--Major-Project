import os
import time
import socket
import requests
import boto3
from collections import Counter
from scapy.all import sniff, IP, TCP, conf
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
AZ_RESOURCE_GROUP = "HawkGrid-Azure-RG"
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000/api/detect")

WINDOW_SIZE = 2.0
packet_buffer = []
last_process_time = time.time()
TARGET_IPS = []
CURRENT_CLOUD = "unknown"

# --- 1. DYNAMIC CLOUD DETECTION ---
def detect_cloud():
    """Detects if the VM is running in AWS or Azure."""
    # Check for Azure Metadata
    try:
        resp = requests.get("http://169.254.169.254/metadata/instance?api-version=2021-02-01", 
                            headers={"Metadata": "true"}, timeout=1)
        if resp.status_code == 200: return "azure"
    except: pass

    # Check for AWS Metadata
    try:
        resp = requests.get("http://169.254.169.254/latest/meta-data/", timeout=1)
        if resp.status_code == 200: return "aws"
    except: pass

    return "unknown"

# --- 2. TARGET DISCOVERY (AWS + AZURE) ---
def get_cloud_targets():
    global CURRENT_CLOUD
    CURRENT_CLOUD = detect_cloud()
    print(f"[*] Detected Cloud Environment: {CURRENT_CLOUD.upper()}")

    ips = []
    
    # AWS Logic (Original)
    if CURRENT_CLOUD == "aws":
        try:
            ec2 = boto3.client('ec2', region_name=AWS_REGION)
            response = ec2.describe_instances(Filters=[
                {'Name': 'tag:Name', 'Values': ["HawkGrid-Linux-Victim", "HawkGrid-Windows-Victim"]},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ])
            ips = [i.get('PublicIpAddress') for r in response['Reservations'] for i in r['Instances'] if i.get('PublicIpAddress')]
        except Exception as e:
            print(f"[!] AWS Discovery Error: {e}")

    # Azure Logic (New)
    elif CURRENT_CLOUD == "azure":
        try:
            credential = DefaultAzureCredential()
            compute_client = ComputeManagementClient(credential, AZURE_SUBSCRIPTION_ID)
            # Find the Target VM private IP (Defaulting to your Terraform setup)
            ips = ["10.0.1.5"] 
        except Exception as e:
            print(f"[!] Azure Discovery Error: {e}")

    return list(set(ips))

# --- 3. DYNAMIC INTERFACE FINDER ---
def get_active_interface():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        for iface in conf.ifaces.values():
            if iface.ip == local_ip: return iface
        return conf.iface
    except Exception as e:
        print(f"[!] Auto-detect failed: {e}. Using default.")
        return conf.iface

# --- 4. PROCESSING & SENDING ---
def analyze_window():
    global packet_buffer
    if not packet_buffer: return

    count = len(packet_buffer)
    dst = packet_buffer[0][IP].dst
    src_ips = [p[IP].src for p in packet_buffer]
    src = Counter(src_ips).most_common(1)[0][0]
    
    # Detection logic for SSH (22) and SMB (445)
    auth_fail = sum(1 for p in packet_buffer if p.haslayer(TCP) and p[TCP].dport in [22, 445])
    egress_mb = sum(len(p) for p in packet_buffer) / 1048576

    payload = {
        "node_id": dst,
        "src_ip": src,
        "dst_ip": dst,
        "API_Call_Freq": count / WINDOW_SIZE,
        "Failed_Auth_Count": auth_fail,
        "Network_Egress_MB": egress_mb,
        "cloud_provider": CURRENT_CLOUD 
    }
    
    try:
        requests.post(ORCHESTRATOR_URL, json=payload, timeout=5)
        print(f"[+] Alert Sent to Orchestrator ({CURRENT_CLOUD}): {count} packets for {dst}")
    except: pass

    packet_buffer = []

def packet_callback(pkt):
    global last_process_time, packet_buffer
    if IP in pkt:
        if pkt[IP].dst in TARGET_IPS:
            print(f"[!] TARGET HIT ({CURRENT_CLOUD}): {pkt[IP].src} -> {pkt[IP].dst}")
            packet_buffer.append(pkt)

    if (time.time() - last_process_time) > WINDOW_SIZE:
        analyze_window()
        last_process_time = time.time()

# --- MAIN START ---
if __name__ == "__main__":
    TARGET_IPS = get_cloud_targets()
    print(f"[*] Monitoring Targets: {TARGET_IPS}")
    
    if not TARGET_IPS:
        print("[!] No Targets found! Check your cloud instances.")
    else:
        active_iface = get_active_interface()
        print(f"[*] Sniffer Active on: {active_iface.name}")
        sniff(iface=active_iface, prn=packet_callback, store=0)