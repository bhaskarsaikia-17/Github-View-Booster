#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import threading
import httpx
import time
import platform
from os import system
from time import sleep
from random import choice

try:
    from colorama import Fore, Style, init
    from tqdm import tqdm

except ModuleNotFoundError:
    print('[>] Modules not found! Installing, please wait...')
    os.system('pip install -r requirements.txt')
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    print('[>] Download successfully completed! The booster will start in 3 seconds.')
    import httpx
    from colorama import Fore, Style, init
    from tqdm import tqdm

    sleep(3)

# Initialize colorama
init(autoreset=True)

config_file = json.load(open('config.json', 'r', encoding='utf-8'))
lock = threading.Lock()
success_count = 0
failed_count = 0
start_time = time.time()


# * Define Functions *#

def clear():
    system('cls' if platform.system() == 'Windows' else 'clear')


def display_header():
    print(f"{Fore.CYAN}{Style.BRIGHT}=== GitHub Profile Views Booster ===")
    print(f"{Fore.CYAN}Created by: {Fore.GREEN}github.com/bhaskarsaikia-17")
    print(f"{Fore.CYAN}Target: {Fore.GREEN}{config_file['counter_url'][:50]}...")
    print(f"{Fore.CYAN}Threads: {Fore.GREEN}{config_file['threads']}")
    print(f"{Fore.CYAN}Using Proxies: {Fore.GREEN}{config_file['use_proxy'].upper()}")
    print(f"{Fore.CYAN}{'=' * 35}")
    print()


def safe_print(*args):
    lock.acquire()
    for arg in args: print(arg, end=' ')
    print()
    lock.release()


def format_proxy(proxy):
    """Format proxy string to httpx compatible format.
    
    Supports formats:
    - ip:port
    - username:password@ip:port
    """
    if '@' in proxy:
        auth, ip_port = proxy.split('@')
        return f"http://{auth}@{ip_port}"
    else:
        return f"http://{proxy}"


def display_stats():
    global success_count, failed_count, start_time
    elapsed_time = time.time() - start_time
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    
    clear()
    display_header()
    
    print(f"{Fore.CYAN}--- Statistics ---")
    print(f"{Fore.GREEN}Successful Requests: {success_count}")
    print(f"{Fore.RED}Failed Requests: {failed_count}")
    print(f"{Fore.YELLOW}Running Time: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    
    if elapsed_time > 0:
        rps = success_count / elapsed_time
        print(f"{Fore.MAGENTA}Requests per second: {rps:.2f}")
    
    print(f"{Fore.CYAN}----------------")
    print()


def run():
    global success_count, failed_count
    
    while True:
        if use_proxy == 'y' or use_proxy == 'yes':
            proxies = open('proxies.txt', 'r', encoding='utf-8').read().splitlines()
            proxy = choice(proxies)

            proxy_url = format_proxy(proxy)
            proxy_dict = {
                "http://": proxy_url,
                "https://": proxy_url
            }

            try:
                url = counter_url
                global r
                r = httpx.get(url=url, proxies=proxy_dict, timeout=10)
            except httpx.ProxyError:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Bad proxy: {proxy}")
                continue
            except httpx.ConnectError:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Connect Error proxy: {proxy}")
                continue
            except httpx.RemoteProtocolError:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Remote Protocol Error, Retrying...")
                continue
            except httpx.ConnectTimeout:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Connect Timeout proxy: {proxy}")
                continue
            except httpx.ReadTimeout:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Read Timeout proxy: {proxy}")
                continue
            except ValueError:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Please change the 'counter_url' with a valid camo url in 'config.json'")
                break
            
            if r.status_code == 200:
                with lock:
                    success_count += 1
                    print(f"{Fore.GREEN}[+] Successful request! Total: {success_count}")
                    if success_count % 10 == 0:  # Update stats every 10 successful requests
                        display_stats()

            elif 'Bad Signature' in r.text:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Invalid Camo Link! Please change to a valid link.")
                    print(f"{Fore.YELLOW}Example Camo Link: https://camo.githubusercontent.com/4d29071feb1358f324bd018ad789e974f4c5963e91aa6bbc57dec9bb118a67c9/68747470733a2f2f6b6f6d617265762e636f6d2f67687076632f3f757365726e616d653d736561646879")
                break
            else:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Error request.")

        elif use_proxy == 'n' or use_proxy == 'no':
            try:
                url = counter_url
                global req
                req = httpx.get(url=url, timeout=10)

            except httpx.ConnectTimeout:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Timeout error.")
                continue

            if req.status_code == 200:
                with lock:
                    success_count += 1
                    print(f"{Fore.GREEN}[+] Successful request! Total: {success_count}")
                    if success_count % 10 == 0:  # Update stats every 10 successful requests
                        display_stats()

            elif 'Bad Signature' in req.text:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Invalid Camo Link! Please change to a valid link.")
                    print(f"{Fore.YELLOW}Example Camo Link: https://camo.githubusercontent.com/4d29071feb1358f324bd018ad789e974f4c5963e91aa6bbc57dec9bb118a67c9/68747470733a2f2f6b6f6d617265762e636f6d2f67687076632f3f757365726e616d653d736561646879")
                break
            else:
                with lock:
                    failed_count += 1
                    print(f"{Fore.RED}[-] Error request.")


# * Run Booster * #

clear()

if __name__ == "__main__":
    counter_url = config_file['counter_url']
    threads = config_file['threads']
    use_proxy = config_file['use_proxy']
    
    clear()
    display_header()
    
    print(f"{Fore.CYAN}[i] Starting {Fore.YELLOW}{threads} {Fore.CYAN}threads...")
    print(f"{Fore.CYAN}[i] Press {Fore.RED}CTRL+C {Fore.CYAN}to stop the booster")
    print()
    
    # Start threads with a simple progress indicator
    for i in range(1, threads + 1):
        t = threading.Thread(target=run)
        t.daemon = True
        t.start()
        
        # Simple progress indicator
        if i % 5 == 0 or i == threads:
            print(f"{Fore.CYAN}[+] Started {i}/{threads} threads", end="\r")
            sleep(0.01)
    
    print(f"\n{Fore.GREEN}[+] All threads started successfully!")
    print(f"{Fore.CYAN}[i] Boosting profile views...")
    
    try:
        while True:
            sleep(5)
            display_stats()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Stopping the booster...")
        print(f"{Fore.GREEN}[+] Successfully boosted {Fore.GREEN}{success_count} {Fore.WHITE}views!")
