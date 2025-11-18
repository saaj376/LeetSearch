import requests
import bs4
from datetime import datetime
import time
import random

graphqlurl="https://leetcode.com/graphql"

user_agents=[
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)",
]

def safe_headers():
    return {"User agent:",random.choice(user_agents)}

def safe_graphql(query,variables):
    time.sleep(random.uniform(0.7,1.4))
    res=requests.post(
        graphqlurl,
        json={"query":query,"variables":variables},
        headers={"Content-Type": "application/json", **safe_headers()}
    )
    if res.status_code == 429:
        print("[RATE LIMIT] Waiting 60 seconds…")
        time.sleep(60)
        return safe_graphql(query, variables)
    return res.json()