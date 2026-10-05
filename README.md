# Termux Open Ports Scanner 🔍

A professional-grade terminal UI for scanning open ports with animations, network discovery, and advanced features.

## ✨ Features

### Core Features
- 🎨 **Beautiful Dashboard** - Polished terminal UI with real-time updates
- 🔄 **Live Refresh** - Smooth animations and progress tracking
- 📊 **Real-time Statistics** - Speed, elapsed time, port counts
- 🎯 **Fast Scanning** - Multi-threaded with up to 200 threads
- 💾 **Export Results** - Save to TXT, JSON, or CSV formats

### Advanced Scanning Modes
- 🌐 **Network Discovery** - Scan local network for active hosts
- 📌 **Common Ports** - Quick scan of frequently used ports
- 🔧 **Custom Ranges** - Define any port range you want
- ⏱️ **Adjustable Timeout** - Control connection timeout

### Result Export
- 📄 **Text Format** - Clean, readable text files
- 📋 **CSV Format** - Import into spreadsheets
- 📦 **JSON Format** - Structured data format

## 🚀 Quick Start

### Installation

```bash
pkg update && pkg upgrade -y
pkg install python3 pip git -y
git clone https://github.com/brixxwrldwide-bit/termux-ports-scanner.git
cd termux-ports-scanner
pip install -r requirements.txt
```

### Basic Usage

```bash
# Scan localhost (ports 1-1024)
python3 scanner.py

# Scan specific host
python3 scanner.py --host 192.168.1.1

# Scan custom port range
python3 scanner.py --host 8.8.8.8 --start 20 --end 500

# Scan common ports only (much faster)
python3 scanner.py --common

# Network discovery mode
python3 scanner.py --network
```

## 📖 Command Reference

### Scan Options

```
--host HOST              Target host to scan (default: 127.0.0.1)
--start PORT             Start port (default: 1)
--end PORT               End port (default: 1024)
--timeout SECONDS        Connection timeout (default: 2)
--threads COUNT          Number of threads (default: 200)
```

### Special Modes

```
--common                 Scan only well-known ports
--network                Network discovery mode
--export {txt,json,csv}  Export format
```

## 💡 Usage Examples

### Example 1: Scan localhost
```bash
python3 scanner.py
```
Scans all ports 1-1024 on localhost with beautiful dashboard

### Example 2: Scan specific host
```bash
python3 scanner.py --host 192.168.1.1
```
Scans target host with default settings

### Example 3: Fast common ports scan
```bash
python3 scanner.py --host 10.0.0.1 --common
```
Scans only common ports: 22, 80, 443, 3306, 5432, 8080, etc.

### Example 4: Network discovery
```bash
python3 scanner.py --network
```
Scans local network and lists all active hosts

### Example 5: Scan with export
```bash
python3 scanner.py --host 192.168.1.1 --export json
```
Scans and automatically exports results to JSON

### Example 6: Custom port range with high threads
```bash
python3 scanner.py --host example.com --start 1 --end 5000 --threads 300
```
Fast scan of ports 1-5000 with 300 threads

## 🎯 Dashboard Explained

The advanced dashboard shows:

```
╔════════════════════════════════════════════╗
║           🔍 Open Ports Scanner            ║
║       Advanced Terminal Edition            ║
╚════════════════════════════════════════════╝

Target Host: 192.168.1.1
Port Range: 1-1024
Threads: 200

[████████████░░░░░░░░░░░░░░░░░░░░░░░░] 35.0% (357/1024)

┌─ 📊 Statistics
│ Scanned: 357/1024
│ Open Ports: 8
│ Speed: 42.5 ports/sec
│ Elapsed: 8.4s
└

═══ OPEN PORTS ===
● 22    SSH
● 80    HTTP
● 443   HTTPS
● 3306  MySQL
```

## 📊 Supported Services

The scanner recognizes common services:

- **20, 21** - FTP (File Transfer)
- **22** - SSH (Secure Shell)
- **25, 587** - SMTP (Email)
- **53** - DNS (Domain Name)
- **80** - HTTP (Web)
- **110, 143** - POP3, IMAP (Email)
- **443** - HTTPS (Secure Web)
- **445** - SMB (File Sharing)
- **3306** - MySQL (Database)
- **3389** - RDP (Remote Desktop)
- **5432** - PostgreSQL (Database)
- **8080, 8443** - HTTP Alternate
- And more...

## 💾 Export Formats

### Text Format
```
============================================================
OPEN PORTS SCAN RESULTS
============================================================

Host: 192.168.1.1
Port Range: 1-1024
Total Scanned: 1024
Open Ports: 8
Scan Time: 2024-01-15 14:30:45

OPEN PORTS:
────────────────────────────────────────────────────────
Port    22: SSH
Port    80: HTTP
Port   443: HTTPS
Port  3306: MySQL
```

### JSON Format
```json
{
  "host": "192.168.1.1",
  "scan_time": "2024-01-15T14:30:45",
  "port_range": {
    "start": 1,
    "end": 1024
  },
  "total_scanned": 1024,
  "open_port_count": 8,
  "open_ports": {
    "22": "SSH",
    "80": "HTTP",
    "443": "HTTPS",
    "3306": "MySQL"
  }
}
```

### CSV Format
```
Port,Service,Status
22,SSH,OPEN
80,HTTP,OPEN
443,HTTPS,OPEN
3306,MySQL,OPEN
```

## ⚙️ Performance Tips

### For Slow Devices
```bash
# Reduce thread count
python3 scanner.py --threads 50

# Scan smaller range
python3 scanner.py --start 1 --end 500
```

### For Fast Scanning
```bash
# Increase thread count
python3 scanner.py --threads 500

# Scan common ports
python3 scanner.py --common

# Reduce timeout for unresponsive hosts
python3 scanner.py --timeout 1
```

## 🔐 Security & Legal Notice

⚠️ **Important**: This tool is for:
- **Authorized testing only**
- Your own networks
- Hosts you own or have permission to scan

**Unauthorized port scanning may be illegal.** Always:
- ✓ Get written permission before scanning
- ✓ Only scan networks you control
- ✓ Respect privacy and security laws

## 🛠️ Troubleshooting

### "Permission denied" error
- Some low-numbered ports require root
- Try scanning ports > 1024
- Or use: `sudo python3 scanner.py` (with caution)

### "Connection timeout"
- Increase timeout: `--timeout 5`
- Check network connectivity
- Verify host is reachable

### Slow scanning
- Reduce port range
- Use `--common` mode
- Check available threads

### App crashes
- Reduce thread count: `--threads 50`
- Reduce port range
- Increase timeout value

## 📋 Requirements

- Python 3.8+
- Termux (Android)
- Dependencies: colorama (for colors)

## 📚 Project Structure

```
termux-ports-scanner/
├── scanner.py           # Main application
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── LICENSE             # MIT License
```

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

MIT License - See LICENSE file

## 👨‍💻 Author

Created for Termux users by @brixxwrldwide-bit

---

**Happy Scanning!** 🎯
