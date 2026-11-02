def calculate_risk(
    cpu_usage,
    memory_usage,
    anomaly_detected,
    anomaly_score
):
    """
    Calculate a SentinelNet risk assessment.

    This is an initial rule-based risk engine.
    A high CPU or memory value by itself does not
    prove malicious activity.

    Args:
        cpu_usage: Current CPU percentage.
        memory_usage: Current memory percentage.
        anomaly_detected: Boolean from ML detector.
        anomaly_score: Isolation Forest score.

    Returns:
        dict: Risk score and severity information.
    """

    risk_score = 0

    reasons = []

    # -------------------------------------------------
    # CPU indicator
    # -------------------------------------------------

    if cpu_usage >= 90:

        risk_score += 25

        reasons.append(
            "Very high CPU utilization."
        )

    elif cpu_usage >= 75:

        risk_score += 15

        reasons.append(
            "High CPU utilization."
        )

    elif cpu_usage >= 60:

        risk_score += 5

        reasons.append(
            "Elevated CPU utilization."
        )

    # -------------------------------------------------
    # Memory indicator
    # -------------------------------------------------

    if memory_usage >= 90:

        risk_score += 25

        reasons.append(
            "Very high memory utilization."
        )

    elif memory_usage >= 75:

        risk_score += 15

        reasons.append(
            "High memory utilization."
        )

    elif memory_usage >= 60:

        risk_score += 5

        reasons.append(
            "Elevated memory utilization."
        )

    # -------------------------------------------------
    # ML anomaly indicator
    # -------------------------------------------------

    if anomaly_detected:

        risk_score += 40

        reasons.append(
            "Machine-learning model detected "
            "potentially anomalous behavior."
        )

    # -------------------------------------------------
    # Additional ML score indicator
    # -------------------------------------------------

    if anomaly_score < -0.20:

        risk_score += 10

        reasons.append(
            "ML anomaly score indicates stronger "
            "deviation from the learned baseline."
        )

    # -------------------------------------------------
    # Limit risk score
    # -------------------------------------------------

    risk_score = min(
        risk_score,
        100
    )

    # -------------------------------------------------
    # Determine severity
    # -------------------------------------------------

    if risk_score >= 80:

        severity = "Critical"

    elif risk_score >= 60:

        severity = "High"

    elif risk_score >= 35:

        severity = "Medium"

    elif risk_score >= 15:

        severity = "Low"

    else:

        severity = "Normal"

    # -------------------------------------------------
    # Normal case
    # -------------------------------------------------

    if not reasons:

        reasons.append(
            "No significant indicators detected."
        )

    return {
        "risk_score": risk_score,
        "severity": severity,
        "reasons": reasons
    }


if __name__ == "__main__":

    print("=" * 70)
    print("SENTINELNET RISK ENGINE TEST")
    print("=" * 70)

    test_cases = [

        {
            "name": "Normal System",
            "cpu": 25,
            "memory": 45,
            "anomaly": False,
            "score": 0.10
        },

        {
            "name": "Elevated Resource Usage",
            "cpu": 65,
            "memory": 70,
            "anomaly": False,
            "score": 0.05
        },

        {
            "name": "Potential Anomaly",
            "cpu": 80,
            "memory": 82,
            "anomaly": True,
            "score": -0.10
        },

        {
            "name": "High Risk Example",
            "cpu": 95,
            "memory": 94,
            "anomaly": True,
            "score": -0.35
        }
    ]

    for test in test_cases:

        result = calculate_risk(
            cpu_usage=test["cpu"],
            memory_usage=test["memory"],
            anomaly_detected=test["anomaly"],
            anomaly_score=test["score"]
        )

        print()

        print(
            f"Test: {test['name']}"
        )

        print(
            f"CPU: {test['cpu']}%"
        )

        print(
            f"Memory: {test['memory']}%"
        )

        print(
            f"ML Anomaly: {test['anomaly']}"
        )

        print(
            f"ML Score: {test['score']}"
        )

        print(
            f"Risk Score: "
            f"{result['risk_score']}/100"
        )

        print(
            f"Severity: "
            f"{result['severity']}"
        )

        print("Reasons:")

        for reason in result["reasons"]:

            print(
                f"  - {reason}"
            )

    print()

    print("=" * 70)
    print("Risk engine test completed.")
    print("=" * 70)