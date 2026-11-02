import sys
from pathlib import Path


# Add the monitoring_agent folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MONITORING_AGENT_PATH = PROJECT_ROOT / "monitoring_agent"

sys.path.insert(0, str(MONITORING_AGENT_PATH))


from monitoring import get_cpu_usage
from monitoring import get_memory_usage
from monitoring import get_system_metrics

from process_monitor import get_running_processes
from process_monitor import get_top_processes

from network_monitor import get_network_connections

from system_info import get_system_information


def test_cpu_usage():

    cpu = get_cpu_usage()

    assert isinstance(cpu, (int, float))

    assert 0 <= cpu <= 100


def test_memory_usage():

    memory = get_memory_usage()

    assert isinstance(memory, dict)

    assert "percent" in memory
    assert "total" in memory
    assert "available" in memory
    assert "used" in memory

    assert 0 <= memory["percent"] <= 100


def test_system_metrics():

    metrics = get_system_metrics()

    assert isinstance(metrics, dict)

    assert "cpu" in metrics
    assert "memory" in metrics
    assert "memory_total" in metrics
    assert "memory_available" in metrics
    assert "memory_used" in metrics

    assert 0 <= metrics["cpu"] <= 100
    assert 0 <= metrics["memory"] <= 100


def test_running_processes():

    processes = get_running_processes()

    assert isinstance(processes, list)

    for process in processes:

        assert isinstance(process, dict)

        assert "pid" in process
        assert "name" in process
        assert "status" in process
        assert "cpu_percent" in process
        assert "memory_percent" in process
        assert "username" in process


def test_top_processes():

    processes = get_top_processes(5)

    assert isinstance(processes, list)

    assert len(processes) <= 5

    for process in processes:

        assert "pid" in process
        assert "name" in process
        assert "cpu_percent" in process
        assert "memory_percent" in process


def test_network_connections():

    connections = get_network_connections()

    assert isinstance(connections, list)

    for connection in connections:

        assert isinstance(connection, dict)

        assert "pid" in connection
        assert "process_name" in connection
        assert "protocol" in connection
        assert "local_ip" in connection
        assert "local_port" in connection
        assert "remote_ip" in connection
        assert "remote_port" in connection
        assert "status" in connection


def test_system_information():

    information = get_system_information()

    assert isinstance(information, dict)

    assert "hostname" in information
    assert "operating_system" in information
    assert "operating_system_release" in information