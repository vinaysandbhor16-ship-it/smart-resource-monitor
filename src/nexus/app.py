"""Application bootstrapper and lifecycle manager for NEXUS."""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.nexus.ui.main_window import MainWindow
from src.nexus.utils.logging_config import setup_logger

logger = setup_logger("nexus.app")


def create_app() -> QApplication:
    """Initializes QApplication with high-DPI scaling and metadata."""
    # Qt High-DPI support is enabled by default in Qt6
    app = QApplication(sys.argv)
    app.setApplicationName("NEXUS")
    app.setOrganizationName("NexusEngineering")
    return app


def run() -> int:
    """Main execution entry point."""
    logger.info("Initializing NEXUS Resource Monitor...")
    app = create_app()
    window = MainWindow()
    window.show()
    return app.exec()
