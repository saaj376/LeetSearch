import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    """Create a throwaway users.json for the tests."""
    data = {
        "alice": {
            "username": "alice",
            "realName": "Alice Example",
            "school": "University of Waterloo",
            "countryName": "Canada",
            "ranking": 1234,
            "aboutMe": "",
            "company": None,
            "websites": [],
        },
        "bob": {
            "username": "bob",
            "realName": "Bob Example",
            "school": "Massachusetts Institute of Technology",
            "countryName": "United States",
            "ranking": 5678,
            "aboutMe": "",
            "company": None,
            "websites": [],
        },
        "carol": {
            "username": "carol",
            "realName": "Carol Example",
            "school": None,
            "countryName": "United States",
            "ranking": 9999,
            "aboutMe": "",
            "company": None,
            "websites": [],
        },
    }

    db_path = tmp_path / "users.json"
    db_path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(main, "DB_PATH", db_path)
    return data


@pytest.fixture()
def client(temp_db):
    return TestClient(main.app)


def test_health_returns_cache_details(client, temp_db):
    resp = client.get("/health")
    body = resp.json()

    assert resp.status_code == 200
    assert body["status"] == "ok"
    assert body["profiles_cached"] == len(temp_db)
    assert body["last_updated"] is not None


def test_search_college_filters_matches(client):
    resp = client.get("/search/college", params={"query": "waterloo"})
    body = resp.json()

    assert resp.status_code == 200
    assert body["total"] == 1
    assert body["results"][0]["username"] == "alice"


def test_get_profile_returns_cached_entry(monkeypatch, client):
    def fail_fetch(username):
        raise AssertionError("fetch_user_profile should not run for cached calls.")

    monkeypatch.setattr(main, "fetch_user_profile", fail_fetch)

    resp = client.get("/profiles/alice")
    body = resp.json()

    assert resp.status_code == 200
    assert body["cached"] is True
    assert body["profile"]["username"] == "alice"


def test_get_profile_refreshes_from_network(monkeypatch, client, tmp_path):
    fresh_profile = {
        "username": "alice",
        "realName": "Alice Example",
        "school": "University of Waterloo",
        "countryName": "Canada",
        "ranking": 42,
        "aboutMe": "Updated",
        "company": None,
        "websites": [],
    }

    monkeypatch.setattr(main, "fetch_user_profile", lambda username: fresh_profile)

    resp = client.get("/profiles/alice", params={"refresh": "true"})
    body = resp.json()

    assert resp.status_code == 200
    assert body["cached"] is False
    assert body["profile"]["ranking"] == 42


def test_refresh_endpoint_dispatches_background(monkeypatch, client):
    called = {}

    def fake_refresh(pages, max_users):
        called["args"] = (pages, max_users)

    monkeypatch.setattr(main, "run_refresh_cycle", fake_refresh)

    resp = client.post("/refresh", json={"pages": 1, "max_users": 3})
    body = resp.json()

    assert resp.status_code == 200
    assert body["started"] is True
    assert called["args"] == (1, 3)

