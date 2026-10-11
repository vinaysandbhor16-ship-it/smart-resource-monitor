# Operating Systems Engineering Concepts in NEXUS

NEXUS was designed as an applied software project demonstrating fundamental theoretical principles taught in undergraduate Operating Systems courses.

---

## 1. Process Management & The Process Control Block (PCB)

In modern operating systems, a process is an active instance of a computer program in execution. The operating system kernel represents each process through a data structure known as the **Process Control Block (PCB)**.

In NEXUS, each row in the **Processes Explorer** directly maps to properties stored in the kernel PCB:
- **Process ID (PID):** A unique numerical identifier assigned by the operating system scheduler.
- **Process State:** The execution phase of the process (`running`, `sleeping`, `zombie`, `stopped`).
- **Memory Footprint:** 
  - **Resident Set Size (RSS):** Physical RAM pages currently assigned and resident in main memory.
  - **Virtual Memory Size (VMS):** Total address space mapped by the process, including swapped-out virtual memory pages.
- **Execution Threads:** The number of independent execution streams sharing the process memory space.

---

## 2. CPU Utilization & Time-Delta Computation

Operating systems do not report CPU percentage as a static instantaneous scalar. Instead, CPU usage is calculated across discrete intervals:

$$\text{CPU Utilization} = \frac{\Delta t_{\text{kernel}} + \Delta t_{\text{user}}}{\Delta t_{\text{total\_elapsed}}} \times 100\%$$

### Why is the initial process reading 0% or unavailable?
When an OS monitor initializes, it reads the cumulative CPU execution ticks for each PID. Because a single snapshot has no prior baseline to calculate $\Delta t$, the rate of work done cannot yet be determined. On the second iteration, the delta is divided by the time elapsed between polls to calculate real CPU utilization.

---

## 3. Safe Process Termination & Privilege Rings

Modern microprocessors and operating systems enforce security rings:
- **Ring 0 (Kernel Mode):** Unrestricted access to hardware and instructions.
- **Ring 3 (User Mode):** Restricted access; processes cannot interfere with other processes or essential system services without explicit authorization.

### Protection Architecture in NEXUS:
NEXUS implements a conservative, platform-aware safety policy:
1. **PID 0:** Kernel / System Idle Process (cannot and must not be terminated).
2. **PID 1:** Init / `systemd` (Linux system root process).
3. **System-Critical Subsystems:** Protects vital Windows processes (`csrss.exe`, `services.exe`, `smss.exe`, `dwm.exe`, `explorer.exe`).
4. **Self-Termination Prevention:** NEXUS checks `os.getpid()` to prevent accidental termination of itself.
5. **Graceful Signals:** Terminations request `SIGTERM` (graceful cleanup) rather than an instantaneous forceful `SIGKILL`.

---

## 4. Virtual Memory Management & Page Swapping

Operating systems utilize paging and virtual memory to allocate more memory than physically exists in hardware.
- **Paging:** Memory pages (typically 4 KB) are moved between RAM and storage (Pagefile on Windows or Swap partition on Linux).
- NEXUS provides visibility into physical RAM vs. swap allocation, helping diagnose thrashing before memory exhaustion occurs.

---

## 5. Non-Blocking Concurrency (GUI Threading vs. Kernel Polling)

Operating system graphical user interfaces run an event loop (e.g. Qt Event Loop) that executes at ~60 frames per second. If system calls like `psutil.process_iter()` (which may inspect hundreds of PIDs and query kernel status) are executed on the main UI thread, the interface will freeze.

NEXUS solves this by executing telemetry polling inside a separate background thread (`QThread` with `MonitorWorker`), communicating with the UI strictly via asynchronous message passing (`Qt Signals and Slots`).
