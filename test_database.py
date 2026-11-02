import sys
from pathlib import Path


# Add the security_console folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECURITY_CONSOLE_PATH = PROJECT_ROOT / "security_console"

sys.path.insert(0, str(SECURITY_CONSOLE_PATH))


from database import (
    get_database_path,
    get_connection,
    initialize_database
)


def test_database_path():

    database_path = get_database_path()

    assert isinstance(database_path, str)

    assert database_path.endswith(
        "sentinelnet.db"
    )


def test_database_connection():

    initialize_database()

    connection = get_connection()

    assert connection is not None

    connection.close()


def test_required_tables():

    initialize_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        )

        tables = {
            row["name"]
            for row in cursor.fetchall()
        }

        required_tables = {
            "agents",
            "system_metrics",
            "process_snapshots",
            "network_snapshots",
            "alerts"
        }

        assert required_tables.issubset(tables)

    finally:

        connection.close()


def test_system_metrics_table():

    initialize_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "PRAGMA table_info(system_metrics)"
        )

        columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        required_columns = {
            "id",
            "agent_id",
            "timestamp",
            "cpu_usage",
            "memory_usage",
            "memory_total",
            "memory_available",
            "memory_used"
        }

        assert required_columns.issubset(columns)

    finally:

        connection.close()


def test_process_snapshots_table():

    initialize_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "PRAGMA table_info(process_snapshots)"
        )

        columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        required_columns = {
            "id",
            "agent_id",
            "timestamp",
            "pid",
            "process_name",
            "status",
            "cpu_percent",
            "memory_percent",
            "username"
        }

        assert required_columns.issubset(columns)

    finally:

        connection.close()


def test_network_snapshots_table():

    initialize_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "PRAGMA table_info(network_snapshots)"
        )

        columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        required_columns = {
            "id",
            "agent_id",
            "timestamp",
            "pid",
            "process_name",
            "protocol",
            "local_ip",
            "local_port",
            "remote_ip",
            "remote_port",
            "status"
        }

        assert required_columns.issubset(columns)

    finally:

        connection.close()


def test_alerts_table():

    initialize_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "PRAGMA table_info(alerts)"
        )

        columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        required_columns = {
            "id",
            "agent_id",
            "timestamp",
            "cpu_usage",
            "memory_usage",
            "anomaly_detected",
            "anomaly_score",
            "risk_score",
            "severity",
            "message",
            "reasons"
        }

        assert required_columns.issubset(columns)

    finally:

        connection.close()