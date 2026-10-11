"""Overview Dashboard Page: real-time summary cards, charts, and top processes."""
from collections import deque
from typing import List, Optional
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.nexus.config import HISTORY_BUFFER_MAX_POINTS
from src.nexus.monitoring.system_monitor import SystemSnapshot
from src.nexus.monitoring.process_monitor import ProcessInfo
from src.nexus.ui.components import MetricCard, InfoStatCard, AlertBanner


class OverviewPage(QWidget):
    """Primary dashboard presenting real-time system metrics, charts, and top consumers."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # In-memory bounded buffers for historical chart data
        self.cpu_history = deque(maxlen=HISTORY_BUFFER_MAX_POINTS)
        self.mem_history = deque(maxlen=HISTORY_BUFFER_MAX_POINTS)
        self.time_points = deque(maxlen=HISTORY_BUFFER_MAX_POINTS)
        self._point_counter = 0

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(18)

        # 1. Alert Banner
        self.alert_banner = AlertBanner()
        main_layout.addWidget(self.alert_banner)

        # 2. Metric Cards Grid
        cards_grid = QGridLayout()
        cards_grid.setSpacing(14)

        self.card_cpu = MetricCard("CPU Utilization", "%")
        self.card_memory = MetricCard("Memory (RAM)", "%")
        self.card_disk = MetricCard("Primary Disk", "%")
        self.card_uptime = InfoStatCard("System Uptime")

        cards_grid.addWidget(self.card_cpu, 0, 0)
        cards_grid.addWidget(self.card_memory, 0, 1)
        cards_grid.addWidget(self.card_disk, 0, 2)
        cards_grid.addWidget(self.card_uptime, 0, 3)

        main_layout.addLayout(cards_grid)

        # 3. Real-time Charts Section (CPU & Memory)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(14)

        # CPU Graph
        cpu_chart_card = QFrame()
        cpu_chart_card.setProperty("class", "MetricCard")
        cpu_vbox = QVBoxLayout(cpu_chart_card)
        cpu_title = QLabel("CPU USAGE HISTORY (RECENT)")
        cpu_title.setProperty("class", "CardTitle")
        cpu_vbox.addWidget(cpu_title)

        pg.setConfigOptions(antialias=True)
        self.cpu_plot = pg.PlotWidget()
        self.cpu_plot.setBackground("#0F172A")
        self.cpu_plot.setYRange(0, 100)
        self.cpu_plot.showGrid(x=True, y=True, alpha=0.15)
        self.cpu_plot.getAxis("bottom").setStyle(showValues=False)
        self.cpu_curve = self.cpu_plot.plot(
            pen=pg.mkPen(color="#38BDF8", width=2),
            brush=pg.mkBrush(color=(56, 189, 248, 40)),
            fillLevel=0,
        )
        cpu_vbox.addWidget(self.cpu_plot)
        charts_layout.addWidget(cpu_chart_card, 1)

        # Memory Graph
        mem_chart_card = QFrame()
        mem_chart_card.setProperty("class", "MetricCard")
        mem_vbox = QVBoxLayout(mem_chart_card)
        mem_title = QLabel("MEMORY USAGE HISTORY (RECENT)")
        mem_title.setProperty("class", "CardTitle")
        mem_vbox.addWidget(mem_title)

        self.mem_plot = pg.PlotWidget()
        self.mem_plot.setBackground("#0F172A")
        self.mem_plot.setYRange(0, 100)
        self.mem_plot.showGrid(x=True, y=True, alpha=0.15)
        self.mem_plot.getAxis("bottom").setStyle(showValues=False)
        self.mem_curve = self.mem_plot.plot(
            pen=pg.mkPen(color="#818CF8", width=2),
            brush=pg.mkBrush(color=(129, 140, 248, 40)),
            fillLevel=0,
        )
        mem_vbox.addWidget(self.mem_plot)
        charts_layout.addWidget(mem_chart_card, 1)

        main_layout.addLayout(charts_layout)

        # 4. Top Consumers Tables (Top 5 CPU & Top 5 Memory)
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(14)

        # Top 5 CPU
        top_cpu_frame = QFrame()
        top_cpu_frame.setProperty("class", "MetricCard")
        top_cpu_box = QVBoxLayout(top_cpu_frame)
        top_cpu_title = QLabel("TOP PROCESSES BY CPU")
        top_cpu_title.setProperty("class", "CardTitle")
        top_cpu_box.addWidget(top_cpu_title)

        self.top_cpu_table = self._create_mini_table(["PID", "Name", "CPU (%)"])
        top_cpu_box.addWidget(self.top_cpu_table)
        tables_layout.addWidget(top_cpu_frame, 1)

        # Top 5 Memory
        top_mem_frame = QFrame()
        top_mem_frame.setProperty("class", "MetricCard")
        top_mem_box = QVBoxLayout(top_mem_frame)
        top_mem_title = QLabel("TOP PROCESSES BY MEMORY")
        top_mem_title.setProperty("class", "CardTitle")
        top_mem_box.addWidget(top_mem_title)

        self.top_mem_table = self._create_mini_table(["PID", "Name", "RAM (MB)"])
        top_mem_box.addWidget(self.top_mem_table)
        tables_layout.addWidget(top_mem_frame, 1)

        main_layout.addLayout(tables_layout)

    def _create_mini_table(self, headers: List[str]) -> QTableWidget:
        table = QTableWidget(5, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setFixedHeight(160)
        return table

    def update_system_data(self, snap: SystemSnapshot):
        """Updates metric cards and real-time history charts."""
        # 1. Update Cards
        cpu_cores_text = f"{snap.cpu_count_physical} Cores / {snap.cpu_count_logical} Threads"
        if snap.cpu_freq_current:
            cpu_cores_text += f" @ {snap.cpu_freq_current:.0f} MHz"
        self.card_cpu.update_metric(snap.cpu_percent, cpu_cores_text)

        used_gb = snap.memory_used / (1024**3)
        total_gb = snap.memory_total / (1024**3)
        avail_gb = snap.memory_available / (1024**3)
        mem_subtext = f"{used_gb:.1f} GB of {total_gb:.1f} GB (Free: {avail_gb:.1f} GB)"
        self.card_memory.update_metric(snap.memory_percent, mem_subtext)

        if snap.disks:
            d0 = snap.disks[0]
            d_used = d0.used_bytes / (1024**3)
            d_total = d0.total_bytes / (1024**3)
            self.card_disk.update_metric(d0.percent, f"{d0.mountpoint} ({d_used:.0f}/{d_total:.0f} GB)")
        else:
            self.card_disk.update_metric(0.0, "No storage detected")

        # Uptime formatting
        days = int(snap.uptime_seconds // 86400)
        hours = int((snap.uptime_seconds % 86400) // 3600)
        minutes = int((snap.uptime_seconds % 3600) // 60)
        uptime_str = f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"
        self.card_uptime.set_content(uptime_str, f"{snap.total_processes} active processes")

        # 2. Update Charts
        self._point_counter += 1
        self.time_points.append(self._point_counter)
        self.cpu_history.append(snap.cpu_percent)
        self.mem_history.append(snap.memory_percent)

        x = list(range(len(self.cpu_history)))
        self.cpu_curve.setData(x, list(self.cpu_history))
        self.mem_curve.setData(x, list(self.mem_history))

        # 3. Check Warning Alerts
        alerts = []
        if snap.cpu_percent >= 90.0:
            alerts.append(f"High CPU utilization ({snap.cpu_percent:.1f}%)")
        if snap.memory_percent >= 90.0:
            alerts.append(f"High Memory consumption ({snap.memory_percent:.1f}%)")

        if alerts:
            self.alert_banner.show_alert(" & ".join(alerts))
        else:
            self.alert_banner.hide_alert()

    def update_process_data(self, processes: List[ProcessInfo]):
        """Populates Top 5 CPU and Memory tables."""
        # Top 5 CPU
        sorted_by_cpu = sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:5]
        for row, p in enumerate(sorted_by_cpu):
            self.top_cpu_table.setItem(row, 0, QTableWidgetItem(str(p.pid)))
            self.top_cpu_table.setItem(row, 1, QTableWidgetItem(p.name))
            self.top_cpu_table.setItem(row, 2, QTableWidgetItem(f"{p.cpu_percent:.1f}%"))

        # Top 5 Memory
        sorted_by_mem = sorted(processes, key=lambda p: p.memory_rss_bytes, reverse=True)[:5]
        for row, p in enumerate(sorted_by_mem):
            self.top_mem_table.setItem(row, 0, QTableWidgetItem(str(p.pid)))
            self.top_mem_table.setItem(row, 1, QTableWidgetItem(p.name))
            self.top_mem_table.setItem(row, 2, QTableWidgetItem(f"{p.memory_mb:.1f} MB"))
