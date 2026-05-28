#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5DOS Real-time Local Monitor v2.0 (Ratio Method)
五维操作系统诊断系统 - 比值法匹配度实时监控面板（双语版）
作者: 赵桂儒 / 五维系统论
联系: zhaoguiru@gmail.com
"""

import sys, os, time, psutil, numpy as np
from collections import deque, defaultdict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QSplitter,
    QGroupBox, QGridLayout, QPushButton, QSpinBox, QDoubleSpinBox,
    QCheckBox, QAbstractItemView, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QBrush, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import matplotlib.font_manager as fm

# ==================== 强制绑定中文字体文件（跨平台） ====================
def get_chinese_font():
    candidates = []
    if sys.platform == 'win32':
        candidates = [
            r'C:\Windows\Fonts\msyh.ttc',
            r'C:\Windows\Fonts\simhei.ttf',
            r'C:\Windows\Fonts\simsun.ttc',
        ]
    elif sys.platform == 'darwin':
        candidates = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
        ]
    else:
        candidates = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return fm.FontProperties(fname=path)
            except Exception:
                continue
    return None

CHINESE_FP = get_chinese_font()
if CHINESE_FP:
    matplotlib.rcParams['font.sans-serif'] = [CHINESE_FP.get_name(), 'DejaVu Sans', 'Arial Unicode MS']
    matplotlib.rcParams['axes.unicode_minus'] = False

# ==================== 语言管理器 ====================
TEXT = {
    'window_title': {'zh': '5DOS Real-time Monitor | 五维系统诊断实时监控 v2.0（比值法）',
                     'en': '5DOS Real-time Monitor | 5D System Diagnosis v2.0 (Ratio)'},
    'pause':          {'zh': '暂停', 'en': 'Pause'},
    'resume':         {'zh': '继续', 'en': 'Resume'},
    'refresh_ms':     {'zh': '刷新(ms):', 'en': 'Refresh(ms):'},
    'kappa_threshold':{'zh': 'κ阈值:', 'en': 'κ Threshold:'},
    'status_filter':  {'zh': '状态过滤:', 'en': 'Status Filter:'},
    'show_top50':     {'zh': '仅显示Top 50', 'en': 'Top 50 Only'},
    'language':       {'zh': '语言:', 'en': 'Language:'},
    'zh_label':       {'zh': '中文', 'en': 'Chinese'},
    'en_label':       {'zh': '英文', 'en': 'English'},
    'about_btn':      {'zh': '关于', 'en': 'About'},
    'about_title':    {'zh': '关于 5DOS', 'en': 'About 5DOS'},
    'about_text': {
        'zh': (
            "<b>5DOS 五维操作系统诊断系统 v2.0（比值法）</b><br><br>"
            "基于五维系统论（5D-ST）构建，采用比值法匹配度公式计算协同系数。<br><br>"
            "<b>作者：</b>赵桂儒 / 五维系统论创始人<br>"
            "<b>联系邮箱：</b>zhaoguiru@gmail.com<br><br>"
            "<b>核心公式（比值法）：</b><br>"
            "匹配度 γ(a,b) = min(a,b) / max(a,b)<br>"
            "外协同系数 κ = ∏ γ(x<sub>d</sub>, 1.0) = ∏ x<sub>d</sub><br>"
            "内协同系数 σ = ∏<sub>1≤i&lt;j≤5</sub> γ(x<sub>i</sub>, x<sub>j</sub>)<br><br>"
            "<b>五维定义：</b><br>"
            "B(边界) — 内存占用比例<br>"
            "R(储备) — CPU累积时间<br>"
            "S(结构) — 线程数量<br>"
            "D(方向) — 进程状态编码<br>"
            "I(强度) — CPU瞬时占用"
        ),
        'en': (
            "<b>5DOS Five-Dimensional OS Diagnosis v2.0 (Ratio Method)</b><br><br>"
            "Built on 5D Systems Theory (5D-ST), using ratio-based matching.<br><br>"
            "<b>Author:</b> Zhao Guiru / Founder of 5D Systems Theory<br>"
            "<b>Contact:</b> zhaoguiru@gmail.com<br><br>"
            "<b>Core Formula (Ratio Method):</b><br>"
            "Matching γ(a,b) = min(a,b) / max(a,b)<br>"
            "External synergy κ = ∏ γ(x<sub>d</sub>, 1.0) = ∏ x<sub>d</sub><br>"
            "Inner synergy σ = ∏<sub>1≤i&lt;j≤5</sub> γ(x<sub>i</sub>, x<sub>j</sub>)<br><br>"
            "<b>Five Dimensions:</b><br>"
            "B (Boundary) — Memory usage ratio<br>"
            "R (Reserve)  — Cumulative CPU time<br>"
            "S (Structure) — Thread count<br>"
            "D (Direction) — Process state encoding<br>"
            "I (Intensity) — Instantaneous CPU usage"
        )
    },
    'sys_avg_kappa':  {'zh': '系统平均 κ:', 'en': 'Sys Avg κ:'},
    'sys_avg_sigma':  {'zh': '系统平均 σ:', 'en': 'Sys Avg σ:'},
    'proc_count':     {'zh': '进程数:', 'en': 'Procs:'},
    'global_health':  {'zh': '全局健康度:', 'en': 'Health:'},
    'normal':         {'zh': '正常', 'en': 'Normal'},
    'subhealthy':     {'zh': '亚健康', 'en': 'Subhealthy'},
    'abnormal':       {'zh': '异常', 'en': 'Abnormal'},
    'filter_all':     {'zh': '全部', 'en': 'All'},
    'filter_running': {'zh': '仅running', 'en': 'Running Only'},
    'filter_run_sleep':{'zh': 'running+sleeping', 'en': 'Running+Sleeping'},
    'filter_idle':    {'zh': '仅idle', 'en': 'Idle Only'},
    'col_pid':        {'zh': 'PID', 'en': 'PID'},
    'col_name':       {'zh': '进程名', 'en': 'Name'},
    'col_status':     {'zh': '状态', 'en': 'Status'},
    'col_b':          {'zh': 'B(边界)', 'en': 'B(Boundary)'},
    'col_r':          {'zh': 'R(储备)', 'en': 'R(Reserve)'},
    'col_s':          {'zh': 'S(结构)', 'en': 'S(Structure)'},
    'col_d':          {'zh': 'D(方向)', 'en': 'D(Direction)'},
    'col_kappa':      {'zh': 'κ(外协同)', 'en': 'κ(Ext)'},
    'col_sigma':      {'zh': 'σ(内协同)', 'en': 'σ(Int)'},
    'radar_b':        {'zh': 'B(边界)', 'en': 'B(Boundary)'},
    'radar_r':        {'zh': 'R(储备)', 'en': 'R(Reserve)'},
    'radar_s':        {'zh': 'S(结构)', 'en': 'S(Structure)'},
    'radar_d':        {'zh': 'D(方向)', 'en': 'D(Direction)'},
    'radar_i':        {'zh': 'I(强度)', 'en': 'I(Intensity)'},
    'trend_title':    {'zh': 'κ/σ 趋势: {}', 'en': 'κ/σ Trend: {}'},
    'global_trend':   {'zh': '系统平均 κ/σ 趋势', 'en': 'System Average κ/σ Trend'},
    'detail_title':   {'zh': '五维数值详情 (归一化)', 'en': '5D Values (Normalized)'},
    'alert_title':    {'zh': '存在论异常诊断', 'en': 'Ontological Diagnosis'},
    'alert_select':   {'zh': '选择进程查看五维诊断结果', 'en': 'Select a process to view diagnosis'},
    'diag_severe':    {'zh': '严重失衡：κ极低，存在体濒临死亡态',
                       'en': 'SEVERE: κ extremely low, entity near death state'},
    'diag_short':     {'zh': '短板告警：{}维度极度缺损（{:.4f}），外协同被锁死',
                       'en': 'SHORTBOARD: {} severely deficient ({:.4f}), external synergy locked'},
    'diag_decouple':  {'zh': '内协同崩解：σ={:.4f}，五维严重解耦，结构失衡',
                       'en': 'DECOUPLED: σ={:.4f}, 5D severely decoupled, structural imbalance'},
    'diag_direction': {'zh': '方向异常：进程处于停止/僵尸/挂起状态，演化方向为负',
                       'en': 'DIRECTION: Process stopped/zombie/suspended, negative evolution'},
    'diag_boundary':  {'zh': '边界膨胀：内存占用超过系统5%，存在体边界过度扩张',
                       'en': 'BOUNDARY: Memory >5%, entity boundary over-expansion'},
    'diag_intensity': {'zh': '强度过载：CPU瞬时占用超过50%，存在体处于亢奋态',
                       'en': 'INTENSITY: CPU >50%, entity in hyper-excited state'},
    'diag_normal':    {'zh': '五维协同正常，存在体处于健康演化状态',
                       'en': '5D synergy normal, entity in healthy evolution'},
    'label_b':        {'zh': 'B(边界): {:.4f}  [原值: {:.2f}%]', 'en': 'B(Boundary): {:.4f}  [raw: {:.2f}%]'},
    'label_r':        {'zh': 'R(储备): {:.4f}  [原值: {:.1f}s]', 'en': 'R(Reserve): {:.4f}  [raw: {:.1f}s]'},
    'label_s':        {'zh': 'S(结构): {:.4f}  [原值: {:.0f}线程]', 'en': 'S(Structure): {:.4f}  [raw: {:.0f} threads]'},
    'label_d':        {'zh': 'D(方向): {:.4f}  [原值: {:+.1f}({})]', 'en': 'D(Direction): {:.4f}  [raw: {:+.1f}({})]'},
    'label_i':        {'zh': 'I(强度): {:.4f}  [原值: {:.1f}%]', 'en': 'I(Intensity): {:.4f}  [raw: {:.1f}%]'},
    'label_kappa':    {'zh': 'κ(外协同): {:.6f}', 'en': 'κ(External): {:.6f}'},
    'label_sigma':    {'zh': 'σ(内协同): {:.6f}', 'en': 'σ(Internal): {:.6f}'},
}

class Lang:
    current = 'en'
    @classmethod
    def tr(cls, key, *args):
        if key == 'about_text':
            return TEXT.get(key, {}).get(cls.current, '')
        s = TEXT.get(key, {}).get(cls.current, key)
        return s.format(*args) if args else s

# ==================== 五维计算核心（比值法） ====================
class FiveDimCalculator:
    DIMS = ['B', 'R', 'S', 'D', 'I']

    @staticmethod
    def ratio_match(a, b):
        """
        比值法匹配度公式
        γ(a,b) = min(a,b) / max(a,b) ,  a,b ≥ 0
        当 a=b 时 γ=1（完全匹配）；当 min=0 时 γ=0（完全不匹配）
        """
        a = float(a)
        b = float(b)
        mx = max(a, b)
        if mx == 0:
            return 1.0
        return min(a, b) / mx

    @staticmethod
    def get_process_5d(proc):
        try:
            with proc.oneshot():
                mem = proc.memory_percent()
                cpu_t = proc.cpu_times()
                r_val = cpu_t.user + cpu_t.system
                s_val = proc.num_threads()
                status = proc.status()
                i_val = proc.cpu_percent(interval=None)
                d_map = {
                    'running': 1.0, 'sleeping': 0.2, 'disk-sleep': 0.1,
                    'stopped': -0.8, 'tracing-stop': -0.5, 'zombie': -1.0,
                    'dead': -1.0, 'wake-kill': 0.5, 'waking': 0.8,
                    'idle': 0.05, 'locked': -0.3, 'waiting': 0.4, 'suspended': -0.6
                }
                d_val = d_map.get(status, 0.0)
                return {
                    'pid': proc.pid, 'name': proc.name(), 'B': max(0.0, float(mem)),
                    'R': max(0.0, float(r_val)), 'S': max(1.0, float(s_val)),
                    'D': float(d_val), 'I': max(0.0, float(i_val)), 'status': status
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None

    @staticmethod
    def normalize_5d(raw_5d, global_max):
        """将原始五维值归一化到 [0,1] 区间，供比值法使用"""
        n = {}
        n['B'] = min(raw_5d['B'] / 5.0, 1.0)
        n['R'] = min(raw_5d['R'] / max(global_max['R'], 1.0), 1.0)
        n['S'] = min(np.log10(raw_5d['S']) / 3.0, 1.0)
        n['D'] = (raw_5d['D'] + 1.0) / 2.0
        i_raw = max(raw_5d['I'], 0.1)
        n['I'] = min(i_raw / 100.0, 1.0)
        return n

    @staticmethod
    def compute_external_synergy(norm_5d):
        """
        外协同系数 κ：各维度与理想体（归一化上限 1.0）的比值匹配度乘积
        γ_d = ratio_match(norm_d, 1.0) = norm_d
        κ = ∏_{d∈{B,R,S,D,I}} γ_d
        """
        kappa = 1.0
        for d in FiveDimCalculator.DIMS:
            kappa *= norm_5d[d]
        return kappa

    @staticmethod
    def compute_internal_synergy(norm_5d):
        """
        内协同系数 σ：五维归一化值之间的两两比值匹配度乘积
        σ = ∏_{1≤i<j≤5} γ_{ij}
        γ_{ij} = ratio_match(norm_i, norm_j) = min(norm_i,norm_j) / max(norm_i,norm_j)
        """
        sigma = 1.0
        dims = FiveDimCalculator.DIMS
        for i in range(len(dims)):
            for j in range(i + 1, len(dims)):
                gamma = FiveDimCalculator.ratio_match(norm_5d[dims[i]], norm_5d[dims[j]])
                sigma *= gamma
        return sigma

# ==================== 后台采集线程 ====================
class MonitorThread(QThread):
    data_updated = pyqtSignal(list, dict)

    def __init__(self, interval_ms=2000, parent=None):
        super().__init__(parent)
        self.interval_ms = interval_ms
        self.running = True
        self.history = defaultdict(lambda: deque(maxlen=300))
        self.global_history = deque(maxlen=300)

    def run(self):
        while self.running:
            procs_data = []
            global_max = {'R': 1.0, 'S': 1.0, 'B': 1.0, 'I': 1.0}
            raw_list = []
            for proc in psutil.process_iter(['pid', 'name']):
                raw = FiveDimCalculator.get_process_5d(proc)
                if raw:
                    raw_list.append(raw)
                    for k in global_max:
                        global_max[k] = max(global_max[k], raw[k])

            kappa_sum = 0.0
            sigma_sum = 0.0
            count = 0
            for raw in raw_list:
                norm = FiveDimCalculator.normalize_5d(raw, global_max)
                kappa = FiveDimCalculator.compute_external_synergy(norm)
                sigma = FiveDimCalculator.compute_internal_synergy(norm)
                self.history[raw['pid']].append({
                    'time': time.time(), 'kappa': kappa, 'sigma': sigma,
                    'norm': norm, 'raw': raw
                })
                procs_data.append({
                    'pid': raw['pid'], 'name': raw['name'], 'status': raw['status'],
                    'raw': raw, 'norm': norm, 'kappa': kappa, 'sigma': sigma,
                    'history': list(self.history[raw['pid']])
                })
                kappa_sum += kappa
                sigma_sum += sigma
                count += 1

            avg_kappa = kappa_sum / max(count, 1)
            avg_sigma = sigma_sum / max(count, 1)
            self.global_history.append({
                'time': time.time(), 'kappa': avg_kappa, 'sigma': avg_sigma
            })
            stats = {
                'global_max': global_max, 'avg_kappa': avg_kappa,
                'avg_sigma': avg_sigma,
                'global_history': list(self.global_history), 'total_procs': count
            }
            self.data_updated.emit(procs_data, stats)
            self.msleep(self.interval_ms)

    def stop(self):
        self.running = False
        self.wait(1000)

# ==================== 雷达图 ====================
class RadarChart(FigureCanvas):
    def __init__(self, parent=None, width=4.5, height=4):
        self.fig = Figure(figsize=(width, height), dpi=100)
        self.ax = self.fig.add_subplot(111, polar=True)
        super().__init__(self.fig)
        self.setParent(parent)
        self.angles = np.linspace(0, 2*np.pi, 5, endpoint=False).tolist()
        self.angles += self.angles[:1]

    def labels(self):
        return [Lang.tr('radar_b'), Lang.tr('radar_r'), Lang.tr('radar_s'),
                Lang.tr('radar_d'), Lang.tr('radar_i')]

    def update_data(self, norm_5d, kappa, sigma, name):
        self.ax.clear()
        values = [norm_5d['B'], norm_5d['R'], norm_5d['S'], norm_5d['D'], norm_5d['I']]
        values += values[:1]
        self.ax.plot(self.angles, values, 'o-', linewidth=2.5, color='#2196F3')
        self.ax.fill(self.angles, values, alpha=0.25, color='#2196F3')
        self.ax.plot(self.angles, [1.0]*6, '--', linewidth=1, color='gray', alpha=0.5)
        self.ax.set_xticks(self.angles[:-1])
        lbls = self.labels()
        title = f"{name}\nκ = {kappa:.5f} | σ = {sigma:.5f}"
        if CHINESE_FP and Lang.current == 'zh':
            self.ax.set_xticklabels(lbls, fontsize=10, fontproperties=CHINESE_FP)
            self.ax.set_title(title, fontsize=11, pad=15, fontproperties=CHINESE_FP)
        else:
            self.ax.set_xticklabels(lbls, fontsize=10)
            self.ax.set_title(title, fontsize=11, pad=15)
        self.ax.set_ylim(0, 1)
        self.ax.grid(True)
        self.fig.tight_layout()
        self.draw()

# ==================== κ/σ 趋势图 ====================
class KappaTrendChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=2.5):
        self.fig = Figure(figsize=(width, height), dpi=100)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

    def update_data(self, history, name):
        self.ax.clear()
        if len(history) > 0:
            x = range(len(history))
            y_kappa = [h['kappa'] for h in history]
            y_sigma = [h['sigma'] for h in history]
            self.ax.plot(x, y_kappa, '-', color='#FF5722', linewidth=1.5, label='κ')
            self.ax.plot(x, y_sigma, '-', color='#2196F3', linewidth=1.5, label='σ')
            self.ax.axhline(y=y_kappa[-1], color='red', linestyle=':', alpha=0.5)
            self.ax.axhline(y=y_sigma[-1], color='blue', linestyle=':', alpha=0.5)
            self.ax.legend(loc='upper right', fontsize=8)
        title = Lang.tr('trend_title', name)
        if CHINESE_FP and Lang.current == 'zh':
            self.ax.set_title(title, fontsize=10, fontproperties=CHINESE_FP)
        else:
            self.ax.set_title(title, fontsize=10)
        self.ax.set_ylim(0, 1.0)
        self.ax.set_xlabel("Samples", fontsize=8)
        self.ax.set_ylabel("κ / σ", fontsize=8)
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.draw()

# ==================== 全局 κ/σ 趋势图 ====================
class GlobalKappaChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=1.8):
        self.fig = Figure(figsize=(width, height), dpi=100)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

    def update_data(self, history):
        self.ax.clear()
        if len(history) > 0:
            x = range(len(history))
            y_kappa = [h['kappa'] for h in history]
            y_sigma = [h['sigma'] for h in history]
            self.ax.plot(x, y_kappa, '-', color='#4CAF50', linewidth=2, label='κ')
            self.ax.plot(x, y_sigma, '-', color='#9C27B0', linewidth=2, label='σ')
            self.ax.axhline(y=y_kappa[-1], color='green', linestyle=':', alpha=0.7)
            self.ax.axhline(y=y_sigma[-1], color='purple', linestyle=':', alpha=0.7)
            self.ax.legend(loc='upper right', fontsize=8)
        title = Lang.tr('global_trend')
        if CHINESE_FP and Lang.current == 'zh':
            self.ax.set_title(title, fontsize=9, fontproperties=CHINESE_FP)
        else:
            self.ax.set_title(title, fontsize=9)
        self.ax.set_ylim(0, max(0.01, max(y_kappa + y_sigma) * 1.5) if len(history) > 0 else 0.01)
        self.ax.set_xlabel("Samples", fontsize=8)
        self.ax.set_ylabel("κ / σ", fontsize=8)
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.draw()

# ==================== 主窗口 ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_pid = None
        self.procs_data = []
        self.stats = {}
        self.kappa_threshold = 0.001

        self.init_ui()
        self.monitor = MonitorThread(interval_ms=2000)
        self.monitor.data_updated.connect(self.on_data_updated)
        self.monitor.start()

        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.refresh_ui)
        self.ui_timer.start(1000)

    def init_ui(self):
        self.setWindowTitle(Lang.tr('window_title'))
        self.resize(1550, 980)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        toolbar = QHBoxLayout()
        self.btn_pause = QPushButton(Lang.tr('pause'))
        self.btn_pause.setCheckable(True)
        self.btn_pause.toggled.connect(self.toggle_monitor)
        toolbar.addWidget(self.btn_pause)

        self.lbl_refresh = QLabel(Lang.tr('refresh_ms'))
        toolbar.addWidget(self.lbl_refresh)
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(500, 10000)
        self.spin_interval.setValue(2000)
        self.spin_interval.setSingleStep(500)
        self.spin_interval.valueChanged.connect(self.change_interval)
        toolbar.addWidget(self.spin_interval)

        self.lbl_threshold = QLabel(Lang.tr('kappa_threshold'))
        toolbar.addWidget(self.lbl_threshold)
        self.spin_threshold = QDoubleSpinBox()
        self.spin_threshold.setRange(0.0001, 1.0)
        self.spin_threshold.setDecimals(4)
        self.spin_threshold.setValue(0.001)
        self.spin_threshold.setSingleStep(0.001)
        self.spin_threshold.valueChanged.connect(lambda v: setattr(self, 'kappa_threshold', v))
        toolbar.addWidget(self.spin_threshold)

        self.lbl_filter = QLabel(Lang.tr('status_filter'))
        toolbar.addWidget(self.lbl_filter)
        self.combo_filter = QComboBox()
        self.combo_filter.addItems([
            Lang.tr('filter_all'), Lang.tr('filter_running'),
            Lang.tr('filter_run_sleep'), Lang.tr('filter_idle')
        ])
        self.combo_filter.setCurrentIndex(0)
        toolbar.addWidget(self.combo_filter)

        self.chk_top = QCheckBox(Lang.tr('show_top50'))
        self.chk_top.setChecked(True)
        toolbar.addWidget(self.chk_top)

        self.lbl_language = QLabel(Lang.tr('language'))
        toolbar.addWidget(self.lbl_language)
        self.combo_lang = QComboBox()
        self.combo_lang.addItems([Lang.tr('zh_label'), Lang.tr('en_label')])
        self.combo_lang.setCurrentIndex(1)
        self.combo_lang.currentIndexChanged.connect(self.change_language)
        toolbar.addWidget(self.combo_lang)

        self.btn_about = QPushButton(Lang.tr('about_btn'))
        self.btn_about.clicked.connect(self.show_about)
        toolbar.addWidget(self.btn_about)

        toolbar.addStretch()
        left_layout.addLayout(toolbar)

        self.lbl_stats = QLabel("")
        left_layout.addWidget(self.lbl_stats)

        # 表格（增加 σ 列）
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            Lang.tr('col_pid'), Lang.tr('col_name'), Lang.tr('col_status'),
            Lang.tr('col_b'), Lang.tr('col_r'), Lang.tr('col_s'),
            Lang.tr('col_d'), Lang.tr('col_kappa'), Lang.tr('col_sigma')
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 140)
        self.table.setColumnWidth(2, 85)
        self.table.setColumnWidth(3, 72)
        self.table.setColumnWidth(4, 72)
        self.table.setColumnWidth(5, 72)
        self.table.setColumnWidth(6, 72)
        self.table.setColumnWidth(7, 95)
        self.table.setColumnWidth(8, 95)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.setAlternatingRowColors(True)
        left_layout.addWidget(self.table)

        # 右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.radar = RadarChart(width=4.5, height=4)
        right_layout.addWidget(self.radar, stretch=3)

        self.trend = KappaTrendChart(width=5, height=2.5)
        right_layout.addWidget(self.trend, stretch=2)

        self.global_trend = GlobalKappaChart(width=5, height=1.8)
        right_layout.addWidget(self.global_trend, stretch=1)

        self.detail_box = QGroupBox(Lang.tr('detail_title'))
        detail_layout = QGridLayout(self.detail_box)
        self.lbl_b = QLabel("B: --")
        self.lbl_r = QLabel("R: --")
        self.lbl_s = QLabel("S: --")
        self.lbl_d = QLabel("D: --")
        self.lbl_i = QLabel("I: --")
        self.lbl_kappa = QLabel("κ: --")
        self.lbl_sigma = QLabel("σ: --")
        detail_layout.addWidget(self.lbl_b, 0, 0)
        detail_layout.addWidget(self.lbl_r, 0, 1)
        detail_layout.addWidget(self.lbl_s, 1, 0)
        detail_layout.addWidget(self.lbl_d, 1, 1)
        detail_layout.addWidget(self.lbl_i, 2, 0)
        detail_layout.addWidget(self.lbl_kappa, 2, 1)
        detail_layout.addWidget(self.lbl_sigma, 3, 0)
        right_layout.addWidget(self.detail_box, stretch=1)

        self.alert_box = QGroupBox(Lang.tr('alert_title'))
        alert_layout = QVBoxLayout(self.alert_box)
        self.lbl_alert = QLabel(Lang.tr('alert_select'))
        self.lbl_alert.setWordWrap(True)
        alert_layout.addWidget(self.lbl_alert)
        right_layout.addWidget(self.alert_box, stretch=1)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([680, 870])
        main_layout.addWidget(splitter)

    def show_about(self):
        QMessageBox.information(self, Lang.tr('about_title'), Lang.tr('about_text'))

    def change_language(self, idx):
        Lang.current = 'zh' if idx == 0 else 'en'
        self.setWindowTitle(Lang.tr('window_title'))
        self.update_static_texts()
        self.refresh_ui()
        if self.current_pid:
            self.update_detail_panel()

    def update_static_texts(self):
        self.btn_pause.setText(Lang.tr('resume') if self.btn_pause.isChecked() else Lang.tr('pause'))
        self.btn_about.setText(Lang.tr('about_btn'))
        self.lbl_refresh.setText(Lang.tr('refresh_ms'))
        self.lbl_threshold.setText(Lang.tr('kappa_threshold'))
        self.lbl_filter.setText(Lang.tr('status_filter'))
        self.chk_top.setText(Lang.tr('show_top50'))
        self.lbl_language.setText(Lang.tr('language'))
        cur_idx = self.combo_filter.currentIndex()
        self.combo_filter.clear()
        self.combo_filter.addItems([
            Lang.tr('filter_all'), Lang.tr('filter_running'),
            Lang.tr('filter_run_sleep'), Lang.tr('filter_idle')
        ])
        self.combo_filter.setCurrentIndex(cur_idx)
        self.table.setHorizontalHeaderLabels([
            Lang.tr('col_pid'), Lang.tr('col_name'), Lang.tr('col_status'),
            Lang.tr('col_b'), Lang.tr('col_r'), Lang.tr('col_s'),
            Lang.tr('col_d'), Lang.tr('col_kappa'), Lang.tr('col_sigma')
        ])
        self.detail_box.setTitle(Lang.tr('detail_title'))
        self.alert_box.setTitle(Lang.tr('alert_title'))
        if not self.table.selectedItems():
            self.lbl_alert.setText(Lang.tr('alert_select'))

    def toggle_monitor(self, checked):
        if checked:
            self.monitor.running = False
            self.btn_pause.setText(Lang.tr('resume'))
        else:
            self.monitor.running = True
            self.monitor.start()
            self.btn_pause.setText(Lang.tr('pause'))

    def change_interval(self, val):
        self.monitor.interval_ms = val

    def on_data_updated(self, procs_data, stats):
        self.procs_data = sorted(procs_data, key=lambda x: x['kappa'], reverse=True)
        self.stats = stats

    def refresh_ui(self):
        if not self.procs_data:
            return

        avg_k = self.stats.get('avg_kappa', 0)
        avg_s = self.stats.get('avg_sigma', 0)
        total = self.stats.get('total_procs', 0)
        if avg_k > 0.01 and avg_s > 0.1:
            health = Lang.tr('normal')
        elif avg_k > 0.001 and avg_s > 0.01:
            health = Lang.tr('subhealthy')
        else:
            health = Lang.tr('abnormal')
        self.lbl_stats.setText(
            f"{Lang.tr('sys_avg_kappa')} {avg_k:.5f} | "
            f"{Lang.tr('sys_avg_sigma')} {avg_s:.5f} | "
            f"{Lang.tr('proc_count')} {total} | "
            f"{Lang.tr('global_health')} {health}"
        )

        idx = self.combo_filter.currentIndex()
        filtered = self.procs_data
        if idx == 1:
            filtered = [p for p in self.procs_data if p['status'] == 'running']
        elif idx == 2:
            filtered = [p for p in self.procs_data if p['status'] in ('running', 'sleeping')]
        elif idx == 3:
            filtered = [p for p in self.procs_data if p['status'] == 'idle']

        display_data = filtered[:50] if self.chk_top.isChecked() else filtered

        current_row = self.table.currentRow()
        current_pid = None
        if current_row >= 0:
            item = self.table.item(current_row, 0)
            if item:
                try:
                    current_pid = int(item.text())
                except Exception:
                    pass

        self.table.setRowCount(len(display_data))

        for row, p in enumerate(display_data):
            pid = p['pid']
            norm = p['norm']
            kappa = p['kappa']
            sigma = p['sigma']
            raw = p['raw']

            items = [
                QTableWidgetItem(str(pid)),
                QTableWidgetItem(p['name']),
                QTableWidgetItem(p['status']),
                QTableWidgetItem(f"{norm['B']:.3f}"),
                QTableWidgetItem(f"{norm['R']:.3f}"),
                QTableWidgetItem(f"{norm['S']:.3f}"),
                QTableWidgetItem(f"{norm['D']:.3f}"),
                QTableWidgetItem(f"{kappa:.5f}"),
                QTableWidgetItem(f"{sigma:.5f}")
            ]

            if kappa < 0.001 or sigma < 0.001:
                color = QColor(255, 180, 180)
                fg = QColor(150, 0, 0)
            elif kappa < 0.01 or sigma < 0.01:
                color = QColor(255, 235, 180)
                fg = QColor(120, 80, 0)
            else:
                color = QColor(200, 255, 200)
                fg = QColor(0, 100, 0)

            for item in items:
                item.setBackground(QBrush(color))
                item.setForeground(QBrush(fg))

            for col, item in enumerate(items):
                self.table.setItem(row, col, item)

            if pid == current_pid:
                self.table.selectRow(row)

        self.global_trend.update_data(self.stats.get('global_history', []))

        if self.current_pid is not None:
            self.update_detail_panel()

    def on_selection_changed(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            pid_item = self.table.item(row, 0)
            if pid_item:
                try:
                    self.current_pid = int(pid_item.text())
                    self.update_detail_panel()
                except Exception:
                    pass

    def update_detail_panel(self):
        proc = None
        for p in self.procs_data:
            if p['pid'] == self.current_pid:
                proc = p
                break
        if not proc:
            return

        norm = proc['norm']
        raw = proc['raw']
        kappa = proc['kappa']
        sigma = proc['sigma']
        name = f"{proc['name']}({proc['pid']})"

        self.radar.update_data(norm, kappa, sigma, name)
        self.trend.update_data(proc['history'], name)

        self.lbl_b.setText(Lang.tr('label_b', norm['B'], raw['B']))
        self.lbl_r.setText(Lang.tr('label_r', norm['R'], raw['R']))
        self.lbl_s.setText(Lang.tr('label_s', norm['S'], raw['S']))
        self.lbl_d.setText(Lang.tr('label_d', norm['D'], raw['D'], raw['status']))
        self.lbl_i.setText(Lang.tr('label_i', norm['I'], raw['I']))
        self.lbl_kappa.setText(Lang.tr('label_kappa', kappa))
        self.lbl_sigma.setText(Lang.tr('label_sigma', sigma))

        dims = {'B': norm['B'], 'R': norm['R'], 'S': norm['S'], 'D': norm['D'], 'I': norm['I']}
        min_dim = min(dims, key=dims.get)
        min_val = dims[min_dim]

        dim_names = {'B': Lang.tr('radar_b'), 'R': Lang.tr('radar_r'),
                     'S': Lang.tr('radar_s'), 'D': Lang.tr('radar_d'), 'I': Lang.tr('radar_i')}

        alerts = []
        if kappa < 0.0001:
            alerts.append(Lang.tr('diag_severe'))
        elif min_val < 0.01:
            alerts.append(Lang.tr('diag_short', dim_names[min_dim], min_val))
        if sigma < 0.001:
            alerts.append(Lang.tr('diag_decouple', sigma))
        if raw['D'] < 0:
            alerts.append(Lang.tr('diag_direction'))
        if raw['B'] > 20:
            alerts.append(Lang.tr('diag_boundary'))
        if raw['I'] > 50:
            alerts.append(Lang.tr('diag_intensity'))

        self.lbl_alert.setText("\n".join(alerts) if alerts else Lang.tr('diag_normal'))

    def closeEvent(self, event):
        self.monitor.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
