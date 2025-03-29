import socket
import json
import threading
import time
import requests
from datetime import datetime
import sys

class TestPeer:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.socket = None
        self.running = True
        self.received_messages = []
        self.setup_socket()
        
    def setup_socket(self):
        """Setup socket for receiving messages"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('127.0.0.1', self.port))
            self.socket.listen(5)
            self.accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            self.accept_thread.start()
        except socket.error as e:
            print(f"Error setting up socket for {self.name}: {e}")
            sys.exit(1)
        
    def accept_connections(self):
        """Accept incoming connections"""
        while self.running:
            try:
                if not self.socket:
                    break
                client, addr = self.socket.accept()
                threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()
            except Exception as e:
                if self.running:  # Only print error if we're still running
                    print(f"Error accepting connection in {self.name}: {e}")
                break
            
    def handle_client(self, client, addr):
        """Handle incoming messages"""
        try:
            while self.running:
                data = client.recv(4096)
                if not data:
                    break
                message = json.loads(data.decode())
                self.received_messages.append(message)
                print(f"{self.name} received: {message}")
        except Exception as e:
            if self.running:  # Only print error if we're still running
                print(f"Error handling client in {self.name}: {e}")
        finally:
            client.close()
            
    def send_message(self, receiver_port, content):
        """Send message to another peer"""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('127.0.0.1', receiver_port))
            message = {
                "type": "message",
                "sender": self.name,
                "receiver": f"peer_{receiver_port}",
                "content": content,
                "message_id": str(datetime.now().timestamp()),
                "timestamp": datetime.now().isoformat()
            }
            client.send(json.dumps(message).encode())
        except Exception as e:
            print(f"Error sending message from {self.name}: {e}")
        finally:
            client.close()
            
    def cleanup(self):
        """Cleanup socket resources"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        if hasattr(self, 'accept_thread'):
            self.accept_thread.join(timeout=1.0)

def test_basic_messaging():
    """Test basic messaging between peers"""
    print("\n=== Testing Basic Messaging ===")
    
    # Create three peers with different ports (avoiding port 8000 used by FastAPI)
    peer1 = TestPeer("peer_5000", 5000)
    peer2 = TestPeer("peer_5001", 5001)
    peer3 = TestPeer("peer_5002", 5002)
    
    peers = [peer1, peer2, peer3]
    
    try:
        # Give time for sockets to setup
        time.sleep(2)
        
        # Test sending messages with longer delays
        print("\nSending messages...")
        
        # First message: Peer 1 -> Peer 2
        print("Sending message from Peer 1 to Peer 2...")
        peer1.send_message(5001, "Hello from peer1!")
        time.sleep(1)  # Increased delay
        
        # Second message: Peer 2 -> Peer 1
        print("Sending message from Peer 2 to Peer 1...")
        peer2.send_message(5000, "Hi peer1!")
        time.sleep(1)  # Increased delay
        
        # Third message: Peer 3 -> Peer 2
        print("Sending message from Peer 3 to Peer 2...")
        peer3.send_message(5001, "Hello peer2!")
        time.sleep(1)  # Increased delay
        
        # Wait for messages to be received
        time.sleep(3)
        
        # Print received messages with more detailed output
        print("\nPeer1 received messages:")
        for msg in peer1.received_messages:
            print(f"- From {msg['sender']}: {msg['content']}")
            
        print("\nPeer2 received messages:")
        for msg in peer2.received_messages:
            print(f"- From {msg['sender']}: {msg['content']}")
            
        print("\nPeer3 received messages:")
        for msg in peer3.received_messages:
            print(f"- From {msg['sender']}: {msg['content']}")
            
    finally:
        # Cleanup
        for peer in peers:
            peer.cleanup()

def test_api_endpoints():
    """Test FastAPI endpoints"""
    print("\n=== Testing API Endpoints ===")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test sending message
        print("\nTesting /send endpoint...")
        message_data = {
            "sender": "test_user1",
            "receiver": "test_user2",
            "content": "Test message via API",
            "receiver_port": 5001  # Specify the receiver's port
        }
        response = requests.post(f"{base_url}/send", json=message_data)
        print(f"Send response: {response.json()}")
        
        # Test blocking user
        print("\nTesting /block endpoint...")
        block_data = {
            "user_id": "test_user2"
        }
        response = requests.post(f"{base_url}/block", json=block_data)
        print(f"Block response: {response.json()}")
        
        # Test muting user
        print("\nTesting /mute endpoint...")
        mute_data = {
            "user_id": "test_user2",
            "duration": 3600
        }
        response = requests.post(f"{base_url}/mute", json=mute_data)
        print(f"Mute response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server. Make sure it's running on port 8000.")
        sys.exit(1)
    except Exception as e:
        print(f"Error testing API endpoints: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Start the FastAPI server in a separate thread
    import uvicorn
    import threading
    
    def run_server():
        try:
            uvicorn.run("api:app", host="127.0.0.1", port=8000, log_level="error")
        except Exception as e:
            print(f"Error starting FastAPI server: {e}")
            sys.exit(1)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Run tests
        test_basic_messaging()
        test_api_endpoints()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1) 