import time
from datetime import datetime

import requests

from agent_config import (
    AGENT_ID,
    AGENT_NAME,
    CONSOLE_URL,
    COLLECTION_INTERVAL,
    REQUEST_TIMEOUT,
    MAX_PROCESSES,
    MAX_NETWORK_CONNECTIONS
)

from monitoring import get_system_metrics
from process_monitor import get_top_processes
from network_monitor import get_network_connections
from system_info import get_system_information


def collect_monitoring_data():
    """
    Collect all monitoring information from the local computer.
    """

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # -------------------------------------------------
    # SYSTEM METRICS
    # -------------------------------------------------

    metrics = get_system_metrics()

    # -------------------------------------------------
    # PROCESS INFORMATION
    # -------------------------------------------------

    processes = get_top_processes()

    # -------------------------------------------------
    # NETWORK INFORMATION
    # -------------------------------------------------

    network_connections = get_network_connections()

    # -------------------------------------------------
    # SYSTEM INFORMATION
    # -------------------------------------------------

    system_information = get_system_information()

    # -------------------------------------------------
    # LIMIT DATA SIZE
    # -------------------------------------------------

    processes = processes[:MAX_PROCESSES]

    network_connections = network_connections[
        :MAX_NETWORK_CONNECTIONS
    ]

    # -------------------------------------------------
    # BUILD COMPLETE DATA PACKAGE
    # -------------------------------------------------

    data = {
        "agent_id": AGENT_ID,
        "agent_name": AGENT_NAME,
        "timestamp": timestamp,
        "system_info": system_information,
        "metrics": metrics,
        "processes": processes,
        "network_connections": network_connections
    }

    return data


def send_monitoring_data(data):
    """
    Send monitoring data to the Security Console.
    """

    try:

        response = requests.post(
            CONSOLE_URL,
            json=data,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:

            print(
                "[SUCCESS] Monitoring data sent to Console."
            )

            print(
                f"[SUCCESS] Agent ID: "
                f"{data['agent_id']}"
            )

            print(
                f"[SUCCESS] Processes stored: "
                f"{len(data['processes'])}"
            )

            print(
                f"[SUCCESS] Network connections stored: "
                f"{len(data['network_connections'])}"
            )

            # -------------------------------------------------
            # DISPLAY SECURITY ANALYSIS
            # -------------------------------------------------

            try:

                result = response.json()

                security_analysis = result.get(
                    "security_analysis"
                )

                if security_analysis:

                    print()
                    print("SECURITY ANALYSIS")
                    print("-" * 70)

                    print(
                        f"ML Anomaly       : "
                        f"{security_analysis.get('anomaly_detected')}"
                    )

                    print(
                        f"Anomaly Score    : "
                        f"{security_analysis.get('anomaly_score')}"
                    )

                    print(
                        f"Risk Score       : "
                        f"{security_analysis.get('risk_score')}/100"
                    )

                    print(
                        f"Severity         : "
                        f"{security_analysis.get('severity')}"
                    )

                    print(
                        f"Alert Created    : "
                        f"{security_analysis.get('alert_created')}"
                    )

            except ValueError:

                print(
                    "[WARNING] Console returned "
                    "a non-JSON response."
                )

            return True

        else:

            print(
                f"[ERROR] Console returned HTTP "
                f"{response.status_code}"
            )

            print(
                "[ERROR] Console response:"
            )

            print(
                response.text
            )

            return False

    except requests.exceptions.ConnectionError:

        print(
            "[ERROR] Could not connect to "
            "the Security Console."
        )

        return False

    except requests.exceptions.Timeout:

        print(
            "[ERROR] Request to Security Console "
            "timed out."
        )

        return False

    except requests.exceptions.RequestException as error:

        print(
            f"[ERROR] Request failed: {error}"
        )

        return False


def display_monitoring_data(data):
    """
    Display collected monitoring information.
    """

    print("=" * 70)
    print("SENTINELNET MONITORING AGENT")
    print("=" * 70)

    print(
        f"Agent ID          : "
        f"{data['agent_id']}"
    )

    print(
        f"Timestamp         : "
        f"{data['timestamp']}"
    )

    print()

    print("SYSTEM METRICS")
    print("-" * 70)

    print(
        f"CPU Usage         : "
        f"{data['metrics']['cpu']}%"
    )

    print(
        f"Memory Usage      : "
        f"{data['metrics']['memory']}%"
    )

    print()

    print("MONITORING DATA")
    print("-" * 70)

    print(
        f"Processes         : "
        f"{len(data['processes'])}"
    )

    print(
        f"Network Connections: "
        f"{len(data['network_connections'])}"
    )

    print()

    print("SYSTEM INFORMATION")
    print("-" * 70)

    print(
        f"Hostname          : "
        f"{data['system_info'].get('hostname')}"
    )

    print(
        f"Operating System  : "
        f"{data['system_info'].get('operating_system')}"
    )

    print(
        f"OS Release        : "
        f"{data['system_info'].get('operating_system_release')}"
    )

    print("=" * 70)


def main():
    """
    Main SentinelNet monitoring loop.
    """

    print()
    print("=" * 70)
    print("SENTINELNET MONITORING AGENT STARTED")
    print("=" * 70)

    print(
        f"Agent ID: {AGENT_ID}"
    )

    print(
        f"Console: {CONSOLE_URL}"
    )

    print(
        f"Collection interval: "
        f"{COLLECTION_INTERVAL} seconds"
    )

    print("=" * 70)
    print()

    while True:

        try:

            data = collect_monitoring_data()

            display_monitoring_data(
                data
            )

            send_monitoring_data(
                data
            )

            print()

            time.sleep(
                COLLECTION_INTERVAL
            )

        except KeyboardInterrupt:

            print()
            print(
                "SentinelNet Monitoring Agent stopped."
            )

            break

        except Exception as error:

            print(
                f"[ERROR] Monitoring cycle failed: "
                f"{error}"
            )

            print(
                f"Retrying in "
                f"{COLLECTION_INTERVAL} seconds..."
            )

            time.sleep(
                COLLECTION_INTERVAL
            )


if __name__ == "__main__":

    main()