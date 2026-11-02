import sys
from pathlib import Path


# Add the security_console folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECURITY_CONSOLE_PATH = PROJECT_ROOT / "security_console"

sys.path.insert(0, str(SECURITY_CONSOLE_PATH))


from anomaly_detector import detect_anomalies


def test_anomaly_detection_insufficient_data():

    cpu_values = [10, 20, 30]
    memory_values = [40, 50, 60]

    result = detect_anomalies(
        cpu_values,
        memory_values
    )

    assert result["status"] == "insufficient_data"
    assert "At least" in result["message"]
    assert result["results"] == []


def test_anomaly_detection_mismatched_data():

    cpu_values = [10, 20, 30]
    memory_values = [40, 50]

    try:
        detect_anomalies(
            cpu_values,
            memory_values
        )

        assert False, "ValueError was not raised."

    except ValueError as error:

        assert str(error) == (
            "CPU and memory data must have the same length."
        )


def test_anomaly_detection_success():

    cpu_values = [
        10, 12, 11, 13, 15,
        14, 12, 11, 13, 14,
        90
    ]

    memory_values = [
        30, 32, 31, 33, 35,
        34, 32, 31, 33, 34,
        95
    ]

    result = detect_anomalies(
        cpu_values,
        memory_values
    )

    assert result["status"] == "success"

    assert result["message"] == (
        "Anomaly detection completed."
    )

    assert len(result["results"]) == len(cpu_values)


def test_anomaly_result_structure():

    cpu_values = [
        20, 21, 22, 23, 24,
        25, 26, 27, 28, 29
    ]

    memory_values = [
        40, 41, 42, 43, 44,
        45, 46, 47, 48, 49
    ]

    result = detect_anomalies(
        cpu_values,
        memory_values
    )

    assert result["status"] == "success"

    for item in result["results"]:

        assert "cpu" in item
        assert "memory" in item
        assert "anomaly" in item
        assert "score" in item

        assert isinstance(item["cpu"], float)
        assert isinstance(item["memory"], float)
        assert isinstance(item["anomaly"], bool)
        assert isinstance(item["score"], float)


def test_anomaly_detection_is_deterministic():

    cpu_values = [
        10, 12, 11, 13, 15,
        14, 12, 11, 13, 14,
        90
    ]

    memory_values = [
        30, 32, 31, 33, 35,
        34, 32, 31, 33, 34,
        95
    ]

    first_result = detect_anomalies(
        cpu_values,
        memory_values
    )

    second_result = detect_anomalies(
        cpu_values,
        memory_values
    )

    assert first_result == second_result