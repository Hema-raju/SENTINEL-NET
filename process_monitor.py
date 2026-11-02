import psutil


def get_process_info(process):
    """
    Safely collect information about one process.

    CPU usage is normalized to the total logical CPU capacity
    of the computer, so the displayed value stays between
    0% and 100%.

    Returns:
        dict or None
    """

    try:

        with process.oneshot():

            pid = process.pid

            name = process.name()

            status = process.status()

            # ------------------------------------------------
            # CPU USAGE
            # ------------------------------------------------

            cpu_percent = process.cpu_percent(interval=0.1)

            if cpu_percent < 0:
                cpu_percent = 0.0

            # ------------------------------------------------
            # Normalize process CPU usage.
            #
            # psutil can report process CPU usage above 100%
            # on multi-core systems.
            #
            # Example:
            # 8 logical CPUs
            # 400% psutil value
            # becomes 50% of total CPU capacity.
            # ------------------------------------------------

            logical_cpu_count = psutil.cpu_count(
                logical=True
            )

            if not logical_cpu_count:
                logical_cpu_count = 1

            cpu_percent = (
                cpu_percent / logical_cpu_count
            )

            # ------------------------------------------------
            # System Idle Process is not an actual
            # CPU-consuming application.
            #
            # PID 0 on Windows represents idle CPU time.
            # Therefore we display it as 0%.
            # ------------------------------------------------

            if pid == 0 or name == "System Idle Process":

                cpu_percent = 0.0

            # ------------------------------------------------
            # Keep CPU value inside 0-100%.
            # ------------------------------------------------

            cpu_percent = min(
                max(cpu_percent, 0.0),
                100.0
            )

            # ------------------------------------------------
            # MEMORY USAGE
            # ------------------------------------------------

            memory_percent = process.memory_percent()

            if memory_percent < 0:
                memory_percent = 0.0

            # ------------------------------------------------
            # USERNAME
            # ------------------------------------------------

            try:

                username = process.username()

            except (
                psutil.AccessDenied,
                psutil.NoSuchProcess,
                psutil.ZombieProcess
            ):

                username = "Unknown"

            # ------------------------------------------------
            # RETURN PROCESS INFORMATION
            # ------------------------------------------------

            return {
                "pid": pid,
                "name": name,
                "status": status,
                "cpu_percent": round(
                    cpu_percent,
                    2
                ),
                "memory_percent": round(
                    memory_percent,
                    2
                ),
                "username": username
            }

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess
    ):

        return None

    except Exception:

        return None


def get_running_processes():
    """
    Collect information about currently running processes.

    Returns:
        list: Process information dictionaries.
    """

    processes = []

    for process in psutil.process_iter():

        process_info = get_process_info(
            process
        )

        if process_info is not None:

            processes.append(
                process_info
            )

    return processes


def get_top_processes(limit=10):
    """
    Return the processes using the most CPU.

    Args:
        limit: Maximum number of processes to return.

    Returns:
        list: Top CPU-consuming processes.
    """

    processes = get_running_processes()

    processes.sort(
        key=lambda process:
            process["cpu_percent"],
        reverse=True
    )

    return processes[:limit]


if __name__ == "__main__":

    print("=" * 70)
    print("SENTINELNET PROCESS MONITOR")
    print("=" * 70)

    logical_cpu_count = psutil.cpu_count(
        logical=True
    )

    print(
        f"Logical CPU Cores: "
        f"{logical_cpu_count}"
    )

    print()

    processes = get_running_processes()

    print(
        f"Running Processes: "
        f"{len(processes)}"
    )

    print()

    print(
        f"{'PID':<8}"
        f"{'PROCESS':<30}"
        f"{'CPU %':<10}"
        f"{'MEM %':<10}"
        f"{'STATUS':<15}"
    )

    print("-" * 70)

    for process in get_top_processes(10):

        print(
            f"{process['pid']:<8}"
            f"{process['name'][:28]:<30}"
            f"{process['cpu_percent']:<10}"
            f"{process['memory_percent']:<10}"
            f"{process['status']:<15}"
        )

    print("=" * 70)
    print(
        "Process monitoring test completed successfully."
    )