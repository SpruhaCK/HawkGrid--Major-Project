from scapy.all import sniff, IP, TCP, conf
import requests
import boto3
import time
from collections import Counter
import socket

# --- CONFIGURATION ---
WINDOW_SIZE = 2.0
packet_buffer = []
last_process_time = time.time()
TARGET_IPS = []

# --- 1. DYNAMIC INTERFACE FINDER ---
def get_active_interface():
    """
    Automatically finds the interface currently connected to the internet.
    """
    try:
        # Create a dummy socket to Google DNS to see which interface OS uses
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Ask Scapy to find the interface matching that IP
        for iface in conf.ifaces.values():
            if iface.ip == local_ip:
                return iface
                
        # Fallback: Scapy's default
        return conf.iface
    except Exception as e:
        print(f"[!] Auto-detect failed: {e}. Using default.")
        return conf.iface

# --- 2. AWS DISCOVERY ---
def get_aws_targets():
    print("[*] Fetching AWS IPs...")
    try:
        ec2 = boto3.client('ec2', region_name="us-east-1")
        response = ec2.describe_instances(Filters=[
            {'Name': 'tag:Name', 'Values': ["HawkGrid-Linux-Victim", "HawkGrid-Windows-Victim"]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ])
        ips = [i.get('PublicIpAddress') for r in response['Reservations'] for i in r['Instances'] if i.get('PublicIpAddress')]
        return ips
    except Exception as e:
        print(f"[!] AWS Error: {e}")
        return []

# --- 3. PROCESSING & SENDING ---
def analyze_window():
    global packet_buffer
    if not packet_buffer: return

    # Basic Stats
    count = len(packet_buffer)
    dst = packet_buffer[0][IP].dst
    src_ips = [p[IP].src for p in packet_buffer]
    src = Counter(src_ips).most_common(1)[0][0]
    
    # Speed Optimization (Prevent DoS Crash)
    auth_fail = 0
    egress_mb = (count * 60) / 1048576 # Approximation for high speed
    
    if count < 500: # Only do deep inspection if traffic is light
        auth_fail = sum(1 for p in packet_buffer if p.haslayer(TCP) and p[TCP].dport == 22)
        egress_mb = sum(len(p) for p in packet_buffer) / 1048576

    payload = {
        "node_id": dst,
        "src_ip": src,
        "dst_ip": dst,
        "API_Call_Freq": count / WINDOW_SIZE,
        "Failed_Auth_Count": auth_fail,
        "Network_Egress_MB": egress_mb,
        "cloud_provider": "aws"
    }
    
    try:
        # 5 second timeout to handle Orchestrator load
        requests.post("http://localhost:8000/api/detect", json=payload, timeout=5)
        print(f"[+] Sent {count} packets to API for {dst}")
    except:
        pass # Keep running even if API is slow

    packet_buffer = [] # Clear buffer

def packet_callback(pkt):
    global last_process_time, packet_buffer
    
    if IP in pkt:
        if pkt[IP].dst in TARGET_IPS:
            # VISUAL PROOF
            print(f"[!] TARGET HIT: {pkt[IP].src} -> {pkt[IP].dst}")
            packet_buffer.append(pkt)

    # Time Check
    if (time.time() - last_process_time) > WINDOW_SIZE:
        analyze_window()
        last_process_time = time.time()

# --- MAIN START ---
if __name__ == "__main__":
    # 1. Get Targets
    TARGET_IPS = get_aws_targets()
    print(f"[*] Targets: {TARGET_IPS}")
    
    if not TARGET_IPS:
        print("[!] No Targets found! Is AWS running?")
    else:
        # 2. Auto-Detect Interface
        active_iface = get_active_interface()
        print(f"[*] Auto-detected Interface: {active_iface.name} ({active_iface.ip})")
        
        # 3. Start Sniffing
        print("[*] Sniffer Active. Waiting for Kali...")
        sniff(iface=active_iface, prn=packet_callback, store=0)