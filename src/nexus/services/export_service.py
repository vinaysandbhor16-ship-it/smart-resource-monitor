"""Exports system summaries and process tables safely to JSON and CSV."""
import csv
import json
import time
from pathlib import Path
from typing import Any, Dict, List
from src.nexus.monitoring.system_monitor import SystemSnapshot
from src.nexus.monitoring.process_monitor import ProcessInfo
from src.nexus.utils.logging_config import setup_logger

logger = setup_logger("nexus.export_service")


class ExportService:
    """Handles clean data formatting and file writing with safety and error handling."""

    @staticmethod
    def export_processes_to_csv(filepath: str, processes: List[ProcessInfo]) -> bool:
        """Exports the accessible process list to CSV."""
        try:
            target_path = Path(filepath)
            target_path.parent.mkdir(parents=True, exist_ok=True)

            with open(target_path, mode="w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "PID",
                    "Process Name",
                    "CPU (%)",
                    "Memory (%)",
                    "Memory (MB)",
                    "Status",
                    "User",
                    "Threads",
                    "Executable Path",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for p in processes:
                    writer.writerow({
                        "PID": p.pid,
                        "Process Name": p.name,
                        "CPU (%)": f"{p.cpu_percent:.1f}",
                        "Memory (%)": f"{p.memory_percent:.1f}",
                        "Memory (MB)": f"{p.memory_mb:.1f}",
                        "Status": p.status,
                        "User": p.username,
                        "Threads": p.num_threads,
                        "Executable Path": p.exe_path,
                    })
            logger.info(f"Successfully exported {len(processes)} processes to {filepath}")
            return True
        except Exception as exc:
            logger.error(f"Failed to export processes to CSV {filepath}: {exc}")
            raise

    @staticmethod
    def export_system_summary_to_json(filepath: str, snapshot: SystemSnapshot) -> bool:
        """Exports a detailed hardware/system metrics snapshot to JSON."""
        try:
            target_path = Path(filepath)
            target_path.parent.mkdir(parents=True, exist_ok=True)

            data: Dict[str, Any] = {
                "report_metadata": {
                    "application": "NEXUS Smart Resource Monitor",
                    "exported_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(snapshot.timestamp)),
                    "timestamp": snapshot.timestamp,
                },
                "system": {
                    "platform": snapshot.system_platform,
                    "architecture": snapshot.system_architecture,
                    "version": snapshot.system_version,
                    "uptime_seconds": round(snapshot.uptime_seconds, 2),
                    "total_processes_running": snapshot.total_processes,
                },
                "cpu": {
                    "utilization_percent": snapshot.cpu_percent,
                    "logical_cores": snapshot.cpu_count_logical,
                    "physical_cores": snapshot.cpu_count_physical,
                    "frequency_mhz": snapshot.cpu_freq_current,
                    "per_cpu_percent": snapshot.per_cpu_percent,
                },
                "memory": {
                    "total_bytes": snapshot.memory_total,
                    "total_gb": round(snapshot.memory_total / (1024**3), 2),
                    "used_bytes": snapshot.memory_used,
                    "used_gb": round(snapshot.memory_used / (1024**3), 2),
                    "available_bytes": snapshot.memory_available,
                    "available_gb": round(snapshot.memory_available / (1024**3), 2),
                    "utilization_percent": snapshot.memory_percent,
                    "swap_total_gb": round(snapshot.swap_total / (1024**3), 2),
                    "swap_used_gb": round(snapshot.swap_used / (1024**3), 2),
                    "swap_percent": snapshot.swap_percent,
                },
                "disks": [
                    {
                        "device": d.device,
                        "mountpoint": d.mountpoint,
                        "filesystem": d.fstype,
                        "total_gb": round(d.total_bytes / (1024**3), 2),
                        "used_gb": round(d.used_bytes / (1024**3), 2),
                        "free_gb": round(d.free_bytes / (1024**3), 2),
                        "utilization_percent": d.percent,
                    }
                    for d in snapshot.disks
                ],
            }

            if snapshot.network:
                data["network"] = {
                    "bytes_sent": snapshot.network.bytes_sent,
                    "bytes_recv": snapshot.network.bytes_recv,
                    "send_rate_kbps": round(snapshot.network.send_rate_bps / 1024, 2),
                    "recv_rate_kbps": round(snapshot.network.recv_rate_bps / 1024, 2),
                }

            with open(target_path, mode="w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            logger.info(f"Successfully exported system summary to JSON at {filepath}")
            return True
        except Exception as exc:
            logger.error(f"Failed to export system summary to JSON {filepath}: {exc}")
            raise
