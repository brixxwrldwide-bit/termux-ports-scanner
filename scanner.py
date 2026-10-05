#!/usr/bin/env python3
"""
Termux Open Ports Scanner
A beautiful terminal UI for scanning open ports with live animations
"""

import socket
import threading
import time
import argparse
import json
from datetime import datetime
from queue import Queue
from collections import defaultdict
import signal
import sys
from ui import TerminalUI
import config

class PortScanner:
    """Multi-threaded port scanner"""
    
    # Common service ports
    SERVICES = {
        20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET",
        25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
        143: "IMAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS",
        587: "SMTP", 993: "IMAPS", 995: "POP3S", 1433: "SQL Server",
        3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
        8000: "Alt-HTTP", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt",
        8888: "Alt-HTTP", 9000: "SonarQube", 27017: "MongoDB"
    }
    
    def __init__(self, host, start_port, end_port, timeout=3, threads=200):
        self.host = host
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.threads = threads
        self.open_ports = {}
        self.scanned_ports = 0
        self.is_paused = False
        self.is_running = True
        self.results_queue = Queue()
        self.ui = TerminalUI()
        
    def get_service_name(self, port):
        """Get service name for port"""
        return self.SERVICES.get(port, "Unknown")
    
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
        """Worker thread function"""
        while self.is_running:
            try:
                port = port_queue.get(timeout=1)
                
                # Check if paused
                while self.is_paused and self.is_running:
                    time.sleep(0.1)
                
                if not self.is_running:
                    port_queue.task_done()
                    break
                
                is_open = self.check_port(port)
                
                if is_open:
                    service = self.get_service_name(port)
                    self.open_ports[port] = service
                    self.results_queue.put((port, service, True))
                else:
                    self.results_queue.put((port, None, False))
                
                self.scanned_ports += 1
                port_queue.task_done()
                
            except:
                try:
                    port_queue.task_done()
                except:
                    pass
    
    def scan(self, callback=None):
        """Start the scan"""
        port_range = self.end_port - self.start_port + 1
        port_queue = Queue()
        
        # Fill queue with ports
        for port in range(self.start_port, self.end_port + 1):
            port_queue.put(port)
        
        # Start worker threads
        thread_list = []
        for _ in range(min(self.threads, port_range)):
            t = threading.Thread(target=self.worker, args=(port_queue,))
            t.daemon = True
            t.start()
            thread_list.append(t)
        
        start_time = time.time()
        last_update = time.time()
        frame = 0
        
        try:
            while self.is_running:
                # Check for results
                while not self.results_queue.empty():
                    try:
                        port, service, is_open = self.results_queue.get_nowait()
                        if callback and is_open:
                            callback(port, service)
                    except:
                        pass
                
                # Update progress
                current_time = time.time()
                if current_time - last_update > config.REFRESH_RATE:
                    if callback:
                        self.ui.print_progress_bar(self.scanned_ports, port_range)
                    last_update = current_time
                    frame += 1
                
                # Check if scan is complete
                if port_queue.empty() and self.scanned_ports >= port_range:
                    break
                
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            self.is_running = False
        
        # Wait for all threads
        for t in thread_list:
            t.join(timeout=1)
        
        duration = time.time() - start_time
        return duration
    
    def pause(self):
        """Pause scanning"""
        self.is_paused = not self.is_paused
    
    def stop(self):
        """Stop scanning"""
        self.is_running = False


class InteractiveScannerUI:
    """Interactive UI wrapper for scanner"""
    
    def __init__(self):
        self.ui = TerminalUI()
        self.scanner = None
        self.current_scan_data = []
    
    def run_scan(self, host, start_port, end_port, threads=200, timeout=3):
        """Run interactive scan"""
        self.ui.clear_screen()
        self.ui.print_header("Termux Ports Scanner", "🔍 Live Port Scanner")
        self.ui.print_scan_info(host, start_port, end_port, threads)
        
        self.scanner = PortScanner(host, start_port, end_port, timeout, threads)
        
        def on_port_found(port, service):
            self.current_scan_data.append((port, service))
            self.ui.print_port_result(port, True, service)
        
        print(f"\n{self.ui.create_animation_frame(0)} Starting scan...\n")
        time.sleep(0.5)
        
        duration = self.scanner.scan(callback=on_port_found)
        
        print("\n")
        self.ui.print_summary(self.scanner.open_ports, 
                             self.scanner.end_port - self.scanner.start_port + 1,
                             duration)
        
        # Display results
        if self.scanner.open_ports:
            self.ui.print_open_ports_list(self.scanner.open_ports)
        else:
            self.ui.print_warning("No open ports found")
        
        self.ui.print_legend()
        
        # Save option
        self.offer_export()
    
    def offer_export(self):
        """Offer to export results"""
        if not self.scanner or not self.scanner.open_ports:
            return
        
        response = input(f"Export results? (y/n): ").lower()
        if response == 'y':
            self.export_results()
    
    def export_results(self):
        """Export scan results"""
        if not self.scanner or not self.scanner.open_ports:
            return
        
        filename = f"scan_{self.scanner.host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("=== Port Scan Results ===\n")
                f.write(f"Host: {self.scanner.host}\n")
                f.write(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Ports Scanned: {self.scanner.end_port - self.scanner.start_port + 1}\n")
                f.write(f"Open Ports: {len(self.scanner.open_ports)}\n\n")
                f.write("Open Ports:\n")
                f.write("-" * 40 + "\n")
                
                for port in sorted(self.scanner.open_ports.keys()):
                    service = self.scanner.open_ports[port]
                    f.write(f"Port {port}: {service}\n")
            
            self.ui.print_success(f"Results exported to {filename}")
        except Exception as e:
            self.ui.print_error(f"Failed to export: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Termux Open Ports Scanner - Beautiful terminal UI for port scanning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 scanner.py                           # Scan localhost ports 1-1024
  python3 scanner.py --host 192.168.1.1       # Scan specific host
  python3 scanner.py --host 8.8.8.8 --start 1 --end 100  # Custom range
  python3 scanner.py --common                  # Scan common ports only
        '''
    )
    
    parser.add_argument('--host', default='127.0.0.1',
                       help='Target host to scan (default: 127.0.0.1)')
    parser.add_argument('--start', type=int, default=1,
                       help='Start port (default: 1)')
    parser.add_argument('--end', type=int, default=1024,
                       help='End port (default: 1024)')
    parser.add_argument('--timeout', type=float, default=3,
                       help='Connection timeout in seconds (default: 3)')
    parser.add_argument('--threads', type=int, default=200,
                       help='Number of threads (default: 200)')
    parser.add_argument('--common', action='store_true',
                       help='Scan only common ports')
    
    args = parser.parse_args()
    
    # Handle common ports mode
    if args.common:
        args.start = min(config.COMMON_PORTS)
        args.end = max(config.COMMON_PORTS)
    
    try:
        scanner_ui = InteractiveScannerUI()
        scanner_ui.run_scan(args.host, args.start, args.end, args.threads, args.timeout)
    
    except KeyboardInterrupt:
        print(f"\n\n{scanner_ui.ui.ui.create_animation_frame(0) if 'scanner_ui' in locals() else ''} Scan interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
