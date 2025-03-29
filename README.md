# P2P Messenger System

A decentralized peer-to-peer messaging system with end-to-end encryption and user management features.

## Features

- P2P communication without central server
- End-to-end encryption
- User blocking and muting
- Local message storage
- REST API and WebSocket support
- Real-time messaging

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your environment:
- For local testing, use your local IP address (e.g., 192.168.1.x)
- For production, you'll need static IPs or a dynamic DNS service

3. Start the application:
```bash
python api.py
```

## API Endpoints

### REST API
- `POST /send` - Send a message
- `POST /block` - Block a user
- `POST /mute` - Mute a user temporarily

### WebSocket
- `ws://localhost:8000/ws` - Real-time messaging endpoint

## Security Features

- End-to-end encryption using Fernet (AES-128-CBC)
- Unique encryption keys per chat
- Local storage of messages and user data
- No central server storing messages

## Development Phases

1. Basic P2P Chat System
   - Socket implementation
   - Basic message structure
   - Local storage

2. API-based Messaging System
   - FastAPI integration
   - Pub-sub model
   - Message queueing

3. Special Messages & User Management
   - User blocking
   - Message muting
   - Status updates

4. Security & Enhancements
   - End-to-end encryption
   - User authentication
   - Message integrity

## Testing

For local testing:
1. Start multiple instances on different ports
2. Use local IP addresses for communication
3. Test message sending/receiving
4. Test user blocking and muting

## Production Considerations

1. Use static IPs or dynamic DNS
2. Implement proper peer discovery
3. Add proper error handling
4. Implement message retry mechanism
5. Add proper logging
6. Implement proper key management 