from datetime import datetime


def create_alert(
    agent_id,
    timestamp,
    cpu_usage,
    memory_usage,
    anomaly_detected,
    anomaly_score,
    risk_score,
    severity,
    reasons
):
    """
    Create a structured SentinelNet alert.

    Args:
        agent_id: Monitoring agent identifier.
        timestamp: Monitoring timestamp.
        cpu_usage: CPU usage percentage.
        memory_usage: Memory usage percentage.
        anomaly_detected: ML anomaly status.
        anomaly_score: ML anomaly score.
        risk_score: Calculated risk score.
        severity: Risk severity.
        reasons: List of reasons for the assessment.

    Returns:
        dict: Structured alert.
    """

    if timestamp is None:

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    alert = {
        "agent_id": agent_id,
        "timestamp": timestamp,
        "cpu_usage": float(cpu_usage),
        "memory_usage": float(memory_usage),
        "anomaly_detected": bool(anomaly_detected),
        "anomaly_score": float(anomaly_score),
        "risk_score": int(risk_score),
        "severity": severity,
        "reasons": reasons
    }

    return alert


def get_alert_message(alert):
    """
    Generate a human-readable alert message.
    """

    if alert["anomaly_detected"]:

        return (
            "Potentially anomalous system behavior "
            "detected by the machine-learning model."
        )

    if alert["severity"] != "Normal":

        return (
            "Elevated system activity detected. "
            "Further monitoring is recommended."
        )

    return (
        "No significant anomalous indicators detected."
    )


def should_create_alert(alert):
    """
    Determine whether an alert should be displayed
    as a security alert.

    Normal observations are not treated as alerts.
    """

    return (
        alert["severity"] != "Normal"
        or alert["anomaly_detected"]
    )


if __name__ == "__main__":

    print("=" * 70)
    print("SENTINELNET ALERT MANAGER TEST")
    print("=" * 70)

    test_alert = create_alert(
        agent_id="SENTINEL-AGENT-001",
        timestamp="2026-09-26 08:30:00",
        cpu_usage=92.5,
        memory_usage=91.2,
        anomaly_detected=True,
        anomaly_score=-0.32,
        risk_score=100,
        severity="Critical",
        reasons=[
            "Very high CPU utilization.",
            "Very high memory utilization.",
            "Machine-learning model detected "
            "potentially anomalous behavior."
        ]
    )

    print()

    print("ALERT CREATED")
    print("-" * 70)

    print(
        f"Agent ID       : "
        f"{test_alert['agent_id']}"
    )

    print(
        f"Timestamp      : "
        f"{test_alert['timestamp']}"
    )

    print(
        f"CPU Usage      : "
        f"{test_alert['cpu_usage']}%"
    )

    print(
        f"Memory Usage   : "
        f"{test_alert['memory_usage']}%"
    )

    print(
        f"ML Anomaly     : "
        f"{test_alert['anomaly_detected']}"
    )

    print(
        f"Anomaly Score  : "
        f"{test_alert['anomaly_score']}"
    )

    print(
        f"Risk Score     : "
        f"{test_alert['risk_score']}/100"
    )

    print(
        f"Severity       : "
        f"{test_alert['severity']}"
    )

    print()

    print("Alert Message:")
    print(
        get_alert_message(test_alert)
    )

    print()

    print("Reasons:")

    for reason in test_alert["reasons"]:

        print(
            f"  - {reason}"
        )

    print()

    print(
        f"Should Create Alert: "
        f"{should_create_alert(test_alert)}"
    )

    print()

    print("=" * 70)
    print("Alert manager test completed.")
    print("=" * 70)