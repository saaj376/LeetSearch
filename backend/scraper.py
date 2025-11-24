import os
import time
import random
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRFTOKEN = os.getenv("CSRFTOKEN")

if not LEETCODE_SESSION or not CSRFTOKEN:
    print("[WARN] Missing LEETCODE_SESSION or CSRFTOKEN in .env. Authenticated queries will fail.")

GRAPHQL_URL = "https://leetcode.com/graphql"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/124.0.0.0"
]

DEFAULT_TIMEOUT = 20
# polite delays
PAGE_DELAY_MIN = 0.3
PAGE_DELAY_MAX = 0.9
PROFILE_DELAY_MIN = 0.5
PROFILE_DELAY_MAX = 1.1

def _auth_headers() -> Dict[str, str]:
    """Return headers including auth cookies and CSRF."""
    return {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://leetcode.com",
        "Origin": "https://leetcode.com",
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRFTOKEN};",
        "X-CSRFToken": CSRFTOKEN,
    }


def _post_graphql(query: str, variables: dict = None, retries: int = 3) -> Optional[dict]:
    """POST GraphQL with auth headers, retry on intermittent failures."""
    payload = {"query": query, "variables": variables or {}}
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(GRAPHQL_URL, json=payload, headers=_auth_headers(), timeout=DEFAULT_TIMEOUT)
        except requests.RequestException as e:
            wait = random.uniform(1.0, 3.0)
            print(f"[ERROR] RequestException: {e} — retrying in {wait:.1f}s (attempt {attempt}/{retries})")
            time.sleep(wait)
            continue

        if resp.status_code == 200:
            try:
                return resp.json()
            except ValueError:
                print("[ERROR] Response not JSON")
                return None

        # handle rate limit / cloudflare-ish statuses gracefully
        if resp.status_code in (403, 429, 520, 521):
            wait = random.uniform(2.0, 6.0)
            print(f"[WARN] Status {resp.status_code}; retrying after {wait:.1f}s (attempt {attempt}/{retries})")
            time.sleep(wait)
            continue

        # for other errors, show snippet and abort
        print(f"[ERROR] GraphQL status {resp.status_code}")
        print(resp.text[:400])
        return None

    print("[ERROR] GraphQL failed after retries")
    return None


def scrape_contest_usernames(pages: int = 3) -> List[str]:
    query = """
    query globalRanking($page: Int!) {
      globalRanking(page: $page) {
        rankingNodes {
          user {
            username
          }
        }
      }
    }
    """

    usernames = set()
    for page in range(1, pages + 1):
        print(f"[SCRAPER] Fetching contest ranking page {page}")
        data = _post_graphql(query, {"page": page})
        if not data or "data" not in data:
            print("[WARN] No data returned for ranking page", page)
            break

        ranking = data["data"].get("globalRanking", {})
        nodes = ranking.get("rankingNodes", [])
        if not nodes:
            print("[WARN] No ranking nodes on page", page)
            break

        for node in nodes:
            user = node.get("user", {})
            uname = user.get("username")
            if uname:
                usernames.add(uname)

        time.sleep(random.uniform(PAGE_DELAY_MIN, PAGE_DELAY_MAX))

    return sorted(usernames)

def fetch_user_profile(username: str) -> Optional[dict]:
    """
    Fetch user's profile details using matchedUser query.
    Note: schema differs across accounts; the following fields are conservative
    and compatible with the common schemas observed.
    """
    query = """
    query userProfile($username: String!) {
      matchedUser(username: $username) {
        username
        profile {
          realName
          aboutMe
          countryName
          ranking
          school
          company
          websites
        }
      }
    }
    """

    data = _post_graphql(query, {"username": username})
    if not data or "data" not in data:
        print(f"[ERROR] No response for profile {username}")
        return None

    matched = data["data"].get("matchedUser")
    if not matched:
        # matchedUser may be null for deleted/private accounts
        return None

    profile = matched.get("profile", {})
    # attach username at top-level for convenience
    profile_out = {"username": matched.get("username")}
    profile_out.update(profile or {})
    return profile_out


def scrape_contest_with_profiles(pages: int = 2) -> Dict[str, dict]:
    """
    Scrape contest usernames and fetch profiles for each username.
    Returns dict: username -> profile dict (profile may be None if fetch failed)
    """
    result = {}
    users = scrape_contest_usernames(pages=pages)
    print(f"[SCRAPER] Total usernames scraped: {len(users)}")

    for i, u in enumerate(users):
        print(f"[SCRAPER] ({i+1}/{len(users)}) Fetching profile for: {u}")
        profile = fetch_user_profile(u)
        result[u] = profile
        time.sleep(random.uniform(PROFILE_DELAY_MIN, PROFILE_DELAY_MAX))

    return result

