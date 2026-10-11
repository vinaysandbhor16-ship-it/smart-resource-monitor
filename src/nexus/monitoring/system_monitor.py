"""System metrics monitoring module using psutil."""
import os
import platform
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import psutil

from src.nexus.utils.logging_config import setup_logger

logger = setup_logger("nexus.system_monitor")


@dataclass
class DiskPartitionInfo:
    device: str
    mountpoint: str
    fstype: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent: float


@dataclass
class NetworkStats:
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    send_rate_bps: float = 0.0  # Bytes per second
    recv_rate_bps: float = 0.0  # Bytes per second


@dataclass
class SystemSnapshot:
    timestamp: float
    cpu_percent: float
    per_cpu_percent: List[float]
    cpu_count_logical: int
    cpu_count_physical: int
    cpu_freq_current: Optional[float]
    
    # Memory metrics
    memory_total: int
    memory_available: int
    memory_used: int
    memory_percent: float
    swap_total: int
    swap_used: int
    swap_percent: float

    # System & OS
    system_platform: str
    system_architecture: str
    system_version: str
    uptime_seconds: float
    total_processes: int

    # Disks & Network
    disks: List[DiskPartitionInfo] = field(default_factory=list)
    primary_disk_percent: float = 0.0
    network: Optional[NetworkStats] = None


class SystemMonitor:
    """Collects real-time OS metrics without blocking or fabricating measurements."""

    def __init__(self):
        self._last_net_io = None
        self._last_net_time = None
        # Prime psutil's internal CPU calculation on initialization
        try:
            psutil.cpu_percent(interval=None)
            psutil.cpu_percent(interval=None, percpu=True)
        except Exception as exc:
            logger.warning(f"Error priming CPU counters: {exc}")

    def get_system_snapshot(self) -> SystemSnapshot:
        """Gathers a consistent snapshot of real system resources."""
        now = time.time()

        # 1. CPU Metrics
        # Passing interval=None computes utilization non-blockingly since the last check
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            per_cpu = psutil.cpu_percent(interval=None, percpu=True)
        except Exception as exc:
            logger.error(f"Failed to read CPU metrics: {exc}")
            cpu_percent = 0.0
            per_cpu = []

        cpu_logical = psutil.cpu_count(logical=True) or 1
        cpu_physical = psutil.cpu_count(logical=False) or cpu_logical

        cpu_freq_current = None
        try:
            freq = psutil.cpu_freq()
            if freq:
                cpu_freq_current = freq.current
        except Exception:
            # Frequency is not supported on all platforms/virtual environments
            pass

        # 2. Memory Metrics
        try:
            vmem = psutil.virtual_memory()
            mem_total = vmem.total
            mem_avail = vmem.available
            mem_used = vmem.used
            mem_pct = vmem.percent
        except Exception as exc:
            logger.error(f"Failed to read virtual memory: {exc}")
            mem_total = mem_avail = mem_used = 0
            mem_pct = 0.0

        try:
            smem = psutil.swap_memory()
            swap_total = smem.total
            swap_used = smem.used
            swap_pct = smem.percent
        except Exception:
            swap_total = swap_used = 0
            swap_pct = 0.0

        # 3. Disks
        disk_list: List[DiskPartitionInfo] = []
        primary_disk_pct = 0.0
        try:
            partitions = psutil.disk_partitions(all=False)
            for part in partitions:
                # Filter out raw CD-ROM or disconnected devices on Windows
                if "cdrom" in part.opts or part.fstype == "":
                    continue
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disk_info = DiskPartitionInfo(
                        device=part.device,
                        mountpoint=part.mountpoint,
                        fstype=part.fstype,
                        total_bytes=usage.total,
                        used_bytes=usage.used,
                        free_bytes=usage.free,
                        percent=usage.percent,
                    )
                    disk_list.append(disk_info)
                except (PermissionError, OSError):
                    continue
            if disk_list:
                primary_disk_pct = disk_list[0].percent
        except Exception as exc:
            logger.warning(f"Error enumerating disk partitions: {exc}")

        # 4. Network Metrics & Transfer Rates
        net_stats = None
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                send_rate = 0.0
                recv_rate = 0.0
                if self._last_net_io and self._last_net_time:
                    dt = now - self._last_net_time
                    if dt > 0:
                        send_rate = max(0.0, (net_io.bytes_sent - self._last_net_io.bytes_sent) / dt)
                        recv_rate = max(0.0, (net_io.bytes_recv - self._last_net_io.bytes_recv) / dt)

                self._last_net_io = net_io
                self._last_net_time = now

                net_stats = NetworkStats(
                    bytes_sent=net_io.bytes_sent,
                    bytes_recv=net_io.bytes_recv,
                    packets_sent=net_io.packets_sent,
                    packets_recv=net_io.packets_recv,
                    send_rate_bps=send_rate,
                    recv_rate_bps=recv_rate,
                )
        except Exception as exc:
            logger.debug(f"Network stats unavailable: {exc}")

        # 5. OS & Uptime
        try:
            boot_time = psutil.boot_time()
            uptime = max(0.0, now - boot_time)
        except Exception:
            uptime = 0.0

        try:
            proc_count = len(psutil.pids())
        except Exception:
            proc_count = 0

        return SystemSnapshot(
            timestamp=now,
            cpu_percent=cpu_percent,
            per_cpu_percent=per_cpu,
            cpu_count_logical=cpu_logical,
            cpu_count_physical=cpu_physical,
            cpu_freq_current=cpu_freq_current,
            memory_total=mem_total,
            memory_available=mem_avail,
            memory_used=mem_used,
            memory_percent=mem_pct,
            swap_total=swap_total,
            swap_used=swap_used,
            swap_percent=swap_pct,
            system_platform=platform.system(),
            system_architecture=f"{platform.machine()} ({platform.architecture()[0]})",
            system_version=platform.version() or platform.release(),
            uptime_seconds=uptime,
            total_processes=proc_count,
            disks=disk_list,
            primary_disk_percent=primary_disk_pct,
            network=net_stats,
        )
