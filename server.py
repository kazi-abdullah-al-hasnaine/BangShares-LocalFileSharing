"""
WebSocket Server for Real-Time File and Text Sharing
Handles text messages and file transfers between connected clients
Compatible with all websockets library versions
"""

import asyncio
import websockets
import json
import base64
import socket
import uuid
from datetime import datetime

# Store all connected clients
connected_clients = set()

# Store chat history for the current session
chat_history = []
MAX_HISTORY_ITEMS = 1000  # Limit to prevent memory issues

# Store large file chunks temporarily
file_chunks_storage = {}

# Map client IDs to their websocket connections
client_connections = {}  # {client_id: websocket}

def get_local_ip():
    """
    Automatically detect the local LAN IP address
    Returns the IP address as a string
    """
    try:
        # Create a socket connection to determine the local IP
        # We connect to an external address (doesn't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error detecting IP: {e}")
        return "127.0.0.1"

async def broadcast_message(message, sender=None):
    """
    Send a message to all connected clients except the sender
    Args:
        message: The message to broadcast (string or dict)
        sender: The websocket connection of the sender (optional)
    """
    if connected_clients:
        # Convert message to JSON string if it's a dict
        message_str = json.dumps(message) if isinstance(message, dict) else message
        
        # Create tasks to send to all clients
        tasks = []
        for client in connected_clients:
            # Don't send back to the sender
            if client != sender:
                tasks.append(client.send(message_str))
        
        # Send to all clients concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def broadcast_online_count():
    """
    Broadcast the current number of connected clients to all clients
    """
    if connected_clients:
        message = json.dumps({
            "type": "online_count",
            "count": len(connected_clients)
        })
        
        # Create tasks to send to all clients
        tasks = [client.send(message) for client in connected_clients]
        
        # Send to all clients concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def send_chat_history(websocket, client_id):
    """
    Send chat history to a newly connected client along with their client ID
    """
    try:
        # First, send the client their unique ID
        await websocket.send(json.dumps({
            "type": "client_id",
            "clientId": client_id
        }))
        
        # Then send history message
        if chat_history:
            await websocket.send(json.dumps({
                "type": "history",
                "messages": chat_history
            }))
    except Exception as e:
        print(f"Error sending chat history: {e}")

def add_to_history(message_data):
    """
    Add a message to chat history
    Only stores text messages and file metadata (not the actual file content)
    """
    global chat_history
    
    # Don't store file chunks in history
    if message_data.get("type") == "file_chunk":
        return
    
    # For files, store metadata only
    if message_data.get("type") == "file":
        history_item = {
            "type": "file",
            "filename": message_data.get("filename"),
            "filesize": message_data.get("filesize"),
            "sender": message_data.get("sender"),
            "clientId": message_data.get("clientId"),
            "senderName": message_data.get("senderName"),
            "senderPic": message_data.get("senderPic"),
            "timestamp": message_data.get("timestamp"),
            "note": "File was shared during session"
        }
    else:
        # Store complete message for text with client ID
        history_item = message_data.copy()
        # Ensure clientId is included
        if "clientId" not in history_item:
            history_item["clientId"] = message_data.get("sender")
    
    chat_history.append(history_item)
    
    # Limit history size
    if len(chat_history) > MAX_HISTORY_ITEMS:
        chat_history = chat_history[-MAX_HISTORY_ITEMS:]

async def handle_client(websocket, path=None):
    """
    Handle individual client connections
    Manages text messages and file transfers
    Compatible with all websockets versions (path parameter is optional)
    """
    # Add new client to the set before getting ID
    connected_clients.add(websocket)
    
    # Get client IP safely
    try:
        client_ip = websocket.remote_address[0]
    except:
        client_ip = "unknown"
    
    # Wait for client to send their client ID (or generate new one)
    client_id = None
    try:
        # Receive first message which should contain client_id or connection request
        first_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
        data = json.loads(first_message)
        
        # Check if client is sending their persistent ID
        if data.get("type") == "register":
            client_id = data.get("clientId")
            if not client_id:
                client_id = str(uuid.uuid4())
        else:
            # Generate new ID if they didn't send one
            client_id = str(uuid.uuid4())
            # Process first message normally (re-queue it conceptually)
    except asyncio.TimeoutError:
        # No message received within 5 seconds, generate new ID
        client_id = str(uuid.uuid4())
    except Exception as e:
        # Error receiving first message, generate new ID
        print(f"Error in client handshake: {e}")
        client_id = str(uuid.uuid4())
    
    # Store the client connection
    client_connections[client_id] = websocket
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Client connected: {client_ip} (ID: {client_id})")
    print(f"Total connected clients: {len(connected_clients)}")
    
    # Send chat history and client ID to the new client
    await send_chat_history(websocket, client_id)
    
    # Broadcast updated online count to all clients
    await broadcast_online_count()
    
    try:
        # Listen for messages from this client
        async for message in websocket:
            try:
                # Parse the incoming message
                data = json.loads(message)
                message_type = data.get("type")
                
                # Skip register messages (already handled)
                if message_type == "register":
                    continue
                
                if message_type == "text":
                    # Handle text message
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Text from {client_ip}: {data.get('content', '')[:50]}...")
                    
                    message_data = {
                        "type": "text",
                        "content": data.get("content", ""),
                        "sender": client_ip,
                        "clientId": client_id,
                        "senderName": data.get("senderName", "Anonymous"),
                        "senderPic": data.get("senderPic", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Add to history
                    add_to_history(message_data)
                    
                    # Broadcast text message to all other clients
                    await broadcast_message(message_data, sender=websocket)
                
                elif message_type == "file":
                    # Handle file transfer (small files sent as single message)
                    filename = data.get("filename", "unknown")
                    filesize = data.get("filesize", 0)
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] File from {client_ip}: {filename} ({filesize} bytes)")
                    
                    message_data = {
                        "type": "file",
                        "filename": filename,
                        "filesize": filesize,
                        "content": data.get("content", ""),  # base64 encoded file data
                        "sender": client_ip,
                        "clientId": client_id,
                        "senderName": data.get("senderName", "Anonymous"),
                        "senderPic": data.get("senderPic", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Add to history (without file content)
                    add_to_history(message_data)
                    
                    # Broadcast file to all other clients
                    await broadcast_message(message_data, sender=websocket)
                
                elif message_type == "file_chunk":
                    # Handle large file chunks (for files sent in parts)
                    filename = data.get("filename", "unknown")
                    chunk_index = data.get("chunkIndex", 0)
                    total_chunks = data.get("totalChunks", 1)
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] File chunk {chunk_index + 1}/{total_chunks} from {client_ip}: {filename}")
                    
                    # Broadcast chunk to all other clients
                    await broadcast_message({
                        "type": "file_chunk",
                        "fileId": data.get("fileId", ""),
                        "filename": filename,
                        "filesize": data.get("filesize", 0),
                        "chunk": data.get("chunk", ""),
                        "chunkIndex": chunk_index,
                        "totalChunks": total_chunks,
                        "sender": client_ip,
                        "clientId": client_id,
                        "senderName": data.get("senderName", "Anonymous"),
                        "senderPic": data.get("senderPic", ""),
                        "timestamp": datetime.now().isoformat()
                    }, sender=websocket)
                
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Unknown message type from {client_ip}: {message_type}")
                    
            except json.JSONDecodeError:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Invalid JSON from {client_ip}")
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Error handling message from {client_ip}: {e}")
    
    except websockets.exceptions.ConnectionClosed:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Client disconnected: {client_ip}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Connection error from {client_ip}: {e}")
    
    finally:
        # Remove client from the set when disconnected
        connected_clients.discard(websocket)
        client_connections.pop(client_id, None)
        print(f"Total connected clients: {len(connected_clients)}")
        
        # Broadcast updated online count to all clients
        if connected_clients:  # Only broadcast if there are still connected clients
            asyncio.create_task(broadcast_online_count())

async def main():
    """
    Main function to start the WebSocket server
    """
    # Get local IP address
    local_ip = get_local_ip()
    
    # WebSocket server configuration
    ws_host = "0.0.0.0"  # Listen on all network interfaces
    ws_port = 8765
    
    # HTTP server configuration (for reference)
    http_port = 8000
    
    print("=" * 60)
    print("WebSocket Server for File and Text Sharing")
    print("=" * 60)
    print(f"\n✓ Server started successfully!")
    print(f"\n📱 Mobile/Other devices can connect to:")
    print(f"   HTTP URL:  http://{local_ip}:{http_port}")
    print(f"   WebSocket: ws://{local_ip}:{ws_port}")
    print(f"\n💡 Make sure the HTTP server is running on port {http_port}")
    print(f"   Run: python -m http.server {http_port}")
    print(f"\n🔌 Waiting for connections...")
    print("=" * 60)
    print()
    
    # Start the WebSocket server with compatibility for all versions
    try:
        # Try newer websockets API (version 10+)
        async with websockets.serve(
            handle_client, 
            ws_host, 
            ws_port,
            max_size=None,  # No limit - we're using chunked transfer
            write_limit=2**20  # 1MB write buffer
        ):
            # Keep the server running
            await asyncio.Future()  # Run forever
    except TypeError:
        # Fallback for older websockets versions
        async with websockets.serve(
            handle_client, 
            ws_host, 
            ws_port
        ):
            # Keep the server running
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        # Run the server
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
