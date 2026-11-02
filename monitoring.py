import psutil


def get_cpu_usage():
    """
    Return the current CPU usage percentage.
    """

    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    """
    Return the current memory usage information.
    """

    memory = psutil.virtual_memory()

    return {
        "percent": memory.percent,
        "total": memory.total,
        "available": memory.available,
        "used": memory.used
    }


def get_system_metrics():
    """
    Collect the main system metrics.

    Returns:
        dict: CPU and memory information.
    """

    cpu_usage = get_cpu_usage()
    memory = get_memory_usage()

    return {
        "cpu": cpu_usage,
        "memory": memory["percent"],
        "memory_total": memory["total"],
        "memory_available": memory["available"],
        "memory_used": memory["used"]
    }


if __name__ == "__main__":

    print("=" * 50)
    print("SENTINELNET MONITORING AGENT")
    print("System Monitoring Test")
    print("=" * 50)

    metrics = get_system_metrics()

    print(f"CPU Usage       : {metrics['cpu']}%")
    print(f"Memory Usage    : {metrics['memory']}%")
    print(f"Memory Used     : {metrics['memory_used']} bytes")
    print(f"Memory Available: {metrics['memory_available']} bytes")
    print(f"Memory Total    : {metrics['memory_total']} bytes")

    print("=" * 50)
    print("Monitoring test completed successfully.")