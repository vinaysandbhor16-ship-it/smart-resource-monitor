"""Reports Page: Export processes to CSV and system telemetry snapshots to JSON."""
import time
from typing import List, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.nexus.monitoring.system_monitor import SystemSnapshot
from src.nexus.monitoring.process_monitor import ProcessInfo
from src.nexus.services.export_service import ExportService
from src.nexus.utils.logging_config import setup_logger

logger = setup_logger("nexus.reports_page")


class ReportsPage(QWidget):
    """Provides user-driven CSV and JSON diagnostic export utilities."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_snapshot: Optional[SystemSnapshot] = None
        self._current_processes: List[ProcessInfo] = []

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # Header description
        desc_frame = QFrame()
        desc_frame.setProperty("class", "MetricCard")
        desc_box = QVBoxLayout(desc_frame)
        title = QLabel("SYSTEM REPORTS & DIAGNOSTIC EXPORTS")
        title.setProperty("class", "CardTitle")
        desc_box.addWidget(title)

        desc_lbl = QLabel(
            "Generate localized diagnostic snapshots without external telemetry or data transmission. "
            "Export running processes to tabular CSV or system specifications to structured JSON."
        )
        desc_lbl.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.4;")
        desc_lbl.setWordWrap(True)
        desc_box.addWidget(desc_lbl)
        layout.addWidget(desc_frame)

        # Export Cards Layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        # 1. Process List CSV Export Card
        csv_card = QFrame()
        csv_card.setProperty("class", "MetricCard")
        c_box = QVBoxLayout(csv_card)
        c_box.setSpacing(10)

        c_title = QLabel("PROCESS LIST EXPORT (CSV)")
        c_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #38BDF8;")
        c_box.addWidget(c_title)

        c_desc = QLabel(
            "Exports the current list of accessible processes including PID, name, "
            "CPU usage, memory consumption, execution status, and active threads."
        )
        c_desc.setStyleSheet("color: #94A3B8;")
        c_desc.setWordWrap(True)
        c_box.addWidget(c_desc)

        self.btn_export_csv = QPushButton("Export Processes to CSV")
        self.btn_export_csv.setProperty("class", "PrimaryButton")
        self.btn_export_csv.clicked.connect(self._handle_export_csv)
        c_box.addWidget(self.btn_export_csv)
        cards_layout.addWidget(csv_card, 1)

        # 2. System Hardware Summary JSON Export Card
        json_card = QFrame()
        json_card.setProperty("class", "MetricCard")
        j_box = QVBoxLayout(json_card)
        j_box.setSpacing(10)

        j_title = QLabel("SYSTEM HARDWARE SNAPSHOT (JSON)")
        j_title.setStyleSheet("font-weight: bold; font-size: 15px; color: #818CF8;")
        j_box.addWidget(j_title)

        j_desc = QLabel(
            "Exports comprehensive hardware diagnostics, multi-core CPU metrics, "
            "virtual and swap memory allocation, storage partitions, and network statistics."
        )
        j_desc.setStyleSheet("color: #94A3B8;")
        j_desc.setWordWrap(True)
        j_box.addWidget(j_desc)

        self.btn_export_json = QPushButton("Export System Summary to JSON")
        self.btn_export_json.setProperty("class", "PrimaryButton")
        self.btn_export_json.clicked.connect(self._handle_export_json)
        j_box.addWidget(self.btn_export_json)
        cards_layout.addWidget(json_card, 1)

        layout.addLayout(cards_layout)

        # Export Log / Status Indicator
        self.status_card = QFrame()
        self.status_card.setProperty("class", "MetricCard")
        s_box = QVBoxLayout(self.status_card)
        s_title = QLabel("RECENT EXPORT ACTIVITY")
        s_title.setProperty("class", "CardTitle")
        s_box.addWidget(s_title)

        self.status_lbl = QLabel("No export generated yet during this session.")
        self.status_lbl.setStyleSheet("color: #64748B; font-style: italic;")
        s_box.addWidget(self.status_lbl)
        layout.addWidget(self.status_card)

        layout.addStretch()

    def update_system_data(self, snap: SystemSnapshot):
        self._current_snapshot = snap

    def update_processes(self, processes: List[ProcessInfo]):
        self._current_processes = processes

    def _handle_export_csv(self):
        if not self._current_processes:
            QMessageBox.warning(self, "Export Notice", "No process metrics have been collected yet.")
            return

        default_name = f"nexus_processes_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Processes to CSV", default_name, "CSV Files (*.csv)"
        )
        if not filepath:
            return

        try:
            ExportService.export_processes_to_csv(filepath, self._current_processes)
            msg = f"Successfully exported {len(self._current_processes)} processes to {filepath}"
            self.status_lbl.setText(f"✓ {msg}")
            self.status_lbl.setStyleSheet("color: #34D399; font-weight: 600;")
            QMessageBox.information(self, "Export Complete", msg)
        except Exception as exc:
            self.status_lbl.setText(f"✗ Failed to write CSV: {exc}")
            self.status_lbl.setStyleSheet("color: #F87171; font-weight: 600;")
            QMessageBox.critical(self, "Export Failed", f"Could not write file:\n{exc}")

    def _handle_export_json(self):
        if not self._current_snapshot:
            QMessageBox.warning(self, "Export Notice", "No system metrics snapshot available yet.")
            return

        default_name = f"nexus_system_summary_{time.strftime('%Y%m%d_%H%M%S')}.json"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save System Summary to JSON", default_name, "JSON Files (*.json)"
        )
        if not filepath:
            return

        try:
            ExportService.export_system_summary_to_json(filepath, self._current_snapshot)
            msg = f"Successfully exported system hardware summary to {filepath}"
            self.status_lbl.setText(f"✓ {msg}")
            self.status_lbl.setStyleSheet("color: #34D399; font-weight: 600;")
            QMessageBox.information(self, "Export Complete", msg)
        except Exception as exc:
            self.status_lbl.setText(f"✗ Failed to write JSON: {exc}")
            self.status_lbl.setStyleSheet("color: #F87171; font-weight: 600;")
            QMessageBox.critical(self, "Export Failed", f"Could not write file:\n{exc}")
