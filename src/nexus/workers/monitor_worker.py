"""Background QThread worker for non-blocking resource sampling."""
import time
from typing import List, Optional
from PySide6.QtCore import QObject, QThread, Signal, Slot

from src.nexus.monitoring.system_monitor import SystemMonitor, SystemSnapshot
from src.nexus.monitoring.process_monitor import ProcessMonitor, ProcessInfo
from src.nexus.utils.logging_config import setup_logger

logger = setup_logger("nexus.monitor_worker")


class MonitorWorker(QObject):
    """
    Worker that executes on a dedicated background QThread.
    Emits snapshots to the GUI via thread-safe Qt Signals.
    """
    system_updated = Signal(object)      # SystemSnapshot
    processes_updated = Signal(list)     # List[ProcessInfo]
    error_occurred = Signal(str)

    def __init__(self, refresh_interval_ms: int = 2000):
        super().__init__()
        self._interval_sec = refresh_interval_ms / 1000.0
        self._running = False
        self._system_monitor: Optional[SystemMonitor] = None
        self._process_monitor: Optional[ProcessMonitor] = None
        # Track iteration to sample processes (process enumeration is heavier than system stats)
        self._iteration = 0

    @Slot()
    def start_monitoring(self):
        """Main loop executed in the worker thread."""
        self._running = True
        logger.info("MonitorWorker started.")
        self._system_monitor = SystemMonitor()
        self._process_monitor = ProcessMonitor()

        while self._running:
            loop_start = time.time()
            try:
                # 1. Collect System Metrics
                if self._system_monitor:
                    snap = self._system_monitor.get_system_snapshot()
                    self.system_updated.emit(snap)

                # 2. Collect Processes
                # We update processes on every loop iteration
                if self._process_monitor:
                    procs = self._process_monitor.get_processes()
                    self.processes_updated.emit(procs)

            except Exception as exc:
                logger.error(f"Error in monitor worker loop: {exc}")
                self.error_occurred.emit(str(exc))

            # Sleep remaining time to respect refresh interval
            elapsed = time.time() - loop_start
            sleep_duration = max(0.1, self._interval_sec - elapsed)

            # Responsive sleep in slices so stop() responds quickly
            steps = int(sleep_duration / 0.1)
            for _ in range(steps):
                if not self._running:
                    break
                time.sleep(0.1)

        logger.info("MonitorWorker stopped.")

    @Slot()
    def stop_monitoring(self):
        """Signals the worker loop to terminate."""
        self._running = False

    @Slot(int)
    def update_interval(self, interval_ms: int):
        """Updates the sampling frequency."""
        self._interval_sec = max(0.5, interval_ms / 1000.0)
        logger.info(f"MonitorWorker interval set to {self._interval_sec}s")
