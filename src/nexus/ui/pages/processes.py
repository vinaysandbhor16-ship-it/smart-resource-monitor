"""Processes Explorer Page: Search, sort, inspect, and safely manage running processes."""
import time
from typing import Dict, List, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.nexus.monitoring.process_monitor import ProcessInfo, ProcessMonitor
from src.nexus.utils.logging_config import setup_logger

logger = setup_logger("nexus.processes_page")


class ProcessDetailDialog(QDialog):
    """Clean detail inspection dialog for a selected process."""

    def __init__(self, proc: ProcessInfo, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(f"Process Details — {proc.name} (PID: {proc.pid})")
        self.resize(560, 420)
        self._init_ui(proc)

    def _init_ui(self, proc: ProcessInfo):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header card
        header_card = QFrame()
        header_card.setProperty("class", "MetricCard")
        h_box = QVBoxLayout(header_card)

        name_lbl = QLabel(f"{proc.name}")
        name_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
        h_box.addWidget(name_lbl)

        pid_lbl = QLabel(f"PID: {proc.pid}  |  Status: {proc.status}  |  User: {proc.username}")
        pid_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        h_box.addWidget(pid_lbl)
        layout.addWidget(header_card)

        # Details table/list
        details_frame = QFrame()
        details_frame.setProperty("class", "MetricCard")
        d_box = QVBoxLayout(details_frame)
        d_box.setSpacing(8)

        created_str = (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(proc.create_time))
            if proc.create_time > 0
            else "Unavailable"
        )

        rows = [
            ("CPU Consumption:", f"{proc.cpu_percent:.1f}%"),
            ("RAM Usage (RSS):", f"{proc.memory_mb:.1f} MB ({proc.memory_percent:.1f}%)"),
            ("Virtual Memory (VMS):", f"{proc.memory_vms_bytes / (1024*1024):.1f} MB"),
            ("Active Threads:", f"{proc.num_threads}"),
            ("Started At:", created_str),
            ("OS Protected Policy:", "Yes (System Critical)" if proc.is_protected else "No (User Accessible)"),
            ("Executable Path:", proc.exe_path),
        ]

        for label, val in rows:
            row_layout = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("font-weight: 600; color: #94A3B8; width: 140px;")
            val_lbl = QLabel(str(val))
            val_lbl.setWordWrap(True)
            val_lbl.setStyleSheet("color: #F8FAFC;")
            row_layout.addWidget(lbl, 1)
            row_layout.addWidget(val_lbl, 2)
            d_box.addLayout(row_layout)

        layout.addWidget(details_frame)

        # Close button
        btn_box = QDialogButtonBox(QDialogButtonBox.Close)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)


class ProcessesPage(QWidget):
    """Processes table with search, sorting, inspection, and safe termination."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.process_monitor = ProcessMonitor()
        self.all_processes: List[ProcessInfo] = []
        self._sort_column = 2  # Default sort by CPU %
        self._sort_ascending = False

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Action Bar (Search, Controls, Process count)
        action_bar = QHBoxLayout()
        action_bar.setSpacing(10)

        # Search field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter processes by Name or PID...")
        self.search_input.textChanged.connect(self._apply_filter)
        action_bar.addWidget(self.search_input, 2)

        # Process Count
        self.count_label = QLabel("0 processes")
        self.count_label.setStyleSheet("color: #94A3B8; font-weight: 600; padding: 0 10px;")
        action_bar.addWidget(self.count_label)

        # Inspect Button
        self.btn_inspect = QPushButton("Inspect Details")
        self.btn_inspect.setProperty("class", "SecondaryButton")
        self.btn_inspect.clicked.connect(self._inspect_selected)
        action_bar.addWidget(self.btn_inspect)

        # Safe Terminate Button
        self.btn_terminate = QPushButton("End Process")
        self.btn_terminate.setProperty("class", "DangerButton")
        self.btn_terminate.clicked.connect(self._terminate_selected)
        action_bar.addWidget(self.btn_terminate)

        layout.addLayout(action_bar)

        # Processes Table
        self.table = QTableWidget()
        self.headers = ["PID", "Process Name", "CPU (%)", "Memory (%)", "RAM (MB)", "Status", "User", "Threads"]
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self._inspect_selected)

        # Enable click header sorting
        self.table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)

        layout.addWidget(self.table)

    def update_processes(self, processes: List[ProcessInfo]):
        """Receives updated process snapshot from worker thread."""
        self.all_processes = processes
        self._apply_filter()

    def _on_header_clicked(self, col: int):
        """Toggle sort order on header click."""
        if self._sort_column == col:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_column = col
            self._sort_ascending = False
        self._apply_filter()

    def _apply_filter(self):
        """Filters by search text and applies sort criteria."""
        query = self.search_input.text().strip().lower()
        filtered = []

        for p in self.all_processes:
            if not query or query in p.name.lower() or query in str(p.pid):
                filtered.append(p)

        # Sort filtered list
        def sort_key(p: ProcessInfo):
            if self._sort_column == 0:
                return p.pid
            elif self._sort_column == 1:
                return p.name.lower()
            elif self._sort_column == 2:
                return p.cpu_percent
            elif self._sort_column == 3:
                return p.memory_percent
            elif self._sort_column == 4:
                return p.memory_rss_bytes
            elif self._sort_column == 5:
                return p.status
            elif self._sort_column == 6:
                return p.username
            elif self._sort_column == 7:
                return p.num_threads
            return p.pid

        filtered.sort(key=sort_key, reverse=not self._sort_ascending)

        # Populate table
        self.count_label.setText(f"{len(filtered)} of {len(self.all_processes)} processes")
        
        # Save current selected PID to preserve selection across refreshes
        selected_pid = self._get_selected_pid()

        self.table.setRowCount(len(filtered))
        for row, p in enumerate(filtered):
            item_pid = QTableWidgetItem(str(p.pid))
            item_pid.setData(Qt.UserRole, p.pid)
            item_name = QTableWidgetItem(p.name)
            item_cpu = QTableWidgetItem(f"{p.cpu_percent:.1f}%")
            item_mempct = QTableWidgetItem(f"{p.memory_percent:.1f}%")
            item_memmb = QTableWidgetItem(f"{p.memory_mb:.1f}")
            item_status = QTableWidgetItem(p.status)
            item_user = QTableWidgetItem(p.username)
            item_threads = QTableWidgetItem(str(p.num_threads))

            self.table.setItem(row, 0, item_pid)
            self.table.setItem(row, 1, item_name)
            self.table.setItem(row, 2, item_cpu)
            self.table.setItem(row, 3, item_mempct)
            self.table.setItem(row, 4, item_memmb)
            self.table.setItem(row, 5, item_status)
            self.table.setItem(row, 6, item_user)
            self.table.setItem(row, 7, item_threads)

            if selected_pid and p.pid == selected_pid:
                self.table.selectRow(row)

    def _get_selected_pid(self) -> Optional[int]:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        item = self.table.item(row, 0)
        if item:
            try:
                return int(item.text())
            except ValueError:
                return None
        return None

    def _get_selected_process(self) -> Optional[ProcessInfo]:
        pid = self._get_selected_pid()
        if pid is None:
            return None
        for p in self.all_processes:
            if p.pid == pid:
                return p
        return None

    def _inspect_selected(self):
        """Opens inspection dialog for selected process."""
        proc = self._get_selected_process()
        if not proc:
            QMessageBox.information(self, "No Selection", "Please select a process from the table to inspect.")
            return

        dialog = ProcessDetailDialog(proc, self)
        dialog.exec()

    def _terminate_selected(self):
        """Safely guides the user through process termination confirmation."""
        proc = self._get_selected_process()
        if not proc:
            QMessageBox.information(self, "No Selection", "Please select a process to terminate.")
            return

        # Check safety policy
        is_protected, reason = self.process_monitor.is_protected_process(proc.pid, proc.name)
        if is_protected:
            QMessageBox.warning(
                self,
                "Action Blocked — System Safety Policy",
                f"Cannot terminate process '{proc.name}' (PID: {proc.pid}).\n\nReason: {reason}",
            )
            return

        # Mandatory confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Process Termination",
            f"Are you sure you want to terminate the following process?\n\n"
            f"• Name: {proc.name}\n"
            f"• PID: {proc.pid}\n"
            f"• Memory: {proc.memory_mb:.1f} MB\n\n"
            "Unsaved work in that program may be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        success, msg = self.process_monitor.terminate_process(proc.pid)
        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.warning(self, "Termination Notice", msg)
