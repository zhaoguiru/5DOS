Five-Dimensional Operating System Probe (5DOS)

A cross-platform process health diagnosis framework that unifies Windows and Linux process metrics into a single, comparable synergy coefficient.

Python 3.8+ | MIT License | Windows & Linux | DOI: 10.5281/zenodo.20376185

Overview

Traditional monitoring tools (top, htop, Windows Task Manager) rely on single-dimensional thresholds such as CPU > 80% or memory > 400 MB. They fail to detect complex pathologies like "sufficient memory but handle leakage" or "idle CPU but exploding context switches."

Five-Dimensional Operating System Probe (5DOS) maps every OS process into five dimensions—Boundary (B), Structure (S), Reserve (R), Direction (D), and Intensity (I)—and computes internal/external synergy coefficients to quantify process health. This enables cross-platform diagnosis without rewriting threshold rules per OS.

Core Formula

Internal Synergy Coefficient sigma measures five-dimensional balance via ten pairwise matching degrees:
sigma = product of (1 - |x_i - x_j|) for all 1<=i<j<=5

External Synergy Coefficient k measures deviation from the system baseline:
k = k_dir^0.20 * k_B^0.20 * k_S^0.20 * k_R^0.20 * k_I^0.20

Energy Level E reflects process scale, independent of synergy:
E = (product of max(v_d, 0.01) for d=1 to 5)^0.2

Detailed theoretical foundations are available in the 5D-ST preprint:
Zenodo DOI 10.5281/zenodo.19925248

Five Dimensions

Dimension B (Boundary):
Windows: VMS + num_handles() + connections
Linux: VMS + num_fds + connections

Dimension S (Structure):
Windows & Linux: threads + children

Dimension R (Reserve):
Windows & Linux: CPU% + RSS + IO

Dimension D (Direction):
Windows: Priority class (Realtime=100, High=80, Normal=50, Idle=20)
Linux: nice value mapped to [0,100]

Dimension I (Intensity):
Windows & Linux: ln(1 + delta_ctx/delta_t + delta_cpu/delta_t)

Installation

Windows:
pip install psutil PyQt5 matplotlib numpy
python 5DOS_probe.py

Linux:
sudo apt install python3-pyqt5 python3-matplotlib python3-numpy python3-psutil
python3 5DOS_probe.py

Quick Start

Step 1: Run the probe.
python 5DOS_probe.py

Step 2: Observe the real-time terminal output.

Example output:
PID    NAME          B      S      R      D      I      sigma  k      E      TAG
1234   python3      0.12   0.05   0.80   0.50   0.03   0.042  0.612  45.2   [ALERT]
5678   systemd      0.01   0.02   0.00   0.50   0.01   0.291  0.884  12.1   [HEALTHY]

Step 3: Identify bottlenecks.
- sigma < 0.1  means dimensional imbalance detected
- TAG = [ALERT] means high-scale, low-synergy process requiring attention
- Bottleneck = BR means Boundary-Reserve mismatch (e.g., large memory footprint but low actual CPU/IO usage)

Interpreting Output

Field: sigma
Meaning: Internal synergy (10 pairwise matching degrees)
Rule: < 0.1 triggers [ALERT]

Field: k
Meaning: External synergy (deviation from system median)
Rule: < 0.5 triggers warning

Field: E
Meaning: Energy level (process scale)
Rule: > 50 means large-scale process

Field: TAG
Meaning: Health classification
Values: [HEALTHY] / [NORMAL] / [ALERT] / [SICK]

Field: Bottleneck
Meaning: Weakest dimension pair
Example: BR = Boundary-Reserve imbalance

Why 5DOS? — Real-World Scenarios

Scenario 1: Zombie Spawn Detection
A parent process forks 200 child processes and exits without calling wait().
- htop: Parent shows CPU 0%, MEM 12 MB, appears healthy.
- 5DOS: Flags [ALERT] with sigma = 0.003, bottleneck SI (Structure-Intensity decoupling), revealing the zombie swarm invisible to resource thresholds.

Scenario 2: Handle Leak on Windows
A background service leaks file handles at 50/sec.
- htop / Resource Monitor: Memory stays below 200 MB, shows green.
- 5DOS: Detects Boundary (B) inflating to 0.95 while Reserve (R) lags at 0.02; BR matching degree collapses to 0.03, triggering [ALERT] 6 seconds before the 300-handle threshold is reached.

Scenario 3: CPU Burst vs. Idle Process
A child process loops intensive computation but averages below 80% CPU over a 2-second window.
- htop rule (CPU > 80%): Fails to trigger (F1 = 0).
- 5DOS: sigma drops below threshold within 1.1 seconds due to Intensity-Reserve imbalance, 100% recall.

Screenshot
![5DOS Probe v1.0 running on Windows 11](monitor.jpg)
5DOS Probe v1.0 running on Windows 11
The GUI dashboard shows:
- Left panel: real-time process table with PID, five-dimensional vector, sigma, k, E, and health tags
- Right panel: radar charts and time-series plots for selected processes

Features

- Cross-platform native adaptation: Unified diagnosis across Windows (handles, priority classes) and Linux (file descriptors, nice values).
- Real-time 5D radar: Visualize the five-dimensional state of any selected process.
- kappa trend tracking: Historical curves of synergy coefficients.
- System health gauge: Global average sigma with color-coded alerts.
- Decomposition diagnosis: Pinpoint exact dimension pairs causing imbalance.
- Bilingual UI: One-click switch between Chinese and English.

License

This project is released under the MIT License.

Contact

Author: Guiru Zhao (赵桂儒)

Email: zhaoguiru@gmail.com

Theory Portal: https://www.5dtheory.org

Source Code & Datasets: Zenodo DOI 10.5281/zenodo.20376185
- 5DOS-OS (Execution Layer): Zenodo DOI [10.5281/zenodo.20399222](https://doi.org/10.5281/zenodo.20399222)
