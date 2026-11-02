import numpy as np

from sklearn.ensemble import IsolationForest

from database import get_connection


MINIMUM_DATA_POINTS = 10


def detect_anomalies(cpu_values, memory_values):
    """
    Detect potentially anomalous system behavior using
    CPU and memory history.

    Args:
        cpu_values: List of CPU usage percentages.
        memory_values: List of memory usage percentages.

    Returns:
        dict: Anomaly detection results.
    """

    if len(cpu_values) != len(memory_values):
        raise ValueError(
            "CPU and memory data must have the same length."
        )

    if len(cpu_values) < MINIMUM_DATA_POINTS:
        return {
            "status": "insufficient_data",
            "message": (
                f"At least {MINIMUM_DATA_POINTS} "
                "data points are required."
            ),
            "results": []
        }

    data = np.column_stack(
        (
            cpu_values,
            memory_values
        )
    )

    model = IsolationForest(
        contamination="auto",
        random_state=42
    )

    predictions = model.fit_predict(data)

    anomaly_scores = model.decision_function(data)

    results = []

    for index in range(len(data)):

        is_anomaly = predictions[index] == -1

        results.append(
            {
                "cpu": float(data[index][0]),
                "memory": float(data[index][1]),
                "anomaly": bool(is_anomaly),
                "score": float(anomaly_scores[index])
            }
        )

    return {
        "status": "success",
        "message": "Anomaly detection completed.",
        "results": results
    }


def get_system_metrics_from_database(limit=500):
    """
    Retrieve recent CPU and memory measurements
    from the SQLite database.

    Args:
        limit: Maximum number of records to retrieve.

    Returns:
        tuple: CPU values, memory values, and database rows.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                agent_id,
                timestamp,
                cpu_usage,
                memory_usage
            FROM system_metrics
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        rows = list(reversed(rows))

        cpu_values = [
            float(row["cpu_usage"])
            for row in rows
        ]

        memory_values = [
            float(row["memory_usage"])
            for row in rows
        ]

        return cpu_values, memory_values, rows

    finally:

        connection.close()


def analyze_database_metrics(limit=500):
    """
    Run anomaly detection against real monitoring
    data stored in the SQLite database.

    Args:
        limit: Number of recent records to analyze.

    Returns:
        dict: Database anomaly analysis result.
    """

    cpu_values, memory_values, rows = (
        get_system_metrics_from_database(limit)
    )

    detection = detect_anomalies(
        cpu_values,
        memory_values
    )

    if detection["status"] != "success":
        return detection

    if not detection["results"]:
        return detection

    latest_result = detection["results"][-1]

    latest_row = rows[-1]

    return {
        "status": "success",
        "message": "Real database anomaly analysis completed.",
        "records_analyzed": len(rows),
        "latest": {
            "id": latest_row["id"],
            "agent_id": latest_row["agent_id"],
            "timestamp": latest_row["timestamp"],
            "cpu": latest_result["cpu"],
            "memory": latest_result["memory"],
            "anomaly": latest_result["anomaly"],
            "score": latest_result["score"]
        },
        "results": detection["results"]
    }


if __name__ == "__main__":

    print("=" * 70)
    print("SENTINELNET REAL DATABASE ANOMALY TEST")
    print("=" * 70)

    result = analyze_database_metrics(
        limit=500
    )

    print()

    print(
        f"Analysis status: "
        f"{result['status']}"
    )

    print()

    if result["status"] == "success":

        print(
            f"Records analyzed: "
            f"{result['records_analyzed']}"
        )

        print()

        latest = result["latest"]

        print("LATEST MONITORING RESULT")
        print("-" * 70)

        print(
            f"Timestamp : {latest['timestamp']}"
        )

        print(
            f"Agent ID  : {latest['agent_id']}"
        )

        print(
            f"CPU       : {latest['cpu']:.2f}%"
        )

        print(
            f"Memory    : {latest['memory']:.2f}%"
        )

        print(
            f"Anomaly   : {latest['anomaly']}"
        )

        print(
            f"Score     : {latest['score']:.4f}"
        )

    else:

        print(
            f"Message: {result['message']}"
        )

    print()

    print("=" * 70)
    print("Real database anomaly test completed.")
    print("=" * 70)