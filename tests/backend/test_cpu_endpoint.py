from fastapi.testclient import TestClient
from main import app

def test_post_cpu_metrics():
    payload={
        "machine_id":"123e4567-e89b-12d3-a456-426614174000",
        "load_avg_perc": 25.0,
        "load_max_perc": 80.0,
        "temp_avg": None,
        "temp_max": None,
    }
    with TestClient(app) as client:
        response=client.post(
            "/metrics/cpu",
            json=payload,
        )
    assert response.status_code==201, response.text
    assert response.json()=="received but posting to db not ready yet"
