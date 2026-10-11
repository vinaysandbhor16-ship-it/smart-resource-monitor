"""Application configuration and constants for NEXUS Resource Monitor."""
from dataclasses import dataclass
from pathlib import Path
import sys

APP_NAME = "NEXUS"
APP_SUBTITLE = "Smart Resource Monitor & Process Manager"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Engineering OS Team"

# Refresh and Monitoring Defaults
DEFAULT_REFRESH_INTERVAL_MS = 2000  # 2.0 seconds
MIN_REFRESH_INTERVAL_MS = 1000      # 1.0 second
MAX_REFRESH_INTERVAL_MS = 10000     # 10.0 seconds
HISTORY_BUFFER_MAX_POINTS = 60      # Keep last 60 measurements (e.g., 2 mins at 2s interval)

# Alert Thresholds (percentages)
DEFAULT_CPU_WARNING_THRESHOLD = 85.0
DEFAULT_MEM_WARNING_THRESHOLD = 90.0

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Process Protection List (Platform-aware conservative critical list)
PROTECTED_PID_LIST = {0, 1}

# Known Windows system critical process names (lowercase)
WINDOWS_CRITICAL_PROCESSES = {
    "system",
    "system idle process",
    "registry",
    "smss.exe",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "svchost.exe",
    "winlogon.exe",
    "explorer.exe",
    "dwm.exe",
    "fontdrvhost.exe"
}

# Known Linux system critical process names
LINUX_CRITICAL_PROCESSES = {
    "systemd",
    "init",
    "kthreadd",
    "systemd-journald",
    "systemd-udevd",
    "dbus-daemon",
    "sshd",
    "bash",
    "sh"
}
