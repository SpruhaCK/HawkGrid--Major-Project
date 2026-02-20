from dotenv import load_dotenv
load_dotenv()
from scapy.all import sniff, IP, TCP, conf
import os
import requests
import time
from collections import Counter
import socket
from src.cloud.provider_factory import get_cloud_providers

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL")
WINDOW_SIZE = 2.0

packet_buffer = []
last_process_time = time.time()

providers = get_cloud_providers()  # returns dict

# Map public_ip -> provider_name
TARGET_MAP = {}

for name, provider in providers.items():
    assets = provider.discover_assets()
    for asset in assets:
        public_ip = asset.get("public_ip")
        if public_ip:
            TARGET_MAP[public_ip] = name


def get_active_interface():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        for iface in conf.ifaces.values():
            if iface.ip == local_ip:
                return iface

        return conf.iface

    except Exception:
        return conf.iface


def analyze_window():
    global packet_buffer

    if not packet_buffer:
        return

    count = len(packet_buffer)
    dst = packet_buffer[0][IP].dst
    src_ips = [p[IP].src for p in packet_buffer]
    src = Counter(src_ips).most_common(1)[0][0]

    auth_fail = sum(
        1 for p in packet_buffer
        if p.haslayer(TCP) and p[TCP].dport in [22, 3389]
    )

    egress_mb = sum(len(p) for p in packet_buffer) / 1048576

    payload = {
        "dst_ip": dst,
        "src_ip": src,
        "API_Call_Freq": count / WINDOW_SIZE,
        "Failed_Auth_Count": auth_fail,
        "Network_Egress_MB": egress_mb,
        "cloud_provider": TARGET_MAP.get(dst, "unknown")
    }

    try:
        resp = requests.post(ORCHESTRATOR_URL, json=payload, timeout=5)
        print(f"[+] Sent window for {dst} - Status: {resp.status_code}") # Added status
    except Exception as e:
        print(f"[!] API error: {e}")

    packet_buffer = []


def packet_callback(pkt):
    global last_process_time, packet_buffer

    if IP in pkt:
        dst_ip = pkt[IP].dst

        if dst_ip in TARGET_MAP:
            packet_buffer.append(pkt)

    if (time.time() - last_process_time) > WINDOW_SIZE:
        analyze_window()
        last_process_time = time.time()


if __name__ == "__main__":

    print(f"[*] Loaded Targets: {list(TARGET_MAP.keys())}")

    if not TARGET_MAP:
        print("[!] No cloud targets discovered.")
    else:
        iface = get_active_interface()
        print(f"[*] Sniffing on {iface.name}")
        sniff(iface=iface, prn=packet_callback, store=0)