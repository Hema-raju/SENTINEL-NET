import sys
from pathlib import Path


# Add the security_console folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECURITY_CONSOLE_PATH = PROJECT_ROOT / "security_console"

sys.path.insert(0, str(SECURITY_CONSOLE_PATH))


from alert_manager import (
    create_alert,
    get_alert_message,
    should_create_alert
)


def test_create_alert():

    alert = create_alert(
        agent_id="SENTINEL-AGENT-001",
        timestamp="2026-10-01 20:00:00",
        cpu_usage=50,
        memory_usage=65,
        anomaly_detected=True,
        anomaly_score=-0.25,
        risk_score=50,
        severity="Medium",
        reasons=[
            "Potentially anomalous system behavior detected."
        ]
    )

    assert isinstance(alert, dict)

    assert alert["agent_id"] == "SENTINEL-AGENT-001"
    assert alert["timestamp"] == "2026-10-01 20:00:00"
    assert alert["cpu_usage"] == 50.0
    assert alert["memory_usage"] == 65.0
    assert alert["anomaly_detected"] is True
    assert alert["anomaly_score"] == -0.25
    assert alert["risk_score"] == 50
    assert alert["severity"] == "Medium"

    assert isinstance(alert["reasons"], list)


def test_create_alert_without_timestamp():

    alert = create_alert(
        agent_id="SENTINEL-AGENT-001",
        timestamp=None,
        cpu_usage=30,
        memory_usage=40,
        anomaly_detected=False,
        anomaly_score=0.10,
        risk_score=0,
        severity="Normal",
        reasons=[
            "No significant indicators detected."
        ]
    )

    assert isinstance(alert, dict)

    assert alert["agent_id"] == "SENTINEL-AGENT-001"

    assert alert["timestamp"] is not None

    assert isinstance(
        alert["timestamp"],
        str
    )


def test_anomaly_alert_message():

    alert = create_alert(
        agent_id="SENTINEL-AGENT-001",
        timestamp="2026-10-01 20:00:00",
        cpu_usage=50,
        memory_usage=60,
        anomaly_detected=True,
        anomaly_score=-0.30,
        risk_score=50,
        severity="Medium",
        reasons=[
            "Machine-learning model detected potentially anomalous behavior."
        ]
    )

    message = get_alert_message(alert)

    assert isinstance(message, str)

    assert "anomalous" in message.lower()


def test_elevated_activity_message():

    alert = create_alert(
        agent_id="SENTINEL-AGENT-001",
        timestamp="2026-10-01 20:00:00",
        cpu_usage=80,
        memory_usage=40,
        anomaly_detected=False,
        anomaly_score=0.05,
        risk_score=15,
        severity="Low",
        reasons=[
            "High CPU utilization."
        ]
    )

    message = get_alert_message(alert)

    assert isinstance(message, str)

    assert "elevated" in message.lower()


def test_normal_activity_message():

    alert = create_alert(
        agent_id="SENTINEL-AGENT-001",
        timestamp="2026-10-01 20:00:00",
        cpu_usage=30,
        memory_usage=40,
        anomaly_detected=False,
        anomaly_score=0.10,
        risk_score=0,
        severity="Normal",
        reasons=[
            "No significant indicators detected."
        ]
    )

    message = get_alert_message(alert)

    assert isinstance(message, str)

    assert "no significant" in message.lower()


def test_anomaly_should_create_alert():

    alert = create_alert(
        agent_id="SENTINEL-AGENT-001",
        timestamp="2026-10-01 20:00:00",
        cpu_usage=50,
        memory_usage=60,
        anomaly_detected=True,
        anomaly_score=-0.30,
        risk_score=50,
        severity="Medium",
        reasons=[
            "Potentially anomalous behavior detected."
        ]
    )

    assert should_create_alert(alert) is True


def test_elevated_severity_should_create_alert():

    alert = create_alert(
        agent_id="SENTINEL-AGENT-001",
        timestamp="2026-10-01 20:00:00",
        cpu_usage=80,
        memory_usage=40,
        anomaly_detected=False,
        anomaly_score=0.05,
        risk_score=15,
        severity="Low",
        reasons=[
            "High CPU utilization."
        ]
    )

    assert should_create_alert(alert) is True


def test_normal_alert_should_not_be_created():

    alert = create_alert(
        agent_id="SENTINEL-AGENT-001",
        timestamp="2026-10-01 20:00:00",
        cpu_usage=30,
        memory_usage=40,
        anomaly_detected=False,
        anomaly_score=0.10,
        risk_score=0,
        severity="Normal",
        reasons=[
            "No significant indicators detected."
        ]
    )

    assert should_create_alert(alert) is False