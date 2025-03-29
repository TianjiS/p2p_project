import socket
import json
import threading
import sqlite3
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class P2PPeer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = {}  # Store active connections
        self.blocked_users = set()  # Store blocked user IDs
        self.muted_users = {}  # Store muted users with their mute end times
        self.setup_database()
        
    def setup_database(self):
        """Initialize SQLite database for local storage"""
        self.conn = sqlite3.connect('p2p_messenger.db')
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                sender_id TEXT,
                receiver_id TEXT,
                content TEXT,
                timestamp DATETIME,
                message_id TEXT UNIQUE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocked_users (
                user_id TEXT PRIMARY KEY
            )
        ''')
        
        self.conn.commit()
    
    def generate_key(self, password):
        """Generate encryption key from password"""
        salt = b'fixed_salt'  # In production, use a random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def start(self):
        """Start the peer server"""
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Listening on {self.host}:{self.port}")
        
        # Start listening thread
        threading.Thread(target=self.accept_connections, daemon=True).start()
    
    def accept_connections(self):
        """Accept incoming connections"""
        while True:
            client, address = self.socket.accept()
            print(f"New connection from {address}")
            threading.Thread(target=self.handle_client, args=(client, address), daemon=True).start()
    
    def handle_client(self, client, address):
        """Handle individual client connections"""
        try:
            while True:
                data = client.recv(4096)
                if not data:
                    break
                    
                message = json.loads(data.decode())
                self.process_message(message, client)
                
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client.close()
    
    def process_message(self, message, client):
        """Process incoming messages"""
        msg_type = message.get('type')
        
        if msg_type == 'message':
            # Store message in database
            self.cursor.execute('''
                INSERT INTO messages (sender_id, receiver_id, content, timestamp, message_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                message['sender'],
                message['receiver'],
                message['content'],
                datetime.now(),
                message['message_id']
            ))
            self.conn.commit()
            
        elif msg_type == 'block':
            self.blocked_users.add(message['user_id'])
            self.cursor.execute('INSERT INTO blocked_users (user_id) VALUES (?)', (message['user_id'],))
            self.conn.commit()
            
        elif msg_type == 'mute':
            mute_duration = message.get('duration', 3600)  # Default 1 hour
            self.muted_users[message['user_id']] = datetime.now().timestamp() + mute_duration
    
    def send_message(self, receiver_address, message):
        """Send message to another peer"""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(receiver_address)
            client.send(json.dumps(message).encode())
        except Exception as e:
            print(f"Error sending message: {e}")
        finally:
            client.close()
    
    def is_user_blocked(self, user_id):
        """Check if a user is blocked"""
        return user_id in self.blocked_users
    
    def is_user_muted(self, user_id):
        """Check if a user is muted"""
        if user_id in self.muted_users:
            if datetime.now().timestamp() > self.muted_users[user_id]:
                del self.muted_users[user_id]
                return False
            return True
        return False

if __name__ == "__main__":
    # Example usage
    peer = P2PPeer()
    peer.start()
