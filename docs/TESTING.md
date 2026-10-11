# Testing Guide & Quality Assurance

This document details automated and manual testing strategies for NEXUS.

## 1. Automated Unit & Integration Tests

The test suite is built on `pytest` and mocks hardware-level anomalies to ensure stability.

### Running Automated Tests:

```bash
python -m pytest -v
```

### Test Suite Coverage:
- `tests/test_system_monitor.py`: Validates non-negative metric ranges, core counts, and simulates permission denied or unsupported hardware gracefully.
- `tests/test_process_monitor.py`: Verifies process enumeration, safety policies (PID 0, PID 1, system critical files), and safe termination safeguards.
- `tests/test_export_service.py`: Validates CSV and JSON output integrity with temporary directories.

---

## 2. Manual Verification Checklist

| Test Item | Steps | Expected Result |
| :--- | :--- | :--- |
| **App Launch** | Run `python main.py` | UI opens cleanly on Overview Page in dark mode at 60 FPS. |
| **Real-time Graphs** | Observe CPU & Memory graphs | Blue & Indigo graphs update periodically every 2 seconds without flickering. |
| **Process Table Sorting**| Click "CPU (%)" or "RAM (MB)" column | Table sorts rows in descending/ascending order smoothly. |
| **Process Search** | Type "python" or a specific PID in search bar | Rows dynamically filter instantaneously. |
| **Process Detail Inspection** | Select a process and click "Inspect Details" | Modal dialog appears showing VMS, RSS, thread counts, and started timestamp. |
| **Safe Process Termination** | Select a safe test process or attempt to terminate PID 0 | Protected process triggers a warning dialog blocking termination. Valid user processes ask for confirmation before SIGTERM. |
| **CSV Export** | Navigate to Reports -> "Export Processes to CSV" | Save file dialog opens; CSV writes correctly; status banner updates to green. |
| **JSON Export** | Navigate to Reports -> "Export System Summary to JSON" | Save file dialog opens; JSON writes hardware tree accurately. |
| **Theme Toggle** | Click "Theme" button in the top right | Color scheme toggles between high-contrast dark theme and crisp light theme. |
| **Pause/Resume** | Click "Pause" / "Resume" in top header | Telemetry polling pauses; status badge changes to red paused indicator; restarts upon resume. |
| **Clean Exit** | Close the window | Background `QThread` safely stops without orphan processes or hanging threads. |
