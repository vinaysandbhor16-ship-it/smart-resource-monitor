"""Automated unit tests for ExportService (CSV and JSON generation)."""
import json
import os
import tempfile
import pytest
from src.nexus.monitoring.system_monitor import SystemSnapshot, DiskPartitionInfo
from src.nexus.monitoring.process_monitor import ProcessInfo
from src.nexus.services.export_service import ExportService


@pytest.fixture
def sample_processes():
    return [
        ProcessInfo(
            pid=100,
            name="test_worker.exe",
            cpu_percent=12.5,
            memory_percent=3.2,
            memory_rss_bytes=104857600,  # 100 MB
            memory_vms_bytes=209715200,
            status="running",
            username="testuser",
            create_time=1700000000.0,
            exe_path="C:/tools/test_worker.exe",
            num_threads=4,
        ),
        ProcessInfo(
            pid=200,
            name="editor.exe",
            cpu_percent=1.1,
            memory_percent=4.5,
            memory_rss_bytes=157286400,  # 150 MB
            memory_vms_bytes=314572800,
            status="sleeping",
            username="testuser",
            create_time=1700000010.0,
            exe_path="C:/tools/editor.exe",
            num_threads=8,
        ),
    ]


@pytest.fixture
def sample_snapshot():
    return SystemSnapshot(
        timestamp=1700000000.0,
        cpu_percent=35.0,
        per_cpu_percent=[30.0, 40.0],
        cpu_count_logical=8,
        cpu_count_physical=4,
        cpu_freq_current=2800.0,
        memory_total=17179869184,  # 16 GB
        memory_available=8589934592,
        memory_used=8589934592,
        memory_percent=50.0,
        swap_total=4294967296,
        swap_used=1073741824,
        swap_percent=25.0,
        system_platform="Windows",
        system_architecture="AMD64 (64bit)",
        system_version="10.0.22631",
        uptime_seconds=3600.0,
        total_processes=120,
        disks=[
            DiskPartitionInfo(
                device="C:\\",
                mountpoint="C:\\",
                fstype="NTFS",
                total_bytes=536870912000,
                used_bytes=268435456000,
                free_bytes=268435456000,
                percent=50.0,
            )
        ],
    )


def test_export_processes_to_csv(sample_processes):
    """Verify CSV export properly creates file with header and rows."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test_procs.csv")
        success = ExportService.export_processes_to_csv(csv_path, sample_processes)
        assert success is True
        assert os.path.exists(csv_path)

        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 3  # Header + 2 items
            assert "PID,Process Name,CPU (%),Memory (%),Memory (MB)" in lines[0]
            assert "test_worker.exe" in lines[1]
            assert "editor.exe" in lines[2]


def test_export_system_summary_to_json(sample_snapshot):
    """Verify JSON export creates structured, valid json format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "test_summary.json")
        success = ExportService.export_system_summary_to_json(json_path, sample_snapshot)
        assert success is True
        assert os.path.exists(json_path)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["system"]["platform"] == "Windows"
            assert data["cpu"]["utilization_percent"] == 35.0
            assert data["memory"]["total_gb"] == 16.0
            assert len(data["disks"]) == 1
            assert data["disks"][0]["mountpoint"] == "C:\\"
