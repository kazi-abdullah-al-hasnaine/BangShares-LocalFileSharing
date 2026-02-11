<p align="center">
  <img src="sample.png" alt="Screenshot" width="900">
</p>
# 🚀 Bang Shares - Local File & Message Sharing

A modern, real-time file and text sharing application that works seamlessly across devices on your local network. Share files, messages, and more without leaving your WiFi network—no accounts, no uploads, no intermediaries.

![GitHub License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![WebSocket](https://img.shields.io/badge/websocket-real--time-brightgreen)

---

## ✨ Features

- **🔄 Real-Time Messaging** – Instant text communication between connected devices
- **📁 File Sharing** – Transfer files of any size with chunked upload support
- **📱 Multi-Device Support** – Works on desktop, mobile, tablet, and any modern browser
- **🌐 Local Network Only** – All data stays within your WiFi; no cloud needed
- **👤 User Profiles** – Customize display names and profile pictures for each connection
- **💾 Chat History** – Session-based message history for reference
- **⚡ Zero Setup** – One-click startup with automatic IP detection
- **🔒 Private & Secure** – No data leaves your local network

---

## 🎯 Quick Start

### Requirements
- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Devices connected to the same WiFi network

### Installation & Setup

#### Windows (Easiest)
```bash
# Simply double-click the provided run.bat file
run.bat
```

The batch script will:
1. Check Python installation
2. Install required dependencies (`websockets`)
3. Auto-detect your local IP address
4. Start both HTTP and WebSocket servers
5. Open the app in your default browser

#### macOS / Linux
```bash
# Install dependencies
pip install websockets

# Start the WebSocket server
python server.py

# In another terminal, start the HTTP server
python -m http.server 8000
```

Then open your browser to `http://localhost:8000` (or your machine's IP for other devices).

---

## 🌐 Connecting Devices

### On Your Computer
Simply open http://localhost:8000 in your browser.

### On Other Devices (Phone, Tablet, etc.)
1. The server will display your IP address on startup
2. Open your browser and navigate to: `http://<YOUR-IP>:8000`
3. Example: `http://192.168.1.100:8000`

**Finding your IP:**
The startup script displays it automatically, or check your router's connected devices list.

---

## 🛠 How It Works

### Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Device 1  │         │   Device 2  │         │   Device 3  │
│  (Browser)  │         │  (Browser)  │         │  (Browser)  │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       └───────────────────────┼───────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  WebSocket Server   │
                    │  (Python/AsyncIO)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   HTTP Server       │
                    │  (Static Files)     │
                    └─────────────────────┘
```

### Key Components

**server.py** – WebSocket server handling:
- Client connection management
- Real-time message broadcasting
- File transfer orchestration
- Chat history persistence

**index.html** – Frontend interface with:
- Modern responsive UI
- WebSocket client implementation
- File upload/download handling
- User authentication and profiles

**run.bat** – Windows automation script:
- Dependency installation
- IP address detection
- Multi-window server startup

---

## 📤 Sharing Files

### Small Files (< 10 MB)
Files are sent as a single WebSocket message with base64 encoding.

### Large Files (> 10 MB)
Files are automatically split into chunks for reliable transfer. Each chunk is processed and reassembled on the receiving end.

**Maximum file size:** Theoretically unlimited (limited by available memory).

---

## 🔧 Configuration

### Server Settings

In `server.py`, you can customize:

```python
# Maximum chat history items to retain
MAX_HISTORY_ITEMS = 1000

# WebSocket server host and port
ws_host = "0.0.0.0"
ws_port = 8765

# HTTP server port
http_port = 8000
```

### WebSocket Buffer Settings

```python
# In websockets.serve() call:
max_size=None          # No message size limit
write_limit=2**20      # 1MB write buffer
```

---

## 🚀 Running the Application

### Option 1: Automated (Windows)
```bash
run.bat
```

### Option 2: Manual (All Platforms)
```bash
# Terminal 1 – WebSocket Server
python server.py

# Terminal 2 – HTTP Server
python -m http.server 8000

# Then open browser
# http://localhost:8000 (local)
# http://<YOUR-IP>:8000 (other devices)
```

### Option 3: Custom Ports
```bash
# Change default ports (edit server.py or run.bat)
python server.py  # Edit ws_port variable
python -m http.server 9000  # Custom HTTP port
```

---

## 📊 API & Message Types

The WebSocket protocol supports the following message types:

### Text Messages
```json
{
  "type": "text",
  "content": "Hello, World!",
  "senderName": "Alice",
  "senderPic": "data:image/png;base64,...",
  "timestamp": "2024-02-12T14:30:45.123456"
}
```

### File Transfer (Small)
```json
{
  "type": "file",
  "filename": "document.pdf",
  "filesize": 2048576,
  "content": "base64-encoded-file-data",
  "senderName": "Bob",
  "timestamp": "2024-02-12T14:31:22.654321"
}
```

### File Transfer (Large – Chunked)
```json
{
  "type": "file_chunk",
  "fileId": "unique-file-id",
  "filename": "movie.mp4",
  "filesize": 1073741824,
  "chunk": "base64-chunk-data",
  "chunkIndex": 0,
  "totalChunks": 512,
  "senderName": "Charlie"
}
```

### System Messages
```json
{
  "type": "online_count",
  "count": 5
}
```

---

## 🔒 Security & Privacy

- **No Cloud Storage** – All data is transmitted directly between devices
- **No User Tracking** – No analytics, no logging, no third parties
- **Local Network Only** – Data doesn't leave your WiFi
- **Session-Based** – No persistent user accounts or authentication
- **Ephemeral Storage** – Chat history is session-specific

**Note:** This application is designed for trusted networks (home, office). For internet-based sharing, consider adding encryption or authentication.

---

## 🐛 Troubleshooting

### "Connection Refused" Error
- Make sure both servers are running (HTTP and WebSocket)
- Check that port 8765 (WebSocket) and 8000 (HTTP) aren't blocked by firewall
- Try `netstat -an` to verify port availability

### Files Not Transferring
- Ensure devices are on the same WiFi network
- Check that WebSocket connection shows "Connected" status in UI
- For large files, increase buffer size in server configuration

### IP Address Not Detected
- The script defaults to `127.0.0.1` if detection fails
- Manually check your IP: Open Command Prompt and run `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Look for "IPv4 Address" in the 192.168.x.x range

### Python Not Found
- Install Python from [python.org](https://www.python.org/)
- Ensure you check "Add Python to PATH" during installation
- Restart your terminal after installation

---

## 📦 Dependencies

- **websockets** – WebSocket protocol support
  ```bash
  pip install websockets
  ```

That's it! No other dependencies needed.

---

## 📝 License

This project is licensed under the MIT License – see the LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs via GitHub Issues
- Suggest features and improvements
- Submit pull requests for enhancements

---

## 🎨 Future Enhancements

- [ ] End-to-end encryption (optional toggle)
- [ ] File sharing with expiration timers
- [ ] Direct peer-to-peer mode (without central server)
- [ ] Mobile app (iOS/Android)
- [ ] Persistent history (optional database)
- [ ] Custom themes and dark mode improvements
- [ ] Screen sharing capabilities
- [ ] Voice & video chat integration

---

## ❓ FAQ

**Q: Can I use this over the internet?**
A: Not safely by default. WiFi Share is designed for local networks. To use over the internet, add authentication and encryption.

**Q: What's the file size limit?**
A: Theoretically unlimited. The chunked transfer system handles large files gracefully. Practical limits depend on available RAM and network speed.

**Q: Is my data saved?**
A: Chat history is kept in memory during the session. Once the server restarts, history is cleared. You can implement persistent storage if needed.

**Q: Can multiple people use it simultaneously?**
A: Yes! The server supports unlimited concurrent connections. Online counter shows active users.

**Q: Why do I need to know my IP address?**
A: To connect other devices, they need to know where to find the server. The IP address is your computer's address on the local network.

---

## 📞 Support

Having issues? Try these resources:
1. Check the **Troubleshooting** section above
2. Verify both servers are running (`python server.py` + `python -m http.server 8000`)
3. Ensure all devices are on the same WiFi network
4. Check your firewall settings (especially corporate/institutional networks)

---

## 🎉 Get Started Now!

```bash
# Windows
run.bat

# macOS/Linux
python server.py &
python -m http.server 8000
```

Then open your browser and start sharing! 🚀

---

**Made with ❤️ for seamless local sharing**
