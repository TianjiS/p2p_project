from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime
import uuid
from peer import P2PPeer

app = FastAPI()
peer = P2PPeer()

class Message(BaseModel):
    sender: str
    receiver: str
    content: str
    message_id: Optional[str] = None
    receiver_port: Optional[int] = None  # Add receiver port

class BlockUser(BaseModel):
    user_id: str

class MuteUser(BaseModel):
    user_id: str
    duration: Optional[int] = 3600  # Default 1 hour

@app.on_event("startup")
async def startup_event():
    peer.start()

@app.post("/send")
async def send_message(message: Message):
    if not message.message_id:
        message.message_id = str(uuid.uuid4())
    
    if peer.is_user_blocked(message.receiver):
        raise HTTPException(status_code=403, detail="User is blocked")
    
    if peer.is_user_muted(message.receiver):
        raise HTTPException(status_code=403, detail="User is muted")
    
    # Use the provided receiver port or default to 5000
    receiver_port = message.receiver_port or 5000
    receiver_address = ("127.0.0.1", receiver_port)
    
    message_dict = {
        "type": "message",
        "sender": message.sender,
        "receiver": message.receiver,
        "content": message.content,
        "message_id": message.message_id,
        "timestamp": datetime.now().isoformat()
    }
    
    peer.send_message(receiver_address, message_dict)
    return {"status": "sent", "message_id": message.message_id}

@app.post("/block")
async def block_user(block: BlockUser):
    message = {
        "type": "block",
        "user_id": block.user_id
    }
    # Broadcast block message to all peers
    # This is a simplified version
    return {"status": "blocked", "user_id": block.user_id}

@app.post("/mute")
async def mute_user(mute: MuteUser):
    message = {
        "type": "mute",
        "user_id": mute.user_id,
        "duration": mute.duration
    }
    # Broadcast mute message to all peers
    # This is a simplified version
    return {"status": "muted", "user_id": mute.user_id}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            # Handle real-time messages
            # This is where you'd implement the WebSocket logic
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 