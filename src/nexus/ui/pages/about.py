"""About Page: Project overview, OS concepts demonstrated, and college team credits."""
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.nexus.config import APP_NAME, APP_SUBTITLE, APP_VERSION, APP_AUTHOR


class AboutPage(QWidget):
    """Academic project documentation, OS concepts overview, and architecture guide."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(18)

        # Title Card
        title_card = QFrame()
        title_card.setProperty("class", "MetricCard")
        t_box = QVBoxLayout(title_card)

        app_title = QLabel(f"{APP_NAME} — {APP_SUBTITLE}")
        app_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #38BDF8;")
        t_box.addWidget(app_title)

        version_lbl = QLabel(f"Version {APP_VERSION}  |  Operating Systems Engineering Project  |  {APP_AUTHOR}")
        version_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        t_box.addWidget(version_lbl)
        layout.addWidget(title_card)

        # Core Concepts Demonstrated
        concepts_card = QFrame()
        concepts_card.setProperty("class", "MetricCard")
        c_box = QVBoxLayout(concepts_card)
        c_title = QLabel("OPERATING SYSTEM CONCEPTS DEMONSTRATED")
        c_title.setProperty("class", "CardTitle")
        c_box.addWidget(c_title)

        concepts_text = (
            "<b>1. Process Management & Process Control Blocks (PCB):</b><br>"
            "Demonstrates process discovery via PID, CPU scheduling utilization metrics, process states (running, sleeping, idle), "
            "and thread counts using kernel API hooks.<br><br>"
            "<b>2. Safe Process Inter-Communication & Termination:</b><br>"
            "Safe lifecycle termination adhering to strict OS protection policies. Restricts termination of PID 0, PID 1, "
            "and essential kernel/subsystem processes (e.g., csrss.exe, systemd).<br><br>"
            "<b>3. Virtual Memory Management:</b><br>"
            "Tracking of physical RAM, Resident Set Size (RSS), Virtual Memory Size (VMS), and page swap file utilization.<br><br>"
            "<b>4. Multithreading & Asynchronous Concurrency:</b><br>"
            "Decouples heavy system kernel telemetry polling from the graphical user interface event loop via Qt QThread workers, "
            "ensuring 60 FPS UI responsiveness without deadlocks."
        )
        c_desc = QLabel(concepts_text)
        c_desc.setTextFormat(Qt.RichText)
        c_desc.setWordWrap(True)
        c_desc.setStyleSheet("color: #E2E8F0; line-height: 1.5; font-size: 13px;")
        c_box.addWidget(c_desc)
        layout.addWidget(concepts_card)

        # Technical Architecture Card
        tech_card = QFrame()
        tech_card.setProperty("class", "MetricCard")
        tech_box = QVBoxLayout(tech_card)
        tech_title = QLabel("TECHNOLOGY STACK & RUNTIME ARCHITECTURE")
        tech_title.setProperty("class", "CardTitle")
        tech_box.addWidget(tech_title)

        tech_desc = QLabel(
            "• <b>Python 3.11+:</b> Core application logic, typing annotations, and structured dataclasses.<br>"
            "• <b>PySide6 (Qt for Python):</b> Native desktop user interface architecture.<br>"
            "• <b>psutil:</b> Cross-platform hardware telemetry and system process abstraction.<br>"
            "• <b>pyqtgraph:</b> High-performance GPU/CPU accelerated charting engine with 60Hz updates.<br>"
            "• <b>pytest:</b> Automated testing suite with mock hardware abstraction fixtures."
        )
        tech_desc.setTextFormat(Qt.RichText)
        tech_desc.setWordWrap(True)
        tech_desc.setStyleSheet("color: #E2E8F0; line-height: 1.5; font-size: 13px;")
        tech_box.addWidget(tech_desc)
        layout.addWidget(tech_card)

        # Student Notes / Viva Tips
        viva_card = QFrame()
        viva_card.setProperty("class", "MetricCard")
        viva_box = QVBoxLayout(viva_card)
        viva_title = QLabel("PROJECT DEFENSE & VIVA PREPARATION")
        viva_title.setProperty("class", "CardTitle")
        viva_box.addWidget(viva_title)

        viva_desc = QLabel(
            "<b>Key Exam Question:</b> Why does the initial process CPU reading register 0%?<br>"
            "<i>Answer:</i> CPU percentage is a rate measurement comparing the difference in CPU execution time "
            "between two discrete ticks against elapsed wall-clock time. The first sample establishes the baseline.<br><br>"
            "<b>Key Exam Question:</b> Why can't a normal user terminate every process?<br>"
            "<i>Answer:</i> Modern OS kernels enforce Discretionary Access Control (DAC) and privilege rings. "
            "Processes executing under SYSTEM/root or critical session managers cannot be terminated by unprivileged user tokens."
        )
        viva_desc.setTextFormat(Qt.RichText)
        viva_desc.setWordWrap(True)
        viva_desc.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.4;")
        viva_box.addWidget(viva_desc)
        layout.addWidget(viva_card)

        scroll.setWidget(container)

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
