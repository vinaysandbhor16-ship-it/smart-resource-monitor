"""Reusable custom Qt widgets for NEXUS (Cards, Badges, Alert Banners)."""
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class MetricCard(QFrame):
    """Clean card displaying a key hardware/resource metric."""

    def __init__(self, title: str, unit: str = "%", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setProperty("class", "MetricCard")
        self.unit = unit

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Header: Title
        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "CardTitle")
        layout.addWidget(self.title_label)

        # Main Value
        self.value_label = QLabel(f"0.0{self.unit}")
        self.value_label.setProperty("class", "CardValue")
        layout.addWidget(self.value_label)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

        # Subtitle / detail
        self.subtext_label = QLabel("Initializing...")
        self.subtext_label.setProperty("class", "CardSubtext")
        layout.addWidget(self.subtext_label)

    def update_metric(self, value: float, subtext: str = "", max_val: float = 100.0):
        """Updates numeric value and progress visualization."""
        if self.unit == "%":
            self.value_label.setText(f"{value:.1f}%")
            self.progress.setValue(int(min(100, max(0, value))))
        else:
            self.value_label.setText(f"{value:.1f} {self.unit}")
            pct = int((value / max_val) * 100) if max_val > 0 else 0
            self.progress.setValue(min(100, max(0, pct)))

        if subtext:
            self.subtext_label.setText(subtext)


class InfoStatCard(QFrame):
    """Textual summary card for system properties (e.g. Uptime, OS, Cores)."""

    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setProperty("class", "MetricCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "CardTitle")
        layout.addWidget(self.title_label)

        self.value_label = QLabel("—")
        self.value_label.setProperty("class", "CardValue")
        self.value_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(self.value_label)

        self.subtext_label = QLabel("")
        self.subtext_label.setProperty("class", "CardSubtext")
        layout.addWidget(self.subtext_label)

    def set_content(self, value: str, subtext: str = ""):
        self.value_label.setText(value)
        self.subtext_label.setText(subtext)


class AlertBanner(QFrame):
    """Warning banner shown at the top of pages when resources exceed critical thresholds."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setVisible(False)
        self.setStyleSheet("""
            QFrame {
                background-color: #450A0A;
                border: 1px solid #DC2626;
                border-radius: 8px;
                padding: 10px 16px;
            }
            QLabel {
                color: #FECACA;
                font-weight: 600;
                font-size: 13px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        self.icon_label = QLabel("ALERT:")
        self.icon_label.setStyleSheet("color: #F87171; font-weight: 800;")
        self.message_label = QLabel("High resource consumption detected.")
        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label, 1)

    def show_alert(self, message: str):
        self.message_label.setText(message)
        self.setVisible(True)

    def hide_alert(self):
        self.setVisible(False)
