# 5DOS Real-time Monitor | 五维操作系统诊断系统 v1.0

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)]()
[![Theory](https://img.shields.io/badge/Theory-5D--ST-orange)]()

> The first engineering implementation of Five-Dimensional Systems Theory (5D-ST) in operating system diagnosis.
> 五维系统论（5D-ST）在操作系统诊断领域的首个工程化实现。

---

## 1. Overview | 简介

5DOS Monitor is a real-time local process monitor built on Five-Dimensional Systems Theory (5D-ST). It maps every system process into five ontological dimensions—Boundary, Reserve, Structure, Direction, and Intensity—and computes the Synergy Coefficient κ to quantify the health and coupling state of digital entities.

5DOS 监控器是基于五维系统论（5D-ST）构建的本地实时进程诊断工具。它将每个系统进程映射到存在论五维——边界、储备、结构、方向、强度——并通过协同系数 κ 量化数字存在体的健康度与耦合状态。

---

## 2. Core Formula | 核心公式

### Synergy Coefficient | 协同系数

    κ = γ_B · γ_R · γ_S · γ_D · γ_I

### Inner Synergy Coefficient | 内协同系数

    σ = ∏_{1≤i<j≤5} γ_{ij}

Where γ_{ij} represents the matching degree between dimension i and dimension j (10 inter-dimensional pairs in total).

其中 γ_{ij} 表示维度 i 与维度 j 之间的匹配度（五维共产生 10 个维度对）。

---

## 3. Five Dimensions | 五维定义

| Dimension | Symbol | Meaning | 含义 |
|-----------|--------|---------|------|
| Boundary | B | Memory usage ratio | 内存占用比例 |
| Reserve | R | Cumulative CPU time | CPU 累积时间 |
| Structure | S | Thread count | 线程数量 |
| Direction | D | Process state encoding | 进程状态编码 |
| Intensity | I | Instantaneous CPU usage | CPU 瞬时占用 |

Direction encoding | 方向编码:
- running = +1.0 (forward evolution | 正向演化)
- sleeping = +0.2 (low-energy maintenance | 低能耗维持)
- stopped = -0.8 (external block | 外部阻断)
- zombie = -1.0 (death residual | 死亡残留)

---

## 4. Installation | 安装

Requirements | 环境要求
- Python 3.8+
- psutil
- PyQt5
- matplotlib
- numpy

Windows:

    pip install psutil PyQt5 matplotlib numpy
    python 5DOS_monitor.py

Linux:

    sudo apt install python3-pyqt5 python3-matplotlib python3-numpy python3-psutil
    python3 5DOS_monitor.py

---

## 5. Features | 功能特性

- Real-time 5D Radar | 实时五维雷达图: Visualize the five-dimensional state of any selected process.
- κ Trend Tracking | κ 趋势追踪: Historical curve of synergy coefficient for each process.
- System Health Gauge | 系统健康度: Global average κ with three-level color alert (Green/Yellow/Red).
- Bilingual UI | 中英双语界面: One-click switch between Chinese and English.
- Status Filter | 状态过滤: Filter by process state (All / Running / Running+Sleeping / Idle).
- Ontological Diagnosis | 存在论异常诊断: Automatic shortboard detection based on the weakest dimension.

---

## 6. Screenshot | 界面预览

![5DOS Running on Windows 11](monitor.jpg)

---

## 7. Project Philosophy | 项目理念

5DOS is not merely a process monitor—it is the computational verification of Five-Dimensional Systems Theory. By open-sourcing this tool, we invite the global community to empirically validate whether the synergy coefficient κ is an intrinsic property of digital entities or merely an artifact of observation.

5DOS 不仅仅是一个进程监控器，它是五维系统论的可计算验证。通过开源这一工具，我们邀请全球社区共同实证：协同系数 κ 究竟是数字存在体的内禀属性，还是观测数据的过拟合产物。

---

## 8. License | 开源协议

This project is released under the MIT License.

本项目采用 MIT 协议 开源。

---

## 9. Contact | 联系方式

Author | 作者: Zhao Guiru (赵桂儒) / Founder of Five-Dimensional Systems Theory
Email | 邮箱: zhaoguiru@gmail.com
Theory Portal | 理论入口: https://www.5dtheory.org

---

"The last low-hanging fruit of human civilization."
"人类文明史上最后一个弯腰就能摘到的果子。"
…
