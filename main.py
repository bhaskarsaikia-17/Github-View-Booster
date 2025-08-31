#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import asyncio
import aiohttp
import websockets
import time
import platform
import random
import signal
import sys
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    import psutil
    from asyncio_throttle import Throttler
except ModuleNotFoundError:
    print('[>] Modules not found! Installing, please wait...')
    os.system('pip install -r requirements.txt')
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    print('[>] Download successfully completed! The booster will start in 3 seconds.')
    time.sleep(3)
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    import psutil
    from asyncio_throttle import Throttler

# Initialize Rich console
console = Console()

@dataclass
class Statistics:
    """Statistics tracking for the booster"""
    successful_requests: int = 0
    failed_requests: int = 0
    proxy_errors: int = 0
    timeout_errors: int = 0
    rate_limited: int = 0
    start_time: float = 0
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    
    @property
    def total_requests(self) -> int:
        return self.successful_requests + self.failed_requests
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    @property
    def requests_per_second(self) -> float:
        if self.elapsed_time == 0:
            return 0.0
        return self.successful_requests / self.elapsed_time

@dataclass 
class SystemStats:
    """System monitoring statistics"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0

class ProxyManager:
    """Advanced proxy management with rotation and health checking"""
    
    def __init__(self, proxy_file: str = "proxies.txt"):
        self.proxy_file = proxy_file
        self.proxies: List[str] = []
        self.working_proxies: List[str] = []
        self.failed_proxies: set = set()
        self.proxy_stats: Dict[str, Dict] = {}
        self.load_proxies()
    
    def load_proxies(self):
        """Load proxies from file"""
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            self.working_proxies = self.proxies.copy()
            console.print(f"[green]Loaded {len(self.proxies)} proxies[/green]")
        except FileNotFoundError:
            console.print(f"[yellow]Warning: {self.proxy_file} not found. Running without proxies.[/yellow]")
    
    def format_proxy(self, proxy: str) -> str:
        """Format proxy string to aiohttp compatible format"""
        if '@' in proxy:
            auth, ip_port = proxy.split('@')
            return f"http://{auth}@{ip_port}"
        else:
            return f"http://{proxy}"
    
    def get_random_proxy(self) -> Optional[str]:
        """Get a random working proxy"""
        if not self.working_proxies:
            return None
        return random.choice(self.working_proxies)
    
    def mark_proxy_failed(self, proxy: str):
        """Mark a proxy as failed and remove from working list"""
        self.failed_proxies.add(proxy)
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
    
    def get_proxy_stats(self) -> Dict:
        """Get proxy statistics"""
        return {
            "total": len(self.proxies),
            "working": len(self.working_proxies),
            "failed": len(self.failed_proxies),
            "success_rate": (len(self.working_proxies) / len(self.proxies) * 100) if self.proxies else 0
        }

class WebSocketServer:
    """WebSocket server for real-time monitoring and control"""
    
    def __init__(self, host: str, port: int, stats: Statistics, proxy_manager: ProxyManager):
        self.host = host
        self.port = port
        self.stats = stats
        self.proxy_manager = proxy_manager
        self.clients: set = set()
        self.running = False
    
    async def register_client(self, websocket):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        console.print(f"[blue]WebSocket client connected from {websocket.remote_address}[/blue]")
    
    async def unregister_client(self, websocket):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        console.print(f"[blue]WebSocket client disconnected[/blue]")
    
    async def broadcast_stats(self):
        """Broadcast statistics to all connected clients"""
        if not self.clients:
            return
        
        system_stats = get_system_stats()
        proxy_stats = self.proxy_manager.get_proxy_stats()
        
        data = {
            "type": "stats_update",
            "timestamp": datetime.now().isoformat(),
            "stats": asdict(self.stats),
            "system": asdict(system_stats),
            "proxy": proxy_stats
        }
        
        message = json.dumps(data)
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Remove disconnected clients
        for client in disconnected:
            await self.unregister_client(client)
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_command(websocket, data)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    async def handle_command(self, websocket, data):
        """Handle commands from WebSocket clients"""
        command = data.get("command")
        
        if command == "get_stats":
            await self.broadcast_stats()
        elif command == "reset_stats":
            self.stats.successful_requests = 0
            self.stats.failed_requests = 0
            self.stats.start_time = time.time()
            await websocket.send(json.dumps({"type": "command_response", "message": "Stats reset"}))
    
    async def start_server(self):
        """Start the WebSocket server"""
        self.running = True
        try:
            server = await websockets.serve(self.handle_client, self.host, self.port)
            console.print(f"[green]WebSocket server started on ws://{self.host}:{self.port}[/green]")
            
            # Broadcast stats periodically
            while self.running:
                await asyncio.sleep(2)
                await self.broadcast_stats()
        except Exception as e:
            console.print(f"[red]WebSocket server error: {e}[/red]")
    
    def stop(self):
        """Stop the WebSocket server"""
        self.running = False

class GitHubViewBooster:
    """Main booster class with async support and advanced features"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.stats = Statistics()
        self.proxy_manager = ProxyManager() if self.config["use_proxy"] else None
        self.throttler = Throttler(
            rate_limit=self.config["rate_limit"]["requests_per_second"],
            period=1.0
        )
        self.user_agents = self.config["request_settings"]["user_agents"]
        self.websocket_server = None
        self.running = False
        self.tasks: List[asyncio.Task] = []
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"[red]Error: {config_file} not found![/red]")
            sys.exit(1)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error parsing {config_file}: {e}[/red]")
            sys.exit(1)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        console.print(f"\n[yellow]Received signal {signum}. Shutting down gracefully...[/yellow]")
        self.stop()
    
    async def make_request(self, session: aiohttp.ClientSession) -> bool:
        """Make a single request with advanced error handling and retries"""
        max_retries = self.config["request_settings"]["max_retries"]
        retry_delay = self.config["request_settings"]["retry_delay"]
        
        for attempt in range(max_retries + 1):
            try:
                # Rate limiting
                async with self.throttler:
                    proxy = None
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    
                    if self.proxy_manager:
                        proxy_str = self.proxy_manager.get_random_proxy()
                        if proxy_str:
                            proxy = self.proxy_manager.format_proxy(proxy_str)
                    
                    timeout = aiohttp.ClientTimeout(total=self.config["request_settings"]["timeout"])
                    
                    async with session.get(
                        self.config["counter_url"],
                        proxy=proxy,
                        headers=headers,
                        timeout=timeout
                    ) as response:
                        content = await response.read()
                        self.stats.total_bytes_received += len(content)
                        
                        if response.status == 200:
                            self.stats.successful_requests += 1
                            return True
                        elif response.status == 429:  # Rate limited
                            self.stats.rate_limited += 1
                            await asyncio.sleep(retry_delay * 2)
                            continue
                        else:
                            self.stats.failed_requests += 1
                            return False
            
            except aiohttp.ClientProxyConnectionError:
                self.stats.proxy_errors += 1
                if self.proxy_manager and proxy_str:
                    self.proxy_manager.mark_proxy_failed(proxy_str)
            except (aiohttp.ClientTimeout, asyncio.TimeoutError):
                self.stats.timeout_errors += 1
            except Exception as e:
                self.stats.failed_requests += 1
                if attempt == max_retries:
                    console.print(f"[red]Request failed after {max_retries} retries: {e}[/red]")
            
            if attempt < max_retries:
                await asyncio.sleep(retry_delay * (attempt + 1))
        
        self.stats.failed_requests += 1
        return False
    
    async def worker(self, worker_id: int, session: aiohttp.ClientSession):
        """Worker coroutine that makes continuous requests"""
        while self.running:
            try:
                await self.make_request(session)
                # Small delay between requests per worker
                await asyncio.sleep(0.1)
            except Exception as e:
                console.print(f"[red]Worker {worker_id} error: {e}[/red]")
                await asyncio.sleep(1)
    
    def create_display_layout(self) -> Layout:
        """Create the display layout for real-time stats"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        layout["main"].split_row(
            Layout(name="stats"),
            Layout(name="system")
        )
        return layout
    
    def update_display(self, layout: Layout):
        """Update the display with current statistics"""
        # Header
        layout["header"].update(Panel(
            Text("🚀 GitHub Profile Views Booster - Enhanced Edition", style="bold cyan", justify="center"),
            style="blue"
        ))
        
        # Stats table
        stats_table = Table(title="📊 Request Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        elapsed = self.stats.elapsed_time
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        stats_table.add_row("✅ Successful", str(self.stats.successful_requests))
        stats_table.add_row("❌ Failed", str(self.stats.failed_requests))
        stats_table.add_row("🚫 Proxy Errors", str(self.stats.proxy_errors))
        stats_table.add_row("⏰ Timeouts", str(self.stats.timeout_errors))
        stats_table.add_row("🛑 Rate Limited", str(self.stats.rate_limited))
        stats_table.add_row("📈 Success Rate", f"{self.stats.success_rate:.1f}%")
        stats_table.add_row("⚡ Req/sec", f"{self.stats.requests_per_second:.2f}")
        stats_table.add_row("🕐 Runtime", f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        
        layout["stats"].update(Panel(stats_table, style="blue"))
        
        # System stats
        system_stats = get_system_stats()
        system_table = Table(title="💻 System Monitor")
        system_table.add_column("Resource", style="cyan")
        system_table.add_column("Usage", style="yellow")
        
        system_table.add_row("🔥 CPU", f"{system_stats.cpu_percent:.1f}%")
        system_table.add_row("🧠 Memory", f"{system_stats.memory_percent:.1f}%")
        system_table.add_row("💾 Memory Used", f"{system_stats.memory_used_mb:.1f} MB")
        system_table.add_row("📤 Network Out", f"{system_stats.network_sent_mb:.1f} MB")
        system_table.add_row("📥 Network In", f"{system_stats.network_recv_mb:.1f} MB")
        
        if self.proxy_manager:
            proxy_stats = self.proxy_manager.get_proxy_stats()
            system_table.add_row("🌐 Proxies Working", f"{proxy_stats['working']}/{proxy_stats['total']}")
        
        layout["system"].update(Panel(system_table, style="green"))
        
        # Footer
        footer_text = "Press Ctrl+C to stop | WebSocket: "
        if self.config["websocket"]["enabled"]:
            footer_text += f"ws://{self.config['websocket']['host']}:{self.config['websocket']['port']}"
        else:
            footer_text += "Disabled"
        
        layout["footer"].update(Panel(
            Text(footer_text, style="bold white", justify="center"),
            style="yellow"
        ))
    
    async def start_websocket_server(self):
        """Start the WebSocket server if enabled"""
        if self.config["websocket"]["enabled"]:
            self.websocket_server = WebSocketServer(
                self.config["websocket"]["host"],
                self.config["websocket"]["port"],
                self.stats,
                self.proxy_manager or ProxyManager()
            )
            task = asyncio.create_task(self.websocket_server.start_server())
            self.tasks.append(task)
    
    async def run(self):
        """Main run method with async support"""
        self.running = True
        self.stats.start_time = time.time()
        
        # Start WebSocket server
        await self.start_websocket_server()
        
        # Create display layout
        layout = self.create_display_layout()
        
        # Create aiohttp session with connection pooling
        connector = aiohttp.TCPConnector(
            limit=self.config["concurrent_workers"] * 2,
            limit_per_host=self.config["concurrent_workers"],
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Start worker tasks
            for i in range(self.config["concurrent_workers"]):
                task = asyncio.create_task(self.worker(i, session))
                self.tasks.append(task)
            
            console.print(f"[green]🚀 Started {self.config['concurrent_workers']} async workers[/green]")
            console.print(f"[blue]🎯 Target: {self.config['counter_url'][:60]}...[/blue]")
            
            # Live display update
            try:
                with Live(layout, refresh_per_second=2, screen=True) as live:
                    while self.running:
                        self.update_display(layout)
                        live.update(layout)
                        await asyncio.sleep(self.config["monitoring"]["stats_update_interval"])
            except KeyboardInterrupt:
                pass
        
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources and stop all tasks"""
        console.print("\n[yellow]🛑 Stopping booster...[/yellow]")
        self.running = False
        
        if self.websocket_server:
            self.websocket_server.stop()
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        console.print(f"[green]✅ Successfully boosted {self.stats.successful_requests} views![/green]")
        console.print(f"[blue]📊 Final success rate: {self.stats.success_rate:.1f}%[/blue]")
    
    def stop(self):
        """Stop the booster"""
        self.running = False

def get_system_stats() -> SystemStats:
    """Get current system statistics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        network = psutil.net_io_counters()
        
        return SystemStats(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            network_sent_mb=network.bytes_sent / 1024 / 1024,
            network_recv_mb=network.bytes_recv / 1024 / 1024
        )
    except Exception:
        return SystemStats()

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

async def main():
    """Main entry point"""
    clear_screen()
    
    # Display banner
    console.print(Panel.fit(
        "[bold cyan]🚀 GitHub Profile Views Booster[/bold cyan]\n"
        "[bold green]Enhanced Edition with WebSockets & Async Support[/bold green]\n"
        "[dim]Crafted With ❤️ By Bhaskar[/dim]",
        style="blue"
    ))
    
    # Initialize and run booster
    booster = GitHubViewBooster()
    try:
        await booster.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]💥 Fatal error: {e}[/red]")
    finally:
        await booster.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")

# Crafted With ❤️ By Bhaskar
