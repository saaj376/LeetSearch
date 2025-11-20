import requests
import random
import time
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
]

graphql_url = "https://leetcode.com/graphql"

def graphql_query(query:str, variables:dict=None,retries: int=3):
    for attempt in range(1, retries + 1):
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": random.choice(user_agents),
            "Origin": "https://leetcode.com",
            "Referer": "https://leetcode.com",
        }

        try:
            response = requests.post(
                graphql_url,
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=15,
            )

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    print("[ERROR] Response is not valid JSON")
                    return None

            if response.status_code in (403, 429, 520, 521):
                wait = random.uniform(2, 5)
                print(
                    f"[WARN] Cloudflare / rate-limit (status {response.status_code}). Retrying in {wait:.1f}s... (attempt {attempt}/{retries})"
                )
                time.sleep(wait)
                continue

            print(f"[ERROR] GraphQL query failed with status {response.status_code}")
            return None

        except requests.exceptions.RequestException as e:
            wait = random.uniform(1, 3)
            print(f"[ERROR] Exception: {e} — retrying in {wait:.1f}s... (attempt {attempt}/{retries})")
            time.sleep(wait)
            continue

    print("[ERROR] GraphQL query failed after all retries")
    return None

def scrape_contest_username(pages=3):
    usernames=set()
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
    for page in range(1,pages+1):
        time.sleep(random.uniform(0.4,1.0))
        data=graphql_query(query,{"page":page})
        if not data or "data" not in data:
            break

        for sub in data["data"]["recentSubmissionList"]["submissions"]:
            if sub["username"]:
                usernames.add(sub["username"])

    return list(usernames)