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


class ScreenSelectionWindow(QtWidgets.QWidget):
    """Full-screen transparent window that allows rubber-band selection."""

    regionSelected = QtCore.pyqtSignal(QtCore.QRect)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setWindowState(self.windowState() | QtCore.Qt.WindowFullScreen)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.origin = QtCore.QPoint()

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            rect = QtCore.QRect(self.origin, event.pos()).normalized()
            self.rubberBand.setGeometry(rect)

    def mouseReleaseEvent(self, event):
        rect = self.rubberBand.geometry()
        self.rubberBand.hide()
        self.origin = QtCore.QPoint()
        self.regionSelected.emit(rect)
        self.close()


class RecorderWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Screen Recorder')
        self.setGeometry(200, 200, 640, 480)

        self.selectBtn = QtWidgets.QPushButton('Select Region')
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
        controls.addWidget(self.selectBtn)
        controls.addWidget(QtWidgets.QLabel('FPS:'))
        controls.addWidget(self.fpsSpin)
        controls.addWidget(self.startBtn)
        controls.addWidget(self.stopBtn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self.previewLabel)

        self.selectBtn.clicked.connect(self.open_selection)
        self.startBtn.clicked.connect(self.start_recording)
        self.stopBtn.clicked.connect(self.stop_recording)

        self.sct = mss.mss()
        self.selection = None  # QRect
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

    def open_selection(self):
        # hide main window and show full-screen selection
        self.hide()
        self.selwin = ScreenSelectionWindow()
        self.selwin.regionSelected.connect(self.on_region_selected)
        self.selwin.show()

    def on_region_selected(self, rect: QtCore.QRect):
        # rect is in screen coordinates
        self.selection = rect
        self.show()
        self.update_preview()
        QtWidgets.QMessageBox.information(self, 'Region Selected', f'Selected region: {rect.x()},{rect.y()} {rect.width()}x{rect.height()}')

    def update_preview(self):
        if not self.selection:
            return
        bbox = {'left': int(self.selection.x()), 'top': int(self.selection.y()), 'width': int(self.selection.width()), 'height': int(self.selection.height())}
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
        if not self.selection:
            QtWidgets.QMessageBox.warning(self, 'No region', 'Please select a region first')
            return
        # prepare writer
        w = int(self.selection.width())
        h = int(self.selection.height())
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
