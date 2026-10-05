#!/usr/bin/env python3
"""
Termux Open Ports Scanner - Advanced Edition
Beautiful terminal UI with dashboard, network scanning, and export features
"""

import socket
import threading
import time
import argparse
import json
import csv
import os
from datetime import datetime
from queue import Queue
from collections import defaultdict
import signal
import sys

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = CYAN = BLUE = MAGENTA = WHITE = ''
    class Back:
        RED = GREEN = YELLOW = CYAN = BLUE = MAGENTA = WHITE = ''
    class Style:
        RESET_ALL = BRIGHT = DIM = ''

COMMON_PORTS = [20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 465, 587, 993, 995, 1433, 3306, 3389, 5432, 5900, 8000, 8080, 8443, 8888, 9000]

SERVICES = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS",
    587: "SMTP", 993: "IMAPS", 995: "POP3S", 1433: "SQL Server", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 8000: "Alt-HTTP", 8080: "HTTP-Proxy",
    8443: "HTTPS-Alt", 8888: "Alt-HTTP", 9000: "SonarQube", 27017: "MongoDB"
}

class Dashboard:
    """Advanced terminal dashboard"""
    
    def __init__(self):
        self.width = self.get_width()
        self.height = self.get_height()
    
    def get_width(self):
        try:
            return os.get_terminal_size().columns
        except:
            return 100
    
    def get_height(self):
        try:
            return os.get_terminal_size().lines
        except:
            return 30
    
    def clear(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def center(self, text):
        """Center text"""
        padding = (self.width - len(text)) // 2
        return ' ' * padding + text
    
    def header(self, title, subtitle=""):
        """Print styled header"""
        print(f"{Fore.CYAN}{'═' * self.width}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.center(title)}{Style.RESET_ALL}")
        if subtitle:
            print(f"{Fore.YELLOW}{self.center(subtitle)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'═' * self.width}{Style.RESET_ALL}\n")
    
    def footer(self, text):
        """Print footer"""
        print(f"{Fore.CYAN}{'─' * self.width}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.center(text)}{Style.RESET_ALL}")
    
    def progress_bar(self, current, total, width=40):
        """Animated progress bar"""
        if total == 0:
            percent = 0
            filled = 0
        else:
            percent = (current / total) * 100
            filled = int(width * current / total)
        
        bar = '█' * filled + '░' * (width - filled)
        return f"{Fore.YELLOW}[{bar}] {percent:5.1f}% ({current}/{total}){Style.RESET_ALL}"
    
    def info_box(self, title, lines):
        """Print info box"""
        print(f"{Fore.CYAN}┌─ {title}{Style.RESET_ALL}")
        for line in lines:
            print(f"{Fore.CYAN}│{Style.RESET_ALL} {line}")
        print(f"{Fore.CYAN}└{Style.RESET_ALL}")
    
    def port_entry(self, port, service, is_open=True):
        """Format port entry"""
        if is_open:
            status = f"{Fore.GREEN}●{Style.RESET_ALL}"
            color = Fore.GREEN
        else:
            status = f"{Fore.RED}●{Style.RESET_ALL}"
            color = Fore.RED
        
        return f"{status} {color}{str(port).ljust(6)}{Style.RESET_ALL} {service}"
    
    def spinner_frame(self, frame):
        """Get spinner frame"""
        frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        return frames[frame % len(frames)]


class PortScanner:
    """Advanced port scanner with network scanning"""
    
    def __init__(self, host, start_port=1, end_port=1024, timeout=2, threads=200):
        self.host = host
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.threads_count = threads
        self.open_ports = {}
        self.closed_ports = {}
        self.scanned = 0
        self.is_running = True
        self.is_paused = False
        self.start_time = None
        self.results_queue = Queue()
        self.dashboard = Dashboard()
    
    def check_port(self, port):
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def worker(self, port_queue):
        """Worker thread"""
        while self.is_running:
            try:
                port = port_queue.get(timeout=1)
                
                while self.is_paused and self.is_running:
                    time.sleep(0.1)
                
                if not self.is_running:
                    port_queue.task_done()
                    break
                
                is_open = self.check_port(port)
                service = SERVICES.get(port, "Unknown")
                
                if is_open:
                    self.open_ports[port] = service
                else:
                    self.closed_ports[port] = service
                
                self.scanned += 1
                port_queue.task_done()
                
            except:
                try:
                    port_queue.task_done()
                except:
                    pass
    
    def scan(self):
        """Start scan"""
        self.start_time = time.time()
        port_range = self.end_port - self.start_port + 1
        port_queue = Queue()
        
        for port in range(self.start_port, self.end_port + 1):
            port_queue.put(port)
        
        threads = []
        for _ in range(min(self.threads_count, port_range)):
            t = threading.Thread(target=self.worker, args=(port_queue,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        self.render_scan(port_range)
        
        for t in threads:
            t.join(timeout=1)
        
        return time.time() - self.start_time
    
    def render_scan(self, total):
        """Render scan progress"""
        frame = 0
        last_open_count = 0
        
        while self.scanned < total and self.is_running:
            self.dashboard.clear()
            self.dashboard.header("🔍 Open Ports Scanner", "Advanced Terminal Edition")
            
            # Scan info
            print(f"{Fore.CYAN}Target Host: {Fore.GREEN}{self.host}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Port Range: {Fore.GREEN}{self.start_port}-{self.end_port}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Threads: {Fore.GREEN}{self.threads_count}{Style.RESET_ALL}\n")
            
            # Progress bar
            print(self.dashboard.progress_bar(self.scanned, total))
            print()
            
            # Statistics
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                speed = self.scanned / elapsed
            else:
                speed = 0
            
            stats = [
                f"Scanned: {self.scanned}/{total}",
                f"Open Ports: {Fore.GREEN}{len(self.open_ports)}{Style.RESET_ALL}",
                f"Speed: {Fore.YELLOW}{speed:.1f} ports/sec{Style.RESET_ALL}",
                f"Elapsed: {Fore.CYAN}{elapsed:.1f}s{Style.RESET_ALL}"
            ]
            
            self.dashboard.info_box("📊 Statistics", stats)
            print()
            
            # Open ports display
            if self.open_ports:
                print(f"{Fore.GREEN}═══ OPEN PORTS ==={Style.RESET_ALL}")
                for port, service in sorted(self.open_ports.items())[:8]:
                    print(self.dashboard.port_entry(port, service, True))
                if len(self.open_ports) > 8:
                    print(f"{Fore.YELLOW}... and {len(self.open_ports) - 8} more{Style.RESET_ALL}")
                print()
            
            # Footer
            spinner = self.dashboard.spinner_frame(frame)
            self.dashboard.footer(f"{spinner} Scanning... Press Ctrl+C to stop")
            
            frame += 1
            time.sleep(0.15)
    
    def display_results(self):
        """Display final results"""
        self.dashboard.clear()
        self.dashboard.header("🎯 Scan Results", f"Target: {self.host}")
        
        elapsed = time.time() - self.start_time
        
        # Summary
        summary = [
            f"Total Scanned: {self.scanned}",
            f"Open Ports: {Fore.GREEN}{len(self.open_ports)}{Style.RESET_ALL}",
            f"Duration: {Fore.CYAN}{elapsed:.2f}s{Style.RESET_ALL}",
            f"Completed: {datetime.now().strftime('%H:%M:%S')}"
        ]
        self.dashboard.info_box("📈 Summary", summary)
        print()
        
        # Open ports
        if self.open_ports:
            print(f"{Fore.GREEN}═══ OPEN PORTS ({len(self.open_ports)}) ==={Style.RESET_ALL}")
            for port, service in sorted(self.open_ports.items()):
                print(self.dashboard.port_entry(port, service, True))
        else:
            print(f"{Fore.RED}No open ports found{Style.RESET_ALL}")
        
        print()
        self.dashboard.footer(f"Scan completed successfully")


class ScanExporter:
    """Export scan results to various formats"""
    
    @staticmethod
    def to_txt(scanner, filename=None):
        """Export to text file"""
        if not filename:
            filename = f"scan_{scanner.host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("="*60 + "\n")
                f.write("OPEN PORTS SCAN RESULTS\n")
                f.write("="*60 + "\n\n")
                f.write(f"Host: {scanner.host}\n")
                f.write(f"Port Range: {scanner.start_port}-{scanner.end_port}\n")
                f.write(f"Total Scanned: {scanner.scanned}\n")
                f.write(f"Open Ports: {len(scanner.open_ports)}\n")
                f.write(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("OPEN PORTS:\n")
                f.write("-"*60 + "\n")
                for port, service in sorted(scanner.open_ports.items()):
                    f.write(f"Port {port:>5}: {service}\n")
            
            return filename
        except Exception as e:
            print(f"{Fore.RED}Export failed: {e}{Style.RESET_ALL}")
            return None
    
    @staticmethod
    def to_json(scanner, filename=None):
        """Export to JSON file"""
        if not filename:
            filename = f"scan_{scanner.host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            data = {
                "host": scanner.host,
                "scan_time": datetime.now().isoformat(),
                "port_range": {"start": scanner.start_port, "end": scanner.end_port},
                "total_scanned": scanner.scanned,
                "open_ports": scanner.open_ports,
                "open_port_count": len(scanner.open_ports)
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return filename
        except Exception as e:
            print(f"{Fore.RED}Export failed: {e}{Style.RESET_ALL}")
            return None
    
    @staticmethod
    def to_csv(scanner, filename=None):
        """Export to CSV file"""
        if not filename:
            filename = f"scan_{scanner.host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            import csv as csv_module
            with open(filename, 'w', newline='') as f:
                writer = csv_module.writer(f)
                writer.writerow(['Port', 'Service', 'Status'])
                for port, service in sorted(scanner.open_ports.items()):
                    writer.writerow([port, service, 'OPEN'])
            
            return filename
        except Exception as e:
            print(f"{Fore.RED}Export failed: {e}{Style.RESET_ALL}")
            return None


class NetworkScanner:
    """Scan local network for active hosts"""
    
    @staticmethod
    def get_local_network():
        """Get local network info"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            
            # Get network range (assume /24)
            base = '.'.join(ip.split('.')[:-1])
            return base
        except:
            return "192.168.1"
    
    @staticmethod
    def ping_host(host, timeout=1):
        """Check if host is reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, 22))  # Try SSH port
            sock.close()
            return result == 0
        except:
            return False
    
    @staticmethod
    def scan_network(base_ip, dashboard):
        """Scan network for active hosts"""
        active_hosts = []
        
        dashboard.clear()
        dashboard.header("🌐 Network Discovery", f"Scanning {base_ip}.0/24")
        
        threads = []
        results = []
        lock = threading.Lock()
        
        def check_host_thread(ip):
            if NetworkScanner.ping_host(ip, 1):
                with lock:
                    results.append(ip)
                    print(f"{Fore.GREEN}✓{Style.RESET_ALL} {ip} is reachable")
        
        print(f"\nScanning {base_ip}.1-{base_ip}.254...\n")
        
        for i in range(1, 255):
            host = f"{base_ip}.{i}"
            t = threading.Thread(target=check_host_thread, args=(host,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join(timeout=5)
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Termux Advanced Ports Scanner',
        epilog='''Examples:
  python3 scanner.py
  python3 scanner.py --host 192.168.1.1
  python3 scanner.py --common
  python3 scanner.py --network
  python3 scanner.py --export json
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--host', default='127.0.0.1', help='Target host')
    parser.add_argument('--start', type=int, default=1, help='Start port')
    parser.add_argument('--end', type=int, default=1024, help='End port')
    parser.add_argument('--timeout', type=float, default=2, help='Socket timeout')
    parser.add_argument('--threads', type=int, default=200, help='Thread count')
    parser.add_argument('--common', action='store_true', help='Scan common ports only')
    parser.add_argument('--network', action='store_true', help='Network discovery mode')
    parser.add_argument('--export', choices=['txt', 'json', 'csv'], help='Export format')
    
    args = parser.parse_args()
    
    if args.common:
        args.start = min(COMMON_PORTS)
        args.end = max(COMMON_PORTS)
    
    try:
        if args.network:
            # Network discovery mode
            dashboard = Dashboard()
            base = NetworkScanner.get_local_network()
            hosts = NetworkScanner.scan_network(base, dashboard)
            
            if hosts:
                print(f"\n{Fore.GREEN}Found {len(hosts)} active hosts:{Style.RESET_ALL}")
                for host in sorted(hosts):
                    print(f"  {host}")
        else:
            # Port scanning mode
            scanner = PortScanner(
                args.host,
                args.start,
                args.end,
                args.timeout,
                args.threads
            )
            
            scanner.scan()
            scanner.display_results()
            
            # Export option
            if args.export or input(f"\n{Fore.CYAN}Export results? (y/n): {Style.RESET_ALL}").lower() == 'y':
                export_fmt = args.export or input(f"{Fore.CYAN}Format (txt/json/csv): {Style.RESET_ALL}")
                
                exporter = ScanExporter()
                if export_fmt == 'json':
                    filename = exporter.to_json(scanner)
                elif export_fmt == 'csv':
                    filename = exporter.to_csv(scanner)
                else:
                    filename = exporter.to_txt(scanner)
                
                if filename:
                    print(f"\n{Fore.GREEN}✓ Saved to {filename}{Style.RESET_ALL}")
    
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Scan interrupted{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == '__main__':
    main()
