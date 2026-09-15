from fastapi.testclient import TestClient

from article.api.main import app

client = TestClient(app)

SAMPLE_RUN = {
    "project_name": "demo-project",
    "charter_name": "The Article Charter",
    "charter_version": "1.0.0",
    "score": 90.0,
    "passed": 9,
    "failed": 1,
    "skipped": 0,
    "results": [
        {"id": "transparency", "title": "Transparency", "status": "pass", "message": "ok", "weight": 1},
    ],
}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_dashboard_serves_html():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "<html lang=\"en\">" in resp.text


def test_create_and_fetch_run():
    created = client.post("/runs", json=SAMPLE_RUN)
    assert created.status_code == 201
    body = created.json()
    assert body["project_name"] == "demo-project"
    assert body["score"] == 90.0

    fetched = client.get(f"/runs/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]


def test_list_runs_filters_by_project():
    client.post("/runs", json={**SAMPLE_RUN, "project_name": "alpha"})
    client.post("/runs", json={**SAMPLE_RUN, "project_name": "beta"})

    resp = client.get("/runs", params={"project_name": "alpha"})
    assert resp.status_code == 200
    assert all(r["project_name"] == "alpha" for r in resp.json())


def test_get_missing_run_returns_404():
    resp = client.get("/runs/999999")
    assert resp.status_code == 404


def test_create_run_rejects_missing_fields():
    resp = client.post("/runs", json={"project_name": "incomplete"})
    assert resp.status_code == 422
