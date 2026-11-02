import platform
import socket
import psutil
from datetime import datetime


def get_system_information():
    """
    Collect basic information about the monitored computer.

    Returns:
        dict: System information.
    """

    try:
        boot_time = psutil.boot_time()

        boot_time_formatted = datetime.fromtimestamp(
            boot_time
        ).strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        boot_time_formatted = "Unknown"

    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "Unknown"

    try:
        operating_system = platform.system()
    except Exception:
        operating_system = "Unknown"

    try:
        operating_system_version = platform.version()
    except Exception:
        operating_system_version = "Unknown"

    try:
        operating_system_release = platform.release()
    except Exception:
        operating_system_release = "Unknown"

    try:
        machine = platform.machine()
    except Exception:
        machine = "Unknown"

    try:
        processor = platform.processor()

        if not processor:
            processor = "Unknown"

    except Exception:
        processor = "Unknown"

    try:
        logical_cpu_count = psutil.cpu_count(logical=True)
    except Exception:
        logical_cpu_count = None

    try:
        physical_cpu_count = psutil.cpu_count(logical=False)
    except Exception:
        physical_cpu_count = None

    return {
        "hostname": hostname,
        "operating_system": operating_system,
        "operating_system_version": operating_system_version,
        "operating_system_release": operating_system_release,
        "machine": machine,
        "processor": processor,
        "logical_cpu_count": logical_cpu_count,
        "physical_cpu_count": physical_cpu_count,
        "boot_time": boot_time_formatted
    }


if __name__ == "__main__":

    print("=" * 70)
    print("SENTINELNET SYSTEM INFORMATION")
    print("=" * 70)

    information = get_system_information()

    print(f"Hostname              : {information['hostname']}")
    print(f"Operating System      : {information['operating_system']}")
    print(f"OS Version            : {information['operating_system_version']}")
    print(f"OS Release            : {information['operating_system_release']}")
    print(f"Machine Architecture  : {information['machine']}")
    print(f"Processor             : {information['processor']}")
    print(f"Physical CPU Cores    : {information['physical_cpu_count']}")
    print(f"Logical CPU Cores     : {information['logical_cpu_count']}")
    print(f"System Boot Time      : {information['boot_time']}")

    print("=" * 70)
    print("System information test completed successfully.")