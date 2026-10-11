"""Main application window: sidebar navigation, header status, and page switching."""
import time
from typing import List, Optional
from PySide6.QtCore import Qt, QThread, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.nexus.config import (
    APP_NAME,
    APP_SUBTITLE,
    DEFAULT_REFRESH_INTERVAL_MS,
)
from src.nexus.monitoring.system_monitor import SystemSnapshot
from src.nexus.monitoring.process_monitor import ProcessInfo
from src.nexus.ui.pages.overview import OverviewPage
from src.nexus.ui.pages.processes import ProcessesPage
from src.nexus.ui.pages.performance import PerformancePage
from src.nexus.ui.pages.reports import ReportsPage
from src.nexus.ui.pages.about import AboutPage
from src.nexus.ui.styles import DARK_THEME_QSS, LIGHT_THEME_QSS
from src.nexus.workers.monitor_worker import MonitorWorker
from src.nexus.utils.logging_config import setup_logger

logger = setup_logger("nexus.main_window")


class MainWindow(QMainWindow):
    """Main Application Window housing navigation, background worker lifecycle, and pages."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — {APP_SUBTITLE}")
        self.resize(1180, 780)
        self.setMinimumSize(960, 640)

        self._is_dark_theme = True
        self._monitoring_active = True

        # Initialize background QThread & Worker
        self._worker_thread = QThread()
        self._worker = MonitorWorker(DEFAULT_REFRESH_INTERVAL_MS)
        self._worker.moveToThread(self._worker_thread)

        self._init_ui()
        self._setup_worker_signals()

        # Start thread
        self._worker_thread.start()

    def _init_ui(self):
        self.setStyleSheet(DARK_THEME_QSS)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = self._build_sidebar()
        main_h_layout.addWidget(sidebar)

        # 2. Right Content Area (Header + Stacked Pages)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        header = self._build_header()
        content_layout.addWidget(header)

        # Stacked Pages
        self.stack = QStackedWidget()
        self.page_overview = OverviewPage()
        self.page_processes = ProcessesPage()
        self.page_performance = PerformancePage()
        self.page_reports = ReportsPage()
        self.page_about = AboutPage()

        self.stack.addWidget(self.page_overview)      # Index 0
        self.stack.addWidget(self.page_processes)     # Index 1
        self.stack.addWidget(self.page_performance)   # Index 2
        self.stack.addWidget(self.page_reports)       # Index 3
        self.stack.addWidget(self.page_about)         # Index 4

        content_layout.addWidget(self.stack, 1)
        main_h_layout.addWidget(content_container, 1)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("SidebarWidget")
        sidebar.setFixedWidth(220)

        vbox = QVBoxLayout(sidebar)
        vbox.setContentsMargins(16, 24, 16, 24)
        vbox.setSpacing(12)

        # App Brand Title
        brand_title = QLabel(APP_NAME)
        brand_title.setObjectName("SidebarTitle")
        vbox.addWidget(brand_title)

        brand_subtitle = QLabel("RESOURCE MONITOR")
        brand_subtitle.setObjectName("SidebarSubtitle")
        vbox.addWidget(brand_subtitle)

        vbox.addSpacing(20)

        # Navigation Buttons Group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_items = [
            ("Overview", 0),
            ("Processes", 1),
            ("Performance", 2),
            ("Reports", 3),
            ("About", 4),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "NavButton")
            btn.setCheckable(True)
            if index == 0:
                btn.setChecked(True)
            self.nav_group.addButton(btn, index)
            vbox.addWidget(btn)

        self.nav_group.idClicked.connect(self._on_nav_clicked)

        vbox.addStretch()

        # Version stamp
        v_label = QLabel("v1.0.0 Stable")
        v_label.setStyleSheet("color: #475569; font-size: 11px;")
        vbox.addWidget(v_label)

        return sidebar

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("HeaderWidget")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 10, 20, 10)

        # Section breadcrumb
        self.header_title = QLabel("Overview Dashboard")
        self.header_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F8FAFC;")
        h_layout.addWidget(self.header_title)

        h_layout.addStretch()

        # Monitoring Status Badge
        self.status_badge = QLabel("● MONITORING ACTIVE")
        self.status_badge.setObjectName("HeaderStatusBadge")
        h_layout.addWidget(self.status_badge)

        # Last updated timestamp
        self.last_update_lbl = QLabel("Last update: --:--:--")
        self.last_update_lbl.setStyleSheet("color: #64748B; font-size: 11px; margin: 0 10px;")
        h_layout.addWidget(self.last_update_lbl)

        # Start / Pause Toggle
        self.btn_toggle_monitor = QPushButton("Pause")
        self.btn_toggle_monitor.setProperty("class", "SecondaryButton")
        self.btn_toggle_monitor.clicked.connect(self._toggle_monitoring)
        h_layout.addWidget(self.btn_toggle_monitor)

        # Refresh Interval Selector
        self.interval_combo = QComboBox()
        self.interval_combo.addItem("1s Refresh", 1000)
        self.interval_combo.addItem("2s Refresh", 2000)
        self.interval_combo.addItem("5s Refresh", 5000)
        self.interval_combo.setCurrentIndex(1)  # Default 2s
        self.interval_combo.currentIndexChanged.connect(self._change_refresh_interval)
        h_layout.addWidget(self.interval_combo)

        # Theme Switcher
        self.btn_theme = QPushButton("Theme")
        self.btn_theme.setProperty("class", "SecondaryButton")
        self.btn_theme.clicked.connect(self._toggle_theme)
        h_layout.addWidget(self.btn_theme)

        return header

    def _setup_worker_signals(self):
        # Connect thread start to worker execution
        self._worker_thread.started.connect(self._worker.start_monitoring)

        # Connect worker data outputs to GUI update methods
        self._worker.system_updated.connect(self._handle_system_update)
        self._worker.processes_updated.connect(self._handle_processes_update)
        self._worker.error_occurred.connect(self._handle_worker_error)

    def _on_nav_clicked(self, page_index: int):
        self.stack.setCurrentIndex(page_index)
        titles = {
            0: "Overview Dashboard",
            1: "Processes Explorer",
            2: "Performance & Hardware Profile",
            3: "Diagnostic Reports & Exports",
            4: "About NEXUS & OS Concepts",
        }
        self.header_title.setText(titles.get(page_index, "NEXUS"))

    @Slot(object)
    def _handle_system_update(self, snap: SystemSnapshot):
        if not self._monitoring_active:
            return

        now_str = time.strftime("%H:%M:%S", time.localtime(snap.timestamp))
        self.last_update_lbl.setText(f"Last update: {now_str}")

        # Update Pages with new metrics
        self.page_overview.update_system_data(snap)
        self.page_performance.update_system_data(snap)
        self.page_reports.update_system_data(snap)

    @Slot(list)
    def _handle_processes_update(self, processes: List[ProcessInfo]):
        if not self._monitoring_active:
            return

        self.page_overview.update_process_data(processes)
        self.page_processes.update_processes(processes)
        self.page_reports.update_processes(processes)

    @Slot(str)
    def _handle_worker_error(self, err: str):
        logger.error(f"Worker report error: {err}")

    def _toggle_monitoring(self):
        self._monitoring_active = not self._monitoring_active
        if self._monitoring_active:
            self.btn_toggle_monitor.setText("Pause")
            self.status_badge.setText("● MONITORING ACTIVE")
            self.status_badge.setObjectName("HeaderStatusBadge")
            self.status_badge.setStyle(self.status_badge.style())
        else:
            self.btn_toggle_monitor.setText("Resume")
            self.status_badge.setText("■ PAUSED")
            self.status_badge.setObjectName("HeaderStatusBadgeStopped")
            self.status_badge.setStyle(self.status_badge.style())

    def _change_refresh_interval(self, index: int):
        interval = self.interval_combo.currentData()
        if interval:
            self._worker.update_interval(interval)

    def _toggle_theme(self):
        self._is_dark_theme = not self._is_dark_theme
        if self._is_dark_theme:
            self.setStyleSheet(DARK_THEME_QSS)
        else:
            self.setStyleSheet(LIGHT_THEME_QSS)

    def closeEvent(self, event):
        """Clean background thread teardown upon application exit."""
        logger.info("Application shutting down. Terminating worker thread...")
        self._worker.stop_monitoring()
        self._worker_thread.quit()
        self._worker_thread.wait(2000)
        event.accept()
