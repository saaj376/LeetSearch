import json
import time
import random
import os
from scraper import scrape_contest_usernames, fetch_user_profile

DB_FILE = "users.json"
MAX_USERS = 35   # limit profile fetch count


def load_database():
    """Load local JSON DB or return empty dict."""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("[WARN] users.json corrupted — recreating.")
        return {}


def save_database(db):
    """Write updated DB to file."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"[DB] Saved {len(db)} profiles to users.json")


def update_profiles(pages=2):
    """Scrape usernames → fetch their profiles → store locally."""
    print("\n=== RUNNING UPDATER ===\n")

    db = load_database()

    # Step 1 — scrape contest usernames
    print("[UPDATER] Scraping contest usernames...")
    usernames = scrape_contest_usernames(pages=pages)
    print(f"[UPDATER] Total usernames scraped: {len(usernames)}")

    # Step 2 — limit profile fetch to MAX_USERS
    usernames_to_process = usernames[:MAX_USERS]
    print(f"[UPDATER] Processing only first {MAX_USERS} users...\n")

    for idx, username in enumerate(usernames_to_process, start=1):
        print(f"[{idx}/{MAX_USERS}] Fetching profile for: {username}")

        profile = fetch_user_profile(username)

        if profile:
            db[username] = profile
        else:
            print(f"[WARN] No profile returned for: {username}")

        # polite delay
        time.sleep(random.uniform(0.7, 1.5))

    # Step 3 — save to json db
    save_database(db)

    print("\n=== UPDATE COMPLETE ===\n")


if __name__ == "__main__":
    update_profiles(pages=2)
