"""Performance Page: Detailed breakdown of CPU, RAM, Disk partitions, and Network."""
from collections import deque
from typing import Optional
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.nexus.config import HISTORY_BUFFER_MAX_POINTS
from src.nexus.monitoring.system_monitor import SystemSnapshot
from src.nexus.ui.components import MetricCard, InfoStatCard


class PerformancePage(QWidget):
    """Detailed hardware architecture, multi-core CPU monitoring, and storage partitions."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.net_in_history = deque(maxlen=HISTORY_BUFFER_MAX_POINTS)
        self.net_out_history = deque(maxlen=HISTORY_BUFFER_MAX_POINTS)

        self._init_ui()

    def _init_ui(self):
        # Use scroll area to ensure all hardware partitions fit nicely
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # 1. Hardware & Architecture Specs
        spec_frame = QFrame()
        spec_frame.setProperty("class", "MetricCard")
        spec_box = QVBoxLayout(spec_frame)
        spec_title = QLabel("SYSTEM ARCHITECTURE & HARDWARE PROFILE")
        spec_title.setProperty("class", "CardTitle")
        spec_box.addWidget(spec_title)

        grid = QGridLayout()
        grid.setSpacing(10)
        self.lbl_os = QLabel("—")
        self.lbl_arch = QLabel("—")
        self.lbl_cores = QLabel("—")
        self.lbl_freq = QLabel("—")

        grid.addWidget(QLabel("Operating System:"), 0, 0)
        grid.addWidget(self.lbl_os, 0, 1)
        grid.addWidget(QLabel("Architecture:"), 0, 2)
        grid.addWidget(self.lbl_arch, 0, 3)
        grid.addWidget(QLabel("CPU Topology:"), 1, 0)
        grid.addWidget(self.lbl_cores, 1, 1)
        grid.addWidget(QLabel("CPU Frequency:"), 1, 2)
        grid.addWidget(self.lbl_freq, 1, 3)

        spec_box.addLayout(grid)
        layout.addWidget(spec_frame)

        # 2. Storage Partitions Table
        disk_frame = QFrame()
        disk_frame.setProperty("class", "MetricCard")
        disk_box = QVBoxLayout(disk_frame)
        disk_title = QLabel("STORAGE PARTITIONS & MOUNT POINTS")
        disk_title.setProperty("class", "CardTitle")
        disk_box.addWidget(disk_title)

        self.disk_table = QTableWidget(0, 6)
        self.disk_table.setHorizontalHeaderLabels([
            "Device", "Mountpoint", "Filesystem", "Total (GB)", "Used (GB)", "Free (GB)"
        ])
        self.disk_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.disk_table.verticalHeader().setVisible(False)
        self.disk_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.disk_table.setFixedHeight(140)
        disk_box.addWidget(self.disk_table)
        layout.addWidget(disk_frame)

        # 3. Network I/O Rates (KB/s)
        net_frame = QFrame()
        net_frame.setProperty("class", "MetricCard")
        net_box = QVBoxLayout(net_frame)
        net_title = QLabel("NETWORK ADAPTER ACTIVITY (THROUGHPUT)")
        net_title.setProperty("class", "CardTitle")
        net_box.addWidget(net_title)

        self.lbl_net_stats = QLabel("Receiving: 0.0 KB/s | Sending: 0.0 KB/s")
        self.lbl_net_stats.setStyleSheet("font-size: 14px; font-weight: bold; color: #38BDF8;")
        net_box.addWidget(self.lbl_net_stats)

        self.net_plot = pg.PlotWidget()
        self.net_plot.setBackground("#0F172A")
        self.net_plot.showGrid(x=True, y=True, alpha=0.15)
        self.net_plot.setFixedHeight(180)
        self.net_plot.getAxis("bottom").setStyle(showValues=False)
        self.recv_curve = self.net_plot.plot(
            pen=pg.mkPen(color="#34D399", width=2),
            name="Download Rate",
        )
        self.send_curve = self.net_plot.plot(
            pen=pg.mkPen(color="#F43F5E", width=2),
            name="Upload Rate",
        )
        net_box.addWidget(self.net_plot)
        layout.addWidget(net_frame)

        scroll.setWidget(container)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)

    def update_system_data(self, snap: SystemSnapshot):
        """Updates architecture and dynamic partition statistics."""
        self.lbl_os.setText(f"{snap.system_platform} ({snap.system_version})")
        self.lbl_arch.setText(snap.system_architecture)
        self.lbl_cores.setText(f"{snap.cpu_count_physical} Cores, {snap.cpu_count_logical} Logical Processors")
        self.lbl_freq.setText(f"{snap.cpu_freq_current:.1f} MHz" if snap.cpu_freq_current else "Dynamic")

        # Disks
        self.disk_table.setRowCount(len(snap.disks))
        for row, d in enumerate(snap.disks):
            self.disk_table.setItem(row, 0, QTableWidgetItem(d.device))
            self.disk_table.setItem(row, 1, QTableWidgetItem(d.mountpoint))
            self.disk_table.setItem(row, 2, QTableWidgetItem(d.fstype))
            self.disk_table.setItem(row, 3, QTableWidgetItem(f"{d.total_bytes / (1024**3):.1f}"))
            self.disk_table.setItem(row, 4, QTableWidgetItem(f"{d.used_bytes / (1024**3):.1f} ({d.percent:.1f}%)"))
            self.disk_table.setItem(row, 5, QTableWidgetItem(f"{d.free_bytes / (1024**3):.1f}"))

        # Network
        if snap.network:
            recv_kb = snap.network.recv_rate_bps / 1024.0
            send_kb = snap.network.send_rate_bps / 1024.0
            total_recv_mb = snap.network.bytes_recv / (1024**2)
            total_sent_mb = snap.network.bytes_sent / (1024**2)

            self.lbl_net_stats.setText(
                f"Down: {recv_kb:.1f} KB/s (Total: {total_recv_mb:.0f} MB)   |   "
                f"Up: {send_kb:.1f} KB/s (Total: {total_sent_mb:.0f} MB)"
            )

            self.net_in_history.append(recv_kb)
            self.net_out_history.append(send_kb)

            x = list(range(len(self.net_in_history)))
            self.recv_curve.setData(x, list(self.net_in_history))
            self.send_curve.setData(x, list(self.net_out_history))
