import socket
import psutil


# ============================================================
# PROTOCOL
# ============================================================

def get_protocol(connection_type):
    """
    Convert psutil socket type into a readable protocol name.

    Returns:
        str: TCP, UDP, or UNKNOWN
    """

    if connection_type == socket.SOCK_STREAM:
        return "TCP"

    if connection_type == socket.SOCK_DGRAM:
        return "UDP"

    return "UNKNOWN"


# ============================================================
# ADDRESS INFORMATION
# ============================================================

def get_address_info(address):
    """
    Safely extract IP address and port from a psutil address object.

    Returns:
        dict: IP address and port.
    """

    if not address:
        return {
            "ip": None,
            "port": None
        }

    try:

        ip_address = getattr(
            address,
            "ip",
            None
        )

        port = getattr(
            address,
            "port",
            None
        )

        return {
            "ip": ip_address,
            "port": port
        }

    except Exception:

        return {
            "ip": None,
            "port": None
        }


# ============================================================
# PROCESS NAME
# ============================================================

def get_process_name(pid):
    """
    Safely obtain the process name associated with a PID.

    Returns:
        str: Process name or Unknown.
    """

    if pid is None:
        return "Unknown"

    try:

        process = psutil.Process(pid)

        return process.name()

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess
    ):

        return "Unknown"

    except Exception:

        return "Unknown"


# ============================================================
# CONNECTION STATUS
# ============================================================

def get_connection_status(connection):
    """
    Safely obtain the connection status.

    TCP connections normally have states such as:
        LISTEN
        ESTABLISHED
        TIME_WAIT
        CLOSE_WAIT
        SYN_SENT

    UDP connections commonly have:
        NONE

    Returns:
        str: Normalized connection status.
    """

    try:

        status = connection.status

        if status is None:
            return "NONE"

        status = str(status).strip()

        if not status:
            return "NONE"

        return status.upper()

    except Exception:

        return "UNKNOWN"


# ============================================================
# NETWORK CONNECTION COLLECTION
# ============================================================

def get_network_connections():
    """
    Collect currently visible network connections.

    Uses psutil to obtain TCP and UDP network information.

    Returns:
        list: Network connection information.
    """

    connections = []

    try:

        raw_connections = psutil.net_connections(
            kind="inet"
        )

    except psutil.AccessDenied:

        return connections

    except Exception:

        return connections


    for connection in raw_connections:

        try:

            # ------------------------------------------------
            # Address information
            # ------------------------------------------------

            local_address = get_address_info(
                connection.laddr
            )

            remote_address = get_address_info(
                connection.raddr
            )


            # ------------------------------------------------
            # PID
            # ------------------------------------------------

            pid = connection.pid


            # ------------------------------------------------
            # Process name
            # ------------------------------------------------

            process_name = get_process_name(pid)


            # ------------------------------------------------
            # Protocol
            # ------------------------------------------------

            protocol = get_protocol(
                connection.type
            )


            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            status = get_connection_status(
                connection
            )


            # ------------------------------------------------
            # Build normalized record
            # ------------------------------------------------

            connection_info = {

                "pid": pid,

                "process_name": process_name,

                "protocol": protocol,

                "local_ip": local_address["ip"],

                "local_port": local_address["port"],

                "remote_ip": remote_address["ip"],

                "remote_port": remote_address["port"],

                "status": status
            }


            connections.append(
                connection_info
            )


        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            # The process may disappear while
            # the snapshot is being collected.
            continue


        except Exception:

            # Ignore one malformed connection
            # without stopping the entire collection.
            continue


    # ========================================================
    # SORTING
    # ========================================================
    #
    # Sorting makes the collected data more predictable.
    #
    # Priority:
    #   1. Process name
    #   2. Protocol
    #   3. Local IP
    #   4. Local port
    #
    # This does NOT remove any connections.
    # ========================================================

    connections.sort(
        key=lambda connection: (
            str(
                connection.get(
                    "process_name"
                ) or ""
            ).lower(),

            str(
                connection.get(
                    "protocol"
                ) or ""
            ),

            str(
                connection.get(
                    "local_ip"
                ) or ""
            ),

            int(
                connection.get(
                    "local_port"
                ) or 0
            )
        )
    )


    return connections


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 100)
    print("SENTINELNET NETWORK MONITOR")
    print("=" * 100)

    connections = get_network_connections()

    print(
        f"Visible Network Connections: "
        f"{len(connections)}"
    )

    print()

    print(
        f"{'PID':<8}"
        f"{'PROCESS':<25}"
        f"{'PROTO':<8}"
        f"{'LOCAL':<30}"
        f"{'REMOTE':<30}"
        f"{'STATUS':<15}"
    )

    print("-" * 115)


    for connection in connections[:20]:

        # ----------------------------------------------------
        # Local address
        # ----------------------------------------------------

        if connection["local_ip"] is not None:

            local_address = (
                f"{connection['local_ip']}:"
                f"{connection['local_port']}"
            )

        else:

            local_address = "-"


        # ----------------------------------------------------
        # Remote address
        # ----------------------------------------------------

        if connection["remote_ip"] is not None:

            remote_address = (
                f"{connection['remote_ip']}:"
                f"{connection['remote_port']}"
            )

        else:

            remote_address = "-"


        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        print(
            f"{str(connection['pid']):<8}"
            f"{connection['process_name'][:23]:<25}"
            f"{connection['protocol']:<8}"
            f"{local_address[:28]:<30}"
            f"{remote_address[:28]:<30}"
            f"{connection['status']:<15}"
        )


    print("=" * 100)

    print(
        "Network monitoring test completed successfully."
    )