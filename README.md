# GitHub Profile Views Booster

A powerful and efficient tool to boost your GitHub profile view counter using multi-threading and proxy support.

## Features

- **Fast Performance**: Multi-threaded architecture for maximum efficiency
- **Proxy Support**: Works with both regular IP:port and authenticated username:password@ip:port proxies
- **Clean UI**: Simple, informative interface with real-time statistics
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Detailed Statistics**: Track successful/failed requests and performance metrics

## Installation

### Prerequisites
- Python 3.6 or higher
- Internet connection

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/bhaskarsaikia-17/Github-View-Booster.git
   cd Github-View-Booster
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Edit the `config.json` file:

   ```json
   {
     "counter_url": "YOUR_GITHUB_COUNTER_URL",
     "threads": 100,
     "use_proxy": "y"
   }
   ```

   - `counter_url`: Your GitHub profile counter URL (see below for instructions)
   - `threads`: Number of concurrent threads (recommended: 50-100)
   - `use_proxy`: Use proxies from proxies.txt file ("y" or "n")

2. If using proxies, add them to `proxies.txt` file:
   - One proxy per line
   - Supports both formats:
     - `ip:port`
     - `username:password@ip:port`

## Usage

Run the program:

```
python main.py
```

The program will display real-time statistics including:
- Successful requests count
- Failed requests count
- Running time
- Requests per second

Press `CTRL+C` to stop the booster.

## How to Get Your GitHub Counter URL

1. Visit your GitHub profile
2. Look for the profile views counter (you may need to add one if you don't have it)
3. Right-click on the counter image and select "Copy Image Address"
4. The URL should look like: `https://camo.githubusercontent.com/...`
5. Paste this URL as the `counter_url` in your config.json file

## Example Counter Services

You can use one of these services to add a counter to your GitHub profile:
- [GitHub Profile Views Counter](https://github.com/antonkomarev/github-profile-views-counter)
- [Komarev Profile Views Counter](https://komarev.com/ghpvc)

## Disclaimer

This tool is for **EDUCATIONAL PURPOSES ONLY**. The developer is NOT responsible for any misuse of this software or any violations of GitHub's terms of service. Use at your own risk.

## Credits

Created by [bhaskarsaikia-17](https://github.com/bhaskarsaikia-17)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
