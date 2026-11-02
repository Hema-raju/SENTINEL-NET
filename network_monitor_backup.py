import socket
import psutil


def get_protocol(connection_type):
    """
    Convert psutil socket type into a readable protocol name.
    """

    if connection_type == socket.SOCK_STREAM:
        return "TCP"

    if connection_type == socket.SOCK_DGRAM:
        return "UDP"

    return "UNKNOWN"


def get_address_info(address):
    """
    Safely extract IP address and port from a psutil address object.
    """

    if not address:
        return {
            "ip": None,
            "port": None
        }

    try:
        return {
            "ip": address.ip,
            "port": address.port
        }

    except AttributeError:
        return {
            "ip": None,
            "port": None
        }


def get_network_connections():
    """
    Collect currently visible network connections.

    Returns:
        list: Network connection information.
    """

    connections = []

    try:
        raw_connections = psutil.net_connections(kind="inet")

    except psutil.AccessDenied:
        return connections

    except Exception:
        return connections

    for connection in raw_connections:

        try:
            local_address = get_address_info(connection.laddr)
            remote_address = get_address_info(connection.raddr)

            pid = connection.pid

            process_name = "Unknown"

            if pid is not None:

                try:
                    process_name = psutil.Process(pid).name()

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess
                ):
                    process_name = "Unknown"

            protocol = get_protocol(connection.type)

            connection_info = {
                "pid": pid,
                "process_name": process_name,
                "protocol": protocol,
                "local_ip": local_address["ip"],
                "local_port": local_address["port"],
                "remote_ip": remote_address["ip"],
                "remote_port": remote_address["port"],
                "status": connection.status
            }

            connections.append(connection_info)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

        except Exception:
            continue

    return connections


if __name__ == "__main__":

    print("=" * 100)
    print("SENTINELNET NETWORK MONITOR")
    print("=" * 100)

    connections = get_network_connections()

    print(f"Visible Network Connections: {len(connections)}")
    print()

    print(
        f"{'PID':<8}"
        f"{'PROCESS':<25}"
        f"{'PROTO':<8}"
        f"{'LOCAL':<25}"
        f"{'REMOTE':<25}"
        f"{'STATUS':<15}"
    )

    print("-" * 100)

    for connection in connections[:20]:

        local_address = (
            f"{connection['local_ip']}:"
            f"{connection['local_port']}"
            if connection["local_ip"] is not None
            else "-"
        )

        remote_address = (
            f"{connection['remote_ip']}:"
            f"{connection['remote_port']}"
            if connection["remote_ip"] is not None
            else "-"
        )

        print(
            f"{str(connection['pid']):<8}"
            f"{connection['process_name'][:23]:<25}"
            f"{connection['protocol']:<8}"
            f"{local_address:<25}"
            f"{remote_address:<25}"
            f"{connection['status']:<15}"
        )

    print("=" * 100)
    print("Network monitoring test completed successfully.")