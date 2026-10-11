# System Architecture & Technical Design

NEXUS is designed around modularity, separation of concerns, and thread safety.

```mermaid
flowchart TD
    subgraph BackgroundWorker ["Background Worker (QThread)"]
        Worker["MonitorWorker"]
        SysMon["SystemMonitor (psutil)"]
        ProcMon["ProcessMonitor (psutil)"]
        Worker --> SysMon
        Worker --> ProcMon
    end

    subgraph DataExchange ["Qt Signal/Slot Inter-Thread Messaging"]
        SigSys["Signal: system_updated(SystemSnapshot)"]
        SigProc["Signal: processes_updated(List[ProcessInfo])"]
        Worker --> SigSys
        Worker --> SigProc
    end

    subgraph UserInterface ["Main GUI Thread (PySide6)"]
        MW["MainWindow"]
        Nav["Sidebar Navigation"]
        Stack["QStackedWidget Pages"]
        
        PageOverview["OverviewPage (Real-time Cards & Charts)"]
        PageProcs["ProcessesPage (Table, Filter, Details, Terminate)"]
        PagePerf["PerformancePage (Multi-disk, Network)"]
        PageReports["ReportsPage (CSV & JSON Exporter)"]
        PageAbout["AboutPage (OS Principles & Viva Q&A)"]
        
        MW --> Nav
        MW --> Stack
        Stack --> PageOverview
        Stack --> PageProcs
        Stack --> PagePerf
        Stack --> PageReports
        Stack --> PageAbout
    end

    SigSys --> MW
    SigProc --> MW

    subgraph Storage ["Services & Exports"]
        ExportService["ExportService (CSV / JSON)"]
        PageReports --> ExportService
    end
```

## Architectural Principles

1. **Separation of Presentation & Telemetry:** 
   The telemetry layer (`src/nexus/monitoring`) has zero Qt dependencies, allowing comprehensive automated testing via `pytest` without a desktop display or mock GUI.
2. **Thread Safety via Signal/Slot:**
   Background worker threads never touch UI widgets directly. All communication is performed using thread-safe Qt Signals with copy-on-write Python dataclasses (`SystemSnapshot`, `ProcessInfo`).
3. **Bounded Memory Profile:**
   Chart series are backed by collections with bounded deques (`collections.deque(maxlen=60)`), preventing memory leaks during indefinite monitoring runs.
4. **Resilient Exception Isolation:**
   Platform-specific hardware queries and restricted kernel processes (e.g. `psutil.AccessDenied`) are caught and logged without propagating crashes to the UI.
