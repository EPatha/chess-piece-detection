#!/usr/bin/env python3
"""Real-time screen capture preview UI.

This provides a lightweight PyQt5 UI that captures a screen region repeatedly (live)
and displays the preview in the window. It's intended as the realtime equivalent of
the screen recorder: instead of writing to disk, frames are available immediately
for processing (YOLO inference, OpenCV pipeline, etc.).

Usage:
    source .venv/bin/activate
    pip install -r requirements.txt
    python3 realtime_capture.py

Controls:
 - Set Left/Top/W/H to choose capture rectangle.
 - Set FPS.
 - Start/Stop to begin live capture.

Placeholder:
 - process_frame(frame) is a hook where you can run YOLO inference on the BGR
   numpy array `frame` (H,W,3) for each captured frame.
"""
import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import mss


class RealtimeCaptureWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Realtime Screen Capture')
        self.setGeometry(300, 200, 700, 480)

        self.sct = mss.mss()
        mon = self.sct.monitors[0]

        # region controls
        self.leftSpin = QtWidgets.QSpinBox(); self.leftSpin.setRange(0, mon['width']); self.leftSpin.setValue(0)
        self.topSpin = QtWidgets.QSpinBox(); self.topSpin.setRange(0, mon['height']); self.topSpin.setValue(0)
        self.widthSpin = QtWidgets.QSpinBox(); self.widthSpin.setRange(1, mon['width']); self.widthSpin.setValue(min(640, mon['width']))
        self.heightSpin = QtWidgets.QSpinBox(); self.heightSpin.setRange(1, mon['height']); self.heightSpin.setValue(min(360, mon['height']))

        self.fpsSpin = QtWidgets.QSpinBox(); self.fpsSpin.setRange(1, 60); self.fpsSpin.setValue(15)
        self.startBtn = QtWidgets.QPushButton('Start')
        self.stopBtn = QtWidgets.QPushButton('Stop'); self.stopBtn.setEnabled(False)

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(QtWidgets.QLabel('Left')); controls.addWidget(self.leftSpin)
        controls.addWidget(QtWidgets.QLabel('Top')); controls.addWidget(self.topSpin)
        controls.addWidget(QtWidgets.QLabel('W')); controls.addWidget(self.widthSpin)
        controls.addWidget(QtWidgets.QLabel('H')); controls.addWidget(self.heightSpin)
        controls.addWidget(QtWidgets.QLabel('FPS')); controls.addWidget(self.fpsSpin)
        controls.addWidget(self.startBtn); controls.addWidget(self.stopBtn)

        self.preview = QtWidgets.QLabel('Preview')
        self.preview.setFixedSize(640, 360)
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.preview.setStyleSheet('background:#000; color:#fff')

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self.preview)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._capture)
        self.is_running = False
        self.last_time = 0

        self.startBtn.clicked.connect(self.start)
        self.stopBtn.clicked.connect(self.stop)
        self.fpsSpin.valueChanged.connect(self._on_fps_change)

    def _on_fps_change(self, v):
        if self.is_running:
            self.timer.setInterval(int(1000 / v))

    def start(self):
        fps = int(self.fpsSpin.value())
        self.timer.start(int(1000 / fps))
        self.is_running = True
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.last_time = time.time()

    def stop(self):
        self.timer.stop()
        self.is_running = False
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)

    def _capture(self):
        left = int(self.leftSpin.value())
        top = int(self.topSpin.value())
        width = int(self.widthSpin.value())
        height = int(self.heightSpin.value())
        bbox = {'left': left, 'top': top, 'width': width, 'height': height}
        try:
            img = self.sct.grab(bbox)
        except Exception as e:
            print('Capture error:', e)
            return
        arr = np.array(img)
        frame = arr[:, :, :3]  # BGRA -> BGR

        # Show preview
        h, w, _ = frame.shape
        qimg = QtGui.QImage(frame.data, w, h, 3*w, QtGui.QImage.Format_BGR888)
        pix = QtGui.QPixmap.fromImage(qimg).scaled(self.preview.width(), self.preview.height(), QtCore.Qt.KeepAspectRatio)
        self.preview.setPixmap(pix)

        # Hook for processing frame (YOLO, etc.) - receives BGR numpy array
        self.process_frame(frame)

    def process_frame(self, frame: np.ndarray):
        """Placeholder for processing a single BGR frame in real-time.

        Replace or extend this method to run YOLO inference and draw overlays.
        It must be fast enough for the target FPS or run inference in a separate
        thread/pool.
        """
        # Example: simple fps print
        now = time.time()
        dt = now - getattr(self, '_last_proc_time', now)
        self._last_proc_time = now
        if dt > 0:
            fps = 1.0 / dt
            self.setWindowTitle(f'Realtime Screen Capture - {fps:.1f} FPS')


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = RealtimeCaptureWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
