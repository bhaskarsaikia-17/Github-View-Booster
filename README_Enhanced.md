# 🚀 GitHub Profile Views Booster - Enhanced Edition

A powerful, async-based GitHub profile views booster with WebSocket monitoring, advanced rate limiting, and real-time statistics.

## ✨ New Features

### 🔄 Async Architecture
- **Asynchronous requests** using `aiohttp` for better performance
- **Concurrent workers** instead of threads for efficiency
- **Non-blocking operations** with proper async/await patterns

### 📊 WebSocket Monitoring
- **Real-time dashboard** via WebSocket server
- **Live statistics** updates without polling
- **Remote monitoring** capability
- **Beautiful HTML dashboard** included (`monitor.html`)

### 🛡️ Advanced Error Handling
- **Intelligent retry mechanisms** with exponential backoff
- **Proxy health checking** and automatic rotation
- **Rate limiting protection** with configurable throttling
- **Graceful shutdown** handling

### 📈 Enhanced Statistics
- **Detailed metrics** including success rates, timeouts, proxy errors
- **System monitoring** (CPU, memory, network usage)
- **Proxy statistics** tracking
- **Performance metrics** (requests per second)

### ⚙️ Improved Configuration
- **JSON-based config** with extensive options
- **Rate limiting** settings
- **WebSocket server** configuration
- **Request timeouts** and retry settings
- **Multiple user agents** rotation

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Settings
Edit `config.json`:
```json
{
    "counter_url": "your_github_camo_url_here",
    "concurrent_workers": 50,
    "use_proxy": true,
    "rate_limit": {
        "requests_per_second": 10,
        "burst_size": 20
    },
    "websocket": {
        "enabled": true,
        "host": "localhost",
        "port": 8765
    }
}
```

### 3. Add Proxies (Optional)
Add your proxies to `proxies.txt`:
```
ip:port
username:password@ip:port
```

### 4. Run the Booster
```bash
py main.py
```

### 5. Monitor via WebSocket
Open `monitor.html` in your browser for real-time monitoring dashboard.

## 🎛️ Configuration Options

### Core Settings
- `counter_url`: Your GitHub profile counter URL
- `concurrent_workers`: Number of async workers (default: 50)
- `use_proxy`: Enable/disable proxy usage

### Rate Limiting
- `requests_per_second`: Maximum requests per second
- `burst_size`: Burst allowance for rate limiting

### WebSocket Server
- `enabled`: Enable WebSocket monitoring server
- `host`: Server host (default: localhost)
- `port`: Server port (default: 8765)

### Request Settings
- `timeout`: Request timeout in seconds
- `max_retries`: Maximum retry attempts
- `retry_delay`: Base delay between retries
- `user_agents`: List of user agents to rotate

### Monitoring
- `stats_update_interval`: Stats refresh interval
- `enable_system_monitoring`: Enable system metrics

## 📊 WebSocket API

Connect to `ws://localhost:8765` for real-time monitoring.

### Commands
- `{"command": "get_stats"}` - Request current statistics
- `{"command": "reset_stats"}` - Reset all counters

### Response Format
```json
{
    "type": "stats_update",
    "timestamp": "2024-01-15T10:30:00",
    "stats": {
        "successful_requests": 1250,
        "failed_requests": 45,
        "success_rate": 96.5,
        "requests_per_second": 8.3
    },
    "system": {
        "cpu_percent": 15.2,
        "memory_percent": 42.1,
        "memory_used_mb": 128.5
    },
    "proxy": {
        "total": 50,
        "working": 48,
        "failed": 2,
        "success_rate": 96.0
    }
}
```

## 🛠️ Advanced Features

### Proxy Management
- **Automatic rotation** of working proxies
- **Health checking** with failed proxy removal
- **Statistics tracking** per proxy
- **Format support** for authenticated proxies

### System Monitoring
- **CPU usage** tracking
- **Memory consumption** monitoring
- **Network bandwidth** measurement
- **Real-time updates** via dashboard

### Error Recovery
- **Automatic reconnection** for failed connections
- **Exponential backoff** for retries
- **Graceful degradation** when proxies fail
- **Signal handling** for clean shutdown

## 🎨 Dashboard Features

The included `monitor.html` provides:
- 📊 **Real-time statistics** with live updates
- 💻 **System resource monitoring**
- 🌐 **Proxy health dashboard**
- 🎛️ **Remote control** capabilities
- 📈 **Progress visualization**
- 🎨 **Beautiful, responsive UI**

## 🔧 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if port 8765 is available
   - Verify firewall settings
   - Ensure WebSocket is enabled in config

2. **High Memory Usage**
   - Reduce `concurrent_workers` count
   - Check for proxy connection issues
   - Monitor system resources

3. **Low Success Rate**
   - Verify proxy quality
   - Adjust rate limiting settings
   - Check target URL validity

## 📝 Performance Tips

1. **Optimal Worker Count**: Start with 50 workers and adjust based on system performance
2. **Rate Limiting**: Don't exceed 10-15 requests per second to avoid detection
3. **Proxy Quality**: Use high-quality, rotating proxies for better success rates
4. **System Resources**: Monitor CPU and memory usage via the dashboard

## 🛡️ Security Considerations

- **Proxy Credentials**: Store proxy credentials securely
- **Rate Limiting**: Respect target server limits
- **WebSocket Access**: Restrict WebSocket server access as needed
- **Local Network**: Consider running on isolated network environments

## 🤝 Credits

**Crafted With ❤️ By Bhaskar**

### Technologies Used
- **Python 3.8+** - Core language
- **aiohttp** - Async HTTP client
- **websockets** - WebSocket server
- **Rich** - Beautiful terminal interface
- **psutil** - System monitoring
- **asyncio-throttle** - Rate limiting

## 📄 License

This project is for educational purposes only. Please use responsibly and respect GitHub's terms of service.
