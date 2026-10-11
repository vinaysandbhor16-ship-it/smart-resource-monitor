"""Automated unit tests for SystemMonitor."""
import pytest
from unittest.mock import patch, MagicMock
from src.nexus.monitoring.system_monitor import SystemMonitor, SystemSnapshot


def test_system_snapshot_types_and_ranges():
    """Verify real system snapshot returns non-negative numbers and correct types."""
    monitor = SystemMonitor()
    snap = monitor.get_system_snapshot()

    assert isinstance(snap, SystemSnapshot)
    assert 0.0 <= snap.cpu_percent <= 100.0
    assert snap.cpu_count_logical >= 1
    assert snap.memory_total > 0
    assert snap.memory_used >= 0
    assert 0.0 <= snap.memory_percent <= 100.0
    assert snap.uptime_seconds >= 0.0
    assert snap.system_platform != ""


def test_system_monitor_handles_disk_permission_error():
    """Verify that inaccessible partitions do not raise exceptions."""
    monitor = SystemMonitor()
    with patch("psutil.disk_usage", side_effect=PermissionError("Access denied")):
        snap = monitor.get_system_snapshot()
        assert isinstance(snap, SystemSnapshot)
        assert snap.disks == []


def test_system_monitor_handles_cpu_exception_gracefully():
    """Verify CPU exception degradation."""
    monitor = SystemMonitor()
    with patch("psutil.cpu_percent", side_effect=RuntimeError("CPU read failure")):
        snap = monitor.get_system_snapshot()
        assert snap.cpu_percent == 0.0
