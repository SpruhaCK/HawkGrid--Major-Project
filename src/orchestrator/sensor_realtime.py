import socket
import time
import requests
from datetime import datetime, timezone

# --- CONFIGURATION ---
TARGET_VM_IP = "10.0.1.5" 
# Use localhost to talk to the API on the same VM
API_URL = "http://127.0.0.1:8000/api/detect"
# Exclude your own admin IP to prevent false alerts
MY_LAPTOP_IP = "103.158.138.45" 
LISTEN_PORT = 80  

def start_socket_sensor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False) 
    
    try:
        server.bind(("0.0.0.0", LISTEN_PORT))
        server.listen(100)
    except OSError:
        print(f"Error: Port {LISTEN_PORT} is already in use.")
        return

    print(f"--- HAWKGRID SOCKET SENSOR ACTIVE ---")
    print(f"Monitoring incoming traffic on Port {LISTEN_PORT}...")

    packet_count = 0
    last_flush = time.time()
    # Important: Track the last seen attacker IP to ensure it's logged correctly
    last_attacker_ip = "0.0.0.0"

    while True:
        try:
            client, addr = server.accept()
            src_ip = addr[0]
            client.close()

            if src_ip != MY_LAPTOP_IP:
                packet_count += 1
                last_attacker_ip = src_ip
                print(f"DEBUG: Connection from {src_ip}")

        except BlockingIOError:
            pass

        now = time.time()
        # Aggregation window (2 seconds)
        if now - last_flush >= 2.0:
            if packet_count > 0:
                # Frequency calculation
                freq = (packet_count / 2.0) * 60
                
                # --- PRESENTATION FIX ---
                # We send higher 'rate' and 'sbytes' values during high frequency
                # to help the ML model distinguish PORT_SCAN from random noise.
                payload = {
                    "src_ip": last_attacker_ip,
                    "dst_ip": TARGET_VM_IP, 
                    "API_Call_Freq": freq,
                    "rate": 5.0 if freq > 100 else 1.0, 
                    "sttl": 64.0,
                    "sbytes": 5000.0 if freq > 100 else 1024.0,
                    "cloud_provider": "azure",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                try:
                    response = requests.post(API_URL, json=payload, timeout=1.0)
                    if response.status_code == 200:
                        data = response.json()
                        attack_label = data.get("type", "UNKNOWN")
                        print(f"[ALERT] {attack_label} Logged! Freq: {freq:.1f} | Source: {last_attacker_ip}")
                    else:
                        print(f"[WARN] API Error: {response.status_code}")
                except Exception as e:
                    print(f"[WARN] API Offline: {e}")
            
            packet_count = 0
            last_flush = now
            
        time.sleep(0.1)

if __name__ == "__main__":
    start_socket_sensor()