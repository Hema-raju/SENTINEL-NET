import sys
from pathlib import Path


# Add the security_console folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECURITY_CONSOLE_PATH = PROJECT_ROOT / "security_console"

sys.path.insert(0, str(SECURITY_CONSOLE_PATH))


from risk_engine import calculate_risk


def test_normal_system_risk():

    result = calculate_risk(
        cpu_usage=30,
        memory_usage=40,
        anomaly_detected=False,
        anomaly_score=0.10
    )

    assert result["risk_score"] == 0
    assert result["severity"] == "Normal"
    assert len(result["reasons"]) > 0


def test_elevated_cpu_risk():

    result = calculate_risk(
        cpu_usage=65,
        memory_usage=40,
        anomaly_detected=False,
        anomaly_score=0.10
    )

    assert result["risk_score"] == 5
    assert result["severity"] == "Normal"


def test_high_cpu_risk():

    result = calculate_risk(
        cpu_usage=80,
        memory_usage=40,
        anomaly_detected=False,
        anomaly_score=0.10
    )

    assert result["risk_score"] == 15
    assert result["severity"] == "Low"


def test_high_memory_risk():

    result = calculate_risk(
        cpu_usage=40,
        memory_usage=80,
        anomaly_detected=False,
        anomaly_score=0.10
    )

    assert result["risk_score"] == 15
    assert result["severity"] == "Low"


def test_anomaly_risk():

    result = calculate_risk(
        cpu_usage=40,
        memory_usage=40,
        anomaly_detected=True,
        anomaly_score=-0.10
    )

    assert result["risk_score"] == 40
    assert result["severity"] == "Medium"


def test_strong_anomaly_risk():

    result = calculate_risk(
        cpu_usage=40,
        memory_usage=40,
        anomaly_detected=True,
        anomaly_score=-0.30
    )

    assert result["risk_score"] == 50
    assert result["severity"] == "Medium"


def test_critical_risk():

    result = calculate_risk(
        cpu_usage=95,
        memory_usage=95,
        anomaly_detected=True,
        anomaly_score=-0.30
    )

    assert result["risk_score"] == 100
    assert result["severity"] == "Critical"


def test_risk_score_never_exceeds_100():

    result = calculate_risk(
        cpu_usage=100,
        memory_usage=100,
        anomaly_detected=True,
        anomaly_score=-1.0
    )

    assert result["risk_score"] <= 100


def test_risk_result_structure():

    result = calculate_risk(
        cpu_usage=50,
        memory_usage=50,
        anomaly_detected=False,
        anomaly_score=0.05
    )

    assert isinstance(result, dict)

    assert "risk_score" in result
    assert "severity" in result
    assert "reasons" in result

    assert isinstance(result["risk_score"], int)
    assert isinstance(result["severity"], str)
    assert isinstance(result["reasons"], list)