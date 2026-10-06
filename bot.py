import random
import time
import requests
import os
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

TARGET_URL = "https://www.profitableratecpmnetwork.com/xij3bnky?key=799b506ccb29959c50a39b9ab41b3065"
MAX_VIEWS = 100000

# MIX OF DESKTOPS AND MOBILE PHONES
PROFILES = [
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", "vp": {"width": 1920, "height": 1080}},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15", "vp": {"width": 1680, "height": 1050}},
    {"ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "vp": {"width": 390, "height": 844}},
    {"ua": "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36", "vp": {"width": 412, "height": 915}},
    {"ua": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "vp": {"width": 820, "height": 1180}},
    {"ua": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36", "vp": {"width": 412, "height": 915}},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0", "vp": {"width": 1366, "height": 768}},
    {"ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1", "vp": {"width": 430, "height": 932}}
]

def get_proxies():
    try:
        res = requests.get('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=json', timeout=10)
        return [p['proxy'] for p in res.json()['proxies'] if p['protocol'] in ['http', 'https']]
    except:
        return []

def run_single_view(proxy, profile, view_number):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=profile['ua'], viewport=profile['vp'], proxy={"server": f"http://{proxy}"})
            page = context.new_page()
            page.goto(TARGET_URL, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000) # Wait 5 seconds
            page.mouse.wheel(0, random.randint(100, 800)) # Scroll randomly
            page.wait_for_timeout(1000)
            browser.close()
            print(f"SUCCESS: View {view_number} completed.")
            return 1
    except Exception as e:
        print(f"Proxy {proxy} failed. Skipping.")
        return 0

def main():
    # Read current count
    if os.path.exists("views.txt"):
        with open("views.txt", "r") as f:
            try: total_views = int(f.read().strip())
            except: total_views = 0
    else:
        total_views = 0

    print(f"Starting from {total_views} views...")

    while total_views < MAX_VIEWS:
        proxies = get_proxies()
        if len(proxies) < 10:
            time.sleep(10)
            continue

        # Shuffle profiles and pick random proxies
        shuffled = random.sample(PROFILES, len(PROFILES))
        used = set()
        
        tasks = []
        for i in range(5): # Run 5 at the same time (Bulk mode)
            profile = shuffled[i % len(shuffled)]
            proxy = random.choice(proxies)
            while proxy in used:
                proxy = random.choice(proxies)
            used.add(proxy)
            tasks.append((proxy, profile, total_views + i + 1))

        # Run 5 browsers in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda args: run_single_view(*args), tasks))
        
        total_views += sum(results)
        
        # Save progress
        with open("views.txt", "w") as f:
            f.write(str(total_views))
        
        print(f"Total Views So Far: {total_views}/{MAX_VIEWS}")

if __name__ == "__main__":
    main()
