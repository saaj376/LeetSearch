import json

DB_FILE = "users.json"

def load_database():
    """Load users.json safely."""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        print("[ERROR] Could not load users.json")
        return {}

def search_by_college(college_name: str):
    """Return all users whose profile school contains the keyword."""
    db = load_database()
    college_name = college_name.lower()

    results = []

    for username, profile in db.items():
        if not profile:
            continue

        school = profile.get("school")
        if not school:
            continue

        if college_name in school.lower():
            results.append({
                "username": username,
                "realName": profile.get("realName"),
                "school": school,
                "ranking": profile.get("ranking"),
                "country": profile.get("countryName")
            })

    return results

