"""Process monitoring and safe process management module."""
import os
import platform
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import psutil

from src.nexus.config import (
    PROTECTED_PID_LIST,
    WINDOWS_CRITICAL_PROCESSES,
    LINUX_CRITICAL_PROCESSES,
)
from src.nexus.utils.logging_config import setup_logger

logger = setup_logger("nexus.process_monitor")


@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_rss_bytes: int  # Resident Set Size
    memory_vms_bytes: int  # Virtual Memory Size
    status: str
    username: str
    create_time: float
    exe_path: str
    num_threads: int
    is_protected: bool = False

    @property
    def memory_mb(self) -> float:
        return self.memory_rss_bytes / (1024 * 1024)


class ProcessMonitor:
    """Collects and filters process data safely without breaking on restricted processes."""

    def __init__(self):
        self._current_pid = os.getpid()

    def is_protected_process(self, pid: int, name: str) -> Tuple[bool, str]:
        """
        Conservative protection policy.
        Returns (is_protected, reason).
        Note: Documented that no blacklist can guarantee 100% operating system safety.
        """
        if pid in PROTECTED_PID_LIST:
            return True, f"PID {pid} is reserved by the Operating System kernel/init."

        if pid == self._current_pid:
            return True, "Cannot terminate NEXUS itself."

        lower_name = name.lower().strip()
        system_type = platform.system().lower()

        if "windows" in system_type:
            if lower_name in WINDOWS_CRITICAL_PROCESSES:
                return True, f"'{name}' is an essential Windows system component."
        else:
            if lower_name in LINUX_CRITICAL_PROCESSES:
                return True, f"'{name}' is a critical Unix/Linux service."

        return False, ""

    def get_processes(self) -> List[ProcessInfo]:
        """
        Iterates over accessible processes using psutil.process_iter.
        Handles AccessDenied, NoSuchProcess, ZombieProcess cleanly.
        """
        processes: List[ProcessInfo] = []

        # Request specific attributes for efficiency
        attrs = [
            "pid",
            "name",
            "cpu_percent",
            "memory_percent",
            "memory_info",
            "status",
            "username",
            "create_time",
            "exe",
            "num_threads",
        ]

        for proc in psutil.process_iter(attrs, ad_value=None):
            try:
                info = proc.info
                pid = info.get("pid")
                if pid is None:
                    continue

                name = info.get("name") or "Unknown"
                cpu_pct = info.get("cpu_percent") or 0.0
                mem_pct = info.get("memory_percent") or 0.0
                
                mem_info = info.get("memory_info")
                mem_rss = mem_info.rss if mem_info else 0
                mem_vms = mem_info.vms if mem_info else 0

                status = info.get("status") or "running"
                username = info.get("username") or "N/A"
                create_time = info.get("create_time") or 0.0
                exe_path = info.get("exe") or "Protected/Inaccessible"
                num_threads = info.get("num_threads") or 1

                is_protected, _ = self.is_protected_process(pid, name)

                processes.append(
                    ProcessInfo(
                        pid=pid,
                        name=name,
                        cpu_percent=cpu_pct,
                        memory_percent=mem_pct,
                        memory_rss_bytes=mem_rss,
                        memory_vms_bytes=mem_vms,
                        status=status,
                        username=username,
                        create_time=create_time,
                        exe_path=exe_path,
                        num_threads=num_threads,
                        is_protected=is_protected,
                    )
                )
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                continue
            except psutil.AccessDenied:
                # Permission denied for this process: ignore and continue
                continue
            except Exception as exc:
                logger.debug(f"Error reading process: {exc}")
                continue

        return processes

    def terminate_process(self, pid: int, timeout: float = 3.0) -> Tuple[bool, str]:
        """
        Safely attempts graceful process termination (SIGTERM).
        Does NOT automatically force kill.
        Returns (success: bool, message: str).
        """
        # First check protection rules
        try:
            target = psutil.Process(pid)
            name = target.name()
        except psutil.NoSuchProcess:
            return False, f"Process with PID {pid} no longer exists."
        except psutil.AccessDenied:
            return False, f"Access denied: Process with PID {pid} requires elevated administrative permissions."
        except Exception as exc:
            return False, f"Cannot inspect PID {pid}: {exc}"

        is_protected, reason = self.is_protected_process(pid, name)
        if is_protected:
            return False, f"Action blocked: {reason}"

        # Attempt graceful termination
        try:
            target.terminate()
            # Wait for exit
            target.wait(timeout=timeout)
            logger.info(f"Successfully terminated process '{name}' (PID: {pid})")
            return True, f"Process '{name}' (PID: {pid}) was terminated successfully."
        except psutil.TimeoutExpired:
            logger.warning(f"Process '{name}' (PID: {pid}) did not exit within {timeout}s.")
            return False, (
                f"Process '{name}' (PID: {pid}) received termination signal but did not exit within {timeout} seconds. "
                "Force-killing is not performed automatically for safety."
            )
        except psutil.AccessDenied:
            logger.error(f"Permission denied terminating PID {pid}")
            return False, f"Access Denied: You do not have permission to terminate '{name}' (PID: {pid})."
        except psutil.NoSuchProcess:
            return True, f"Process '{name}' (PID: {pid}) exited."
        except Exception as exc:
            logger.error(f"Error terminating PID {pid}: {exc}")
            return False, f"Error terminating process: {exc}"
