#!/usr/bin/env python3
"""Simple screen recorder UI using PyQt5 and mss.

Features:
- Select a rectangular region on the screen with a rubber-band selection.
- Live preview of the selected region.
- Start/Stop recording to an MP4 file (using OpenCV VideoWriter).

Usage:
    source .venv/bin/activate
    pip install PyQt5 mss opencv-python numpy
    python3 screen_recorder.py

Notes:
- This is intentionally minimal and focused on recording a screen crop for later processing.
- Recording uses CPU; pick a modest FPS (10-15) for reliability on laptops.
"""
import sys
import time
import os
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import cv2
import mss


# Removed interactive screen selection. Users can now enter a crop rectangle
# (left, top, width, height) manually in the UI. This simplifies UI and
# avoids fullscreen transparent windows which can be problematic on some OSes.


class RecorderWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Screen Recorder')
        self.setGeometry(200, 200, 640, 480)
        # screen grabber
        self.sct = mss.mss()
        mon = self.sct.monitors[0]

        # manual region inputs (left, top, width, height)
        self.leftSpin = QtWidgets.QSpinBox()
        self.leftSpin.setRange(0, mon['width'])
        self.leftSpin.setValue(0)
        self.topSpin = QtWidgets.QSpinBox()
        self.topSpin.setRange(0, mon['height'])
        self.topSpin.setValue(0)
        self.widthSpin = QtWidgets.QSpinBox()
        self.widthSpin.setRange(1, mon['width'])
        self.widthSpin.setValue(min(640, mon['width']))
        self.heightSpin = QtWidgets.QSpinBox()
        self.heightSpin.setRange(1, mon['height'])
        self.heightSpin.setValue(min(360, mon['height']))

        self.startBtn = QtWidgets.QPushButton('Start Recording')
        self.stopBtn = QtWidgets.QPushButton('Stop Recording')
        self.stopBtn.setEnabled(False)

        self.fpsSpin = QtWidgets.QSpinBox()
        self.fpsSpin.setRange(1, 60)
        self.fpsSpin.setValue(15)

        self.previewLabel = QtWidgets.QLabel('No region selected')
        self.previewLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previewLabel.setFixedSize(600, 360)
        self.previewLabel.setStyleSheet('background: #222; color: #eee;')

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(QtWidgets.QLabel('Left:'))
        controls.addWidget(self.leftSpin)
        controls.addWidget(QtWidgets.QLabel('Top:'))
        controls.addWidget(self.topSpin)
        controls.addWidget(QtWidgets.QLabel('W:'))
        controls.addWidget(self.widthSpin)
        controls.addWidget(QtWidgets.QLabel('H:'))
        controls.addWidget(self.heightSpin)
        controls.addWidget(QtWidgets.QLabel('FPS:'))
        controls.addWidget(self.fpsSpin)
        controls.addWidget(self.startBtn)
        controls.addWidget(self.stopBtn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self.previewLabel)

        self.startBtn.clicked.connect(self.start_recording)
        self.stopBtn.clicked.connect(self.stop_recording)

        # keep selection compatibility variable (not used)
        self.selection = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_preview)
        self.writer = None
        self.recording = False
        self.frame_interval = 1.0 / self.fpsSpin.value()
        self.last_frame_time = 0

        # update fps change
        self.fpsSpin.valueChanged.connect(self.on_fps_changed)

    def on_fps_changed(self, v):
        self.frame_interval = 1.0 / v

    # Removed interactive selection handlers; user provides region via spinboxes

    def update_preview(self):
        # Use manual spinbox values for the capture region
        left = int(self.leftSpin.value())
        top = int(self.topSpin.value())
        width = int(self.widthSpin.value())
        height = int(self.heightSpin.value())
        if width <= 0 or height <= 0:
            return
        bbox = {'left': left, 'top': top, 'width': width, 'height': height}
        img = self.sct.grab(bbox)
        arr = np.array(img)
        # BGRA -> BGR
        frame = arr[:, :, :3]
        h, w, _ = frame.shape
        # convert to QImage
        qimg = QtGui.QImage(frame.data, w, h, 3*w, QtGui.QImage.Format_BGR888)
        pix = QtGui.QPixmap.fromImage(qimg).scaled(self.previewLabel.width(), self.previewLabel.height(), QtCore.Qt.KeepAspectRatio)
        self.previewLabel.setPixmap(pix)

        # if recording, write frame (respect fps)
        if self.recording:
            now = time.time()
            if now - self.last_frame_time >= self.frame_interval:
                self.last_frame_time = now
                # ensure writer is set
                if self.writer is not None:
                    # convert BGR to RGB for writing with cv2 if needed
                    self.writer.write(frame)

    def start_recording(self):
        # prepare writer using spinbox region
        w = int(self.widthSpin.value())
        h = int(self.heightSpin.value())
        fps = int(self.fpsSpin.value())
        out_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save recording', os.path.expanduser('~/screen_recording.mp4'), 'MP4 files (*.mp4)')[0]
        if not out_name:
            return
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(out_name, fourcc, fps, (w, h))
        if not self.writer.isOpened():
            QtWidgets.QMessageBox.critical(self, 'Error', 'Cannot open video writer')
            self.writer = None
            return
        self.recording = True
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.timer.start(int(self.frame_interval * 1000))
        self.last_frame_time = 0

    def stop_recording(self):
        self.recording = False
        self.timer.stop()
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        QtWidgets.QMessageBox.information(self, 'Saved', 'Recording finished')


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = RecorderWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
