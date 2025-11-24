import json
import time
import random
import os
from datetime import datetime
from scraper import scrape_contest_usernames, fetch_user_profile

DB_FILE = "users.json"
MAX_USERS = 35              
PAGES_PER_CYCLE = 2          
CRON_INTERVAL_MINUTES = 30   

def load_database():
    """Load local JSON DB, or return empty dict."""
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("[WARN] users.json corrupted — recreating new file.")
        return {}


def save_database(db):
    """Safely write updated DB to JSON."""
    temp = DB_FILE + ".tmp"

    try:
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)

        os.replace(temp, DB_FILE)
        print(f"[DB] Saved {len(db)} profiles → {DB_FILE}")

    except Exception as e:
        print("[ERROR] Failed to save DB:", e)
        if os.path.exists(temp):
            os.remove(temp)



def update_profiles():
    print("\n====================================")
    print("        🔵 RUNNING SCRAPER CYCLE")
    print("====================================")
    print(f"[INFO] Started at {datetime.now()}")

    db = load_database()

    # Step 1 → scrape contest usernames (first 2 pages)
    print("[UPDATER] Scraping contest usernames...")
    usernames = scrape_contest_usernames(pages=PAGES_PER_CYCLE)
    print(f"[UPDATER] Total scraped from contest pages: {len(usernames)}")

    # Step 2 → limit how many we process in each cycle
    usernames_to_fetch = usernames[:MAX_USERS]
    print(f"[UPDATER] Fetching profiles for first {MAX_USERS} users...\n")

    # Step 3 → fetch profile for each username
    for idx, username in enumerate(usernames_to_fetch, start=1):
        print(f"[{idx}/{MAX_USERS}] Fetching profile for: {username}")

        profile = fetch_user_profile(username)

        if profile:
            db[username] = profile        # update or insert
        else:
            print(f"[WARN] No profile returned for: {username}")

        time.sleep(random.uniform(0.7, 1.5))   # polite delay

    # Step 4 → Save updated DB
    save_database(db)

    print(f"[INFO] Cycle completed at {datetime.now()}")
    print("====================================\n")


