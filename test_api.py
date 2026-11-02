import sys
from pathlib import Path


# Add the security_console folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECURITY_CONSOLE_PATH = PROJECT_ROOT / "security_console"

sys.path.insert(0, str(SECURITY_CONSOLE_PATH))


from app import app


def test_dashboard_page():

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_history_page():

    client = app.test_client()

    response = client.get("/history")

    assert response.status_code == 200


def test_processes_page():

    client = app.test_client()

    response = client.get("/processes")

    assert response.status_code == 200


def test_network_page():

    client = app.test_client()

    response = client.get("/network")

    assert response.status_code == 200


def test_reports_page():

    client = app.test_client()

    response = client.get("/reports")

    assert response.status_code == 200


def test_status_api():

    client = app.test_client()

    response = client.get("/api/status")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, dict)


def test_processes_api():

    client = app.test_client()

    response = client.get("/api/processes")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, dict)

    assert "success" in data


def test_network_api():

    client = app.test_client()

    response = client.get("/api/network")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, dict)

    assert "success" in data


def test_network_analysis_api():

    client = app.test_client()

    response = client.get("/api/network/analysis")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, dict)

    assert "success" in data


def test_network_risk_api():

    client = app.test_client()

    response = client.get("/api/network/risk")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, dict)

    assert "success" in data