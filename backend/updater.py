import time
import random
from scraper import scrape_contest_username

contest_interval=15*60
min_jitter=-20
max_jitter=30

def jitter(base_seconds):
    return base_seconds + random.randint(min_jitter,max_jitter)

def contest_updater():
    lastrun=0
    while True:
        now=time.time()
        if now-lastrun >= jitter(contest_interval):
            try:
                usernames=scrape_contest_username(pages=3)
            except Exception as e:
                print("Contest Scraper Failed: ",e)
            lastrun=now
            time.sleep(random.uniform(1,2))
        time.sleep(5)

if __name__ == "__main__":
    contest_updater()