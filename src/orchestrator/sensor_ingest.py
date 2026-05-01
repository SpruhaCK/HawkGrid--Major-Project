# import os
# import time
# import socket
# import requests
# import boto3
# from collections import Counter
# from scapy.all import sniff, IP, TCP, conf
# from azure.identity import DefaultAzureCredential
# from azure.mgmt.compute import ComputeManagementClient
# from dotenv import load_dotenv

# load_dotenv()

# # --- CONFIGURATION ---
# AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
# AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
# ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000/api/detect")
# WINDOW_SIZE = 2.0

# packet_buffer = []
# last_process_time = time.time()
# TARGET_IPS = []
# CURRENT_CLOUD = "unknown"

# def detect_cloud():
#     try:
#         if requests.get("http://169.254.169.254/metadata/instance?api-version=2021-02-01", headers={"Metadata": "true"}, timeout=1).status_code == 200:
#             return "azure"
#     except: pass
#     try:
#         if requests.get("http://169.254.169.254/latest/meta-data/", timeout=1).status_code == 200:
#             return "aws"
#     except: pass
#     return "unknown"

# def get_cloud_targets():
#     global CURRENT_CLOUD
#     CURRENT_CLOUD = detect_cloud()
#     print(f"[*] Detected Cloud Environment: {CURRENT_CLOUD.upper()}")
#     ips = []
    
#     if CURRENT_CLOUD == "aws":
#         try:
#             ec2 = boto3.client('ec2', region_name=AWS_REGION)
#             response = ec2.describe_instances(Filters=[
#                 {'Name': 'tag:Name', 'Values': ["HawkGrid-Linux-Victim", "HawkGrid-Windows-Victim"]},
#                 {'Name': 'instance-state-name', 'Values': ['running']}
#             ])
#             ips = [i.get('PrivateIpAddress') for r in response['Reservations'] for i in r['Instances'] if i.get('PrivateIpAddress')]
#         except Exception as e:
#             print(f"[!] AWS Discovery Error: {e}")

#     elif CURRENT_CLOUD == "azure":
#         try:
#             # Assumes target VM is 10.0.1.5 based on Terraform subnet rules
#             ips = ["10.0.1.5"] 
#         except Exception as e:
#             print(f"[!] Azure Discovery Error: {e}")

#     return list(set(ips))

# def get_active_interface():
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", 80))
#         local_ip = s.getsockname()[0]
#         s.close()
#         for iface in conf.ifaces.values():
#             if iface.ip == local_ip: return iface
#         return conf.iface
#     except:
#         return conf.iface

# def analyze_window():
#     global packet_buffer
#     if not packet_buffer: return

#     count = len(packet_buffer)
#     dst = packet_buffer[0][IP].dst
#     src_ips = [p[IP].src for p in packet_buffer]
#     src = Counter(src_ips).most_common(1)[0][0]

#     auth_fail = sum(1 for p in packet_buffer if p.haslayer(TCP) and p[TCP].dport in [22, 3389, 445] and p[TCP].flags == "S")
#     egress_mb = sum(len(p) for p in packet_buffer) / 1048576

#     payload = {
#         "node_id": dst,
#         "src_ip": src,
#         "dst_ip": dst,
#         "API_Call_Freq": float(count / WINDOW_SIZE),
#         "Failed_Auth_Count": float(auth_fail),
#         "Network_Egress_MB": float(egress_mb),
#         "cloud_provider": CURRENT_CLOUD
#     }

#     try:
#         requests.post(ORCHESTRATOR_URL, json=payload, timeout=5)
#         print(f"[+] Alert Sent to Orchestrator ({CURRENT_CLOUD}): {count} packets from {src} to {dst}")
#     except Exception as e: 
#         print(f"[!] API Error: {e}")

#     packet_buffer = []

# def packet_callback(pkt):
#     global last_process_time, packet_buffer
#     if IP in pkt and pkt[IP].dst in TARGET_IPS:
#         packet_buffer.append(pkt)
    
#     if (time.time() - last_process_time) > WINDOW_SIZE:
#         analyze_window()
#         last_process_time = time.time()

# if __name__ == "__main__":
#     TARGET_IPS = get_cloud_targets()
#     print(f"[*] Monitoring Targets: {TARGET_IPS}")
#     if TARGET_IPS:
#         active_iface = get_active_interface()
#         print(f"[*] Sniffer Active on: {active_iface.name} ({active_iface.ip})")
#         sniff(iface=active_iface, prn=packet_callback, store=0)
#     else:
#         print("[!] No Targets found! Check your cloud instances.")
import os
import time
import socket
import requests
from collections import Counter
from scapy.all import sniff, IP, TCP, conf
from dotenv import load_dotenv

# Load unified environment variables
load_dotenv()
from src.cloud.provider_factory import get_cloud_providers

# --- CONFIGURATION ---
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000/api/detect")
WINDOW_SIZE = 2.0

packet_buffer = []
last_process_time = time.time()
TARGET_IP_MAP = {}  # Maps Public IP -> Cloud Provider Name

def get_cloud_targets():
    """Dynamically fetches Public IPs of running cloud instances."""
    print("[*] Contacting Cloud Providers to discover live targets...")
    providers = get_cloud_providers()
    
    for name, provider in providers.items():
        try:
            assets = provider.discover_assets()
            for asset in assets:
                pub_ip = asset.get("public_ip")
                if pub_ip:
                    TARGET_IP_MAP[pub_ip] = name
                    print(f"    -> Monitoring {name.upper()} Target: {pub_ip}")
        except Exception as e:
            print(f"    -> [!] Error loading {name} assets: {e}")
            
    return list(TARGET_IP_MAP.keys())

def get_active_interface():
    """Finds the active network interface sending traffic to the internet."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        for iface in conf.ifaces.values():
            if iface.ip == local_ip: return iface
        return conf.iface
    except:
        return conf.iface

def analyze_window():
    global packet_buffer
    if not packet_buffer: return

    count = len(packet_buffer)
    dst = packet_buffer[0][IP].dst
    src_ips = [p[IP].src for p in packet_buffer]
    src = Counter(src_ips).most_common(1)[0][0]
    
    cloud_provider_name = TARGET_IP_MAP.get(dst, "unknown")

    # Detect failed auth attempts (SYN packets to SSH/RDP/SMB)
    auth_fail = sum(1 for p in packet_buffer if p.haslayer(TCP) and p[TCP].dport in [22, 3389, 445] and p[TCP].flags == "S")
    egress_mb = sum(len(p) for p in packet_buffer) / 1048576

    payload = {
        "node_id": dst,
        "src_ip": src,
        "dst_ip": dst,
        "API_Call_Freq": float(count / WINDOW_SIZE),
        "Failed_Auth_Count": float(auth_fail),
        "Network_Egress_MB": float(egress_mb),
        "cloud_provider": cloud_provider_name
    }

    try:
        requests.post(ORCHESTRATOR_URL, json=payload, timeout=5)
        print(f"[+] Alert Sent to API ({cloud_provider_name.upper()}): {count} packets from {src} to {dst}")
    except Exception as e: 
        print(f"[!] API Connection Error: Is the API running? ({e})")

    packet_buffer = []

def packet_callback(pkt):
    global last_process_time, packet_buffer
    
    # Only buffer packets that are targeting our known Cloud Public IPs
    if IP in pkt and pkt[IP].dst in TARGET_IP_MAP:
        packet_buffer.append(pkt)
    
    if (time.time() - last_process_time) > WINDOW_SIZE:
        analyze_window()
        last_process_time = time.time()

if __name__ == "__main__":
    targets = get_cloud_targets()
    if targets:
        active_iface = get_active_interface()
        print(f"\n[*] Scapy Sniffer Active on: {active_iface.name} ({active_iface.ip})")
        print("[*] Launch your Kali Linux attacks now. Press Ctrl+C to stop.\n")
        
        # 🚨 promisc=True added to catch Bridged VM traffic
        sniff(iface=active_iface, prn=packet_callback, store=0, promisc=True)
    else:
        print("\n[!] No Targets found! Check your cloud instances and .env credentials.")