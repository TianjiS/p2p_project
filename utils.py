import json
import socket


def load_config(path="config.json"):
    """Load peer configuration from a JSON file."""
    with open(path, "r") as f:
        config = json.load(f)
    return config


def format_message(sender_ip, sender_port, text):
    """Format a message as a JSON string."""
    return json.dumps({
        "from": f"{sender_ip}:{sender_port}",
        "message": text
    })


def parse_message(raw_data):
    """Parse a raw JSON string into a message dictionary."""
    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:
        return None


def get_own_ip():
    """Return the current machine's local IP address."""
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def print_received_message(msg_dict):
    """Nicely print the received message dictionary."""
    sender = msg_dict.get("from", "unknown")
    message = msg_dict.get("message", "")
    print(f"\n[FROM {sender}] {message}\n> ", end='')  # keeps prompt ready


def safe_close_socket(sock):
    """Close a socket safely."""
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except:
        pass
    finally:
        sock.close()
