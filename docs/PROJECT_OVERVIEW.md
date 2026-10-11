# NEXUS — Project Overview

## Academic Context
- **Course:** Operating Systems Laboratory / Theory
- **Target Audience:** Engineering Students, Faculty Evaluators, System Administrators
- **Objective:** Bridge core theoretical concepts (scheduling, process control blocks, virtual memory, concurrency, signals) with an intuitive real-world desktop tool.

## Key Highlights
1. **True Native Telemetry:** Uses native kernel APIs (`psutil`) rather than simulated data.
2. **Crash-Resilient Design:** Completely handles inaccessible system processes, permissions (`AccessDenied`), and zombie processes.
3. **Decoupled Architecture:** Asynchronous worker threads keep the user interface smooth and responsive.
4. **Safety-First Process Control:** Restricts accidental disruption of kernel/OS processes while providing safe user management.
