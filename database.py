import os
import sqlite3

from console_config import DATABASE_PATH


def get_database_path():
    """
    Return the absolute path of the SentinelNet database.
    """

    base_directory = os.path.dirname(
        os.path.abspath(__file__)
    )

    database_path = os.path.join(
        base_directory,
        DATABASE_PATH
    )

    return os.path.abspath(database_path)


def get_connection():
    """
    Create a connection to the SQLite database.

    Returns:
        sqlite3.Connection
    """

    database_path = get_database_path()

    database_directory = os.path.dirname(
        database_path
    )

    os.makedirs(
        database_directory,
        exist_ok=True
    )

    connection = sqlite3.connect(
        database_path
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create the SentinelNet database tables.
    """

    connection = get_connection()

    cursor = connection.cursor()

    # -------------------------------------------------
    # AGENTS TABLE
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS agents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            agent_id TEXT NOT NULL UNIQUE,

            agent_name TEXT,

            hostname TEXT,

            operating_system TEXT,

            operating_system_version TEXT,

            operating_system_release TEXT,

            machine TEXT,

            processor TEXT,

            logical_cpu_count INTEGER,

            physical_cpu_count INTEGER,

            boot_time TEXT,

            first_seen TEXT,

            last_seen TEXT

        )
        """
    )

    # -------------------------------------------------
    # SYSTEM METRICS TABLE
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS system_metrics (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            agent_id TEXT NOT NULL,

            timestamp TEXT NOT NULL,

            cpu_usage REAL,

            memory_usage REAL,

            memory_total INTEGER,

            memory_available INTEGER,

            memory_used INTEGER

        )
        """
    )

    # -------------------------------------------------
    # PROCESS SNAPSHOTS TABLE
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS process_snapshots (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            agent_id TEXT NOT NULL,

            timestamp TEXT NOT NULL,

            pid INTEGER,

            process_name TEXT,

            status TEXT,

            cpu_percent REAL,

            memory_percent REAL,

            username TEXT

        )
        """
    )

    # -------------------------------------------------
    # NETWORK SNAPSHOTS TABLE
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS network_snapshots (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            agent_id TEXT NOT NULL,

            timestamp TEXT NOT NULL,

            pid INTEGER,

            process_name TEXT,

            protocol TEXT,

            local_ip TEXT,

            local_port INTEGER,

            remote_ip TEXT,

            remote_port INTEGER,

            status TEXT

        )
        """
    )

    # -------------------------------------------------
    # ALERTS TABLE
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            agent_id TEXT NOT NULL,

            timestamp TEXT NOT NULL,

            cpu_usage REAL,

            memory_usage REAL,

            anomaly_detected INTEGER NOT NULL,

            anomaly_score REAL,

            risk_score INTEGER,

            severity TEXT,

            message TEXT,

            reasons TEXT

        )
        """
    )

    connection.commit()

    connection.close()


if __name__ == "__main__":

    print("=" * 70)
    print("SENTINELNET DATABASE INITIALIZATION")
    print("=" * 70)

    initialize_database()

    print()
    print("Database initialized successfully.")
    print()
    print(
        f"Database location:"
        f"\n{get_database_path()}"
    )

    print("=" * 70)