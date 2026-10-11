"""Automated unit tests for ProcessMonitor and safe termination rules."""
import pytest
from unittest.mock import patch, MagicMock
from src.nexus.monitoring.process_monitor import ProcessMonitor, ProcessInfo


def test_process_collection_not_empty():
    """Verify that process collection yields running processes safely."""
    monitor = ProcessMonitor()
    procs = monitor.get_processes()

    assert isinstance(procs, list)
    assert len(procs) > 0

    first = procs[0]
    assert isinstance(first, ProcessInfo)
    assert first.pid >= 0
    assert isinstance(first.name, str)
    assert first.memory_mb >= 0.0


def test_protected_process_policy():
    """Verify kernel/init PID 0 and 1, as well as critical names are protected."""
    monitor = ProcessMonitor()

    # PID 0 & 1
    is_prot, _ = monitor.is_protected_process(0, "System")
    assert is_prot is True

    is_prot, _ = monitor.is_protected_process(1, "init")
    assert is_prot is True

    # Windows critical processes
    is_prot, reason = monitor.is_protected_process(9999, "csrss.exe")
    # If on windows, csrss is blocked
    import platform
    if platform.system().lower() == "windows":
        assert is_prot is True
        assert "Windows system component" in reason


def test_safe_termination_blocks_protected_process():
    """Verify termination method refuses to terminate protected processes."""
    monitor = ProcessMonitor()

    with patch.object(monitor, "is_protected_process", return_value=(True, "System process")):
        success, msg = monitor.terminate_process(0)
        assert success is False
        assert "Action blocked" in msg
