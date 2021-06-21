# -*- coding: UTF-8 -*-

import time
import sys

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .utils import *
# from cv2 import VideoCapture,CAP_PROP_FPS
import cv2
import numpy as np


class ArrayCapture:
    def init(self):
        self.data = []
        self.pos = 0

    def __init__(self):
        self.init()

    def open(self, obj: list):
        self.data = obj
        self.pos = 0

    def release(self):
        self.init()

    def read(self) -> [bool, np.ndarray]:
        if 0 <= self.pos < len(self.data):
            ans = True, self.data[self.pos]
            self.pos += 1
        else:
            ans = False, None
        return ans


class VideoBox(QWidget):
    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1

    STATUS_INIT = 0
    STATUS_PLAYING = 1
    STATUS_PAUSE = 2

    video_obj = ""

    def set_control_box(self):
        control_box = QHBoxLayout()
        control_box.setContentsMargins(0, 0, 0, 0)
        control_box.addWidget(self.playButton)
        groupBox = QGroupBox('Set FPS')
        fpsLayout = QHBoxLayout()
        self.fps_spin = QSpinBox()
        self.fps_spin.setMaximum(50)
        self.fps_spin.setMinimum(1)
        self.fps_spin.setValue(24)
        groupBox.setMaximumWidth(100)
        groupBox.setMaximumHeight(80)
        fpsLayout.addWidget(self.fps_spin)
        groupBox.setLayout(fpsLayout)
        control_box.addWidget(groupBox)
        return control_box

    def set_init_image(self):
        init_image = QPixmap("./res/video.jpeg")#.scaled(self.pictureLabel.width(), self.pictureLabel.height())
        def set_image(qpixmap):
            qpixmap=qpixmap.scaled(self.pictureLabel.width(), self.pictureLabel.height(),Qt.KeepAspectRatio)
            self.pictureLabel.setPixmap(qpixmap)

        if self.capture is None or self.video_obj is None:
            set_image(init_image)
            return
        ok, frame=self.capture.read()
        if not ok:
            set_image(init_image)
            return
        temp_image = self.img2qimage(frame)
        temp_pixmap = QPixmap.fromImage(temp_image)
        set_image(temp_pixmap)

    def setup_UI(self):
        self.pictureLabel = QLabel()
        self.set_init_image()
        self.playButton = QPushButton()
        self.playButton.setEnabled(True)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        control_box = self.set_control_box()
        layout = QVBoxLayout()
        layout.addWidget(self.pictureLabel)
        layout.addLayout(control_box)
        self.setLayout(layout)

    def setup_object(self):
        self.status = self.STATUS_INIT  # 0: init 1:playing 2: pause
        # capture 初始设置
        if self.video_obj is None:
            return
        if isinstance(self.video_obj, str):
            self.capture = cv2.VideoCapture()
        elif isinstance(self.video_obj, list):
            if len(self.video_obj)<=0 or not isinstance(self.video_obj[0],np.ndarray):
                raise Exception('invalid ndarray list')
            self.capture = ArrayCapture()
        else:
            raise Exception(f'invalid type {type(self.video_obj)}')
        self.capture.open(self.video_obj)
        self.set_init_image()


        self.timer.stop()
        # self.status = VideoBox.STATUS_PLAYING
        # self.toggle_video()


    def __init__(self, parent=None,video_obj=None, video_type=VIDEO_TYPE_OFFLINE, auto_play=False):
        QWidget.__init__(self,parent)
        self.video_obj = video_obj
        self.video_type = video_type  # 0: offline  1: realTime
        self.auto_play = auto_play
        self.capture=None
        # timer 设置
        self.timer = VideoTimer()
        # 组件展示
        self.setup_UI()
        # 初始化一些对象
        # if video_obj is not None:
        self.setup_object()
        self.playButton.clicked.connect(self.toggle_video)
        self.timer.timeSignal.signal[str].connect(self.show_video_images)


    def reset(self):

        self.capture.release()
        self.status = VideoBox.STATUS_INIT
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.timer.stop()

    def img2qimage(self, image):
        if image.shape.__len__() == 2:
            image = stack_gray_to_rgb(image)
        Y, X = image.shape[:2]
        self._bgra = np.zeros((Y, X, 4), dtype=np.uint8, order='C')
        self._bgra[..., 0] = image[..., 2]
        self._bgra[..., 1] = image[..., 1]
        self._bgra[..., 2] = image[..., 0]
        qimage = QtGui.QImage(self._bgra.data, X, Y, QtGui.QImage.Format_RGB32)
        return qimage

    def show_video_images(self):
        # print(self.capture.pos,len(self.capture.data))
        success, frame = self.capture.read()
        if success:
            size = self.pictureLabel.size()
            height, width = size.height(), size.width()
            # frame = cv2.resize(frame, (width, height))
            temp_image = self.img2qimage(frame)
            temp_pixmap = QPixmap.fromImage(temp_image).scaled(width,height,Qt.KeepAspectRatio)
            self.pictureLabel.setPixmap(temp_pixmap)
        else:
            print("read failed, no frame data")
            success, frame = self.capture.read()
            if not success and self.video_type is VideoBox.VIDEO_TYPE_OFFLINE:
                print("play finished")  # 判断本地文件播放完毕
                self.reset()
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
            return

    def video_init(self):
        self.capture.open(self.video_obj)
        self.timer.start()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def toggle_video(self):
        self.timer.stop()
        fps = self.fps_spin.value()
        self.timer.set_fps(float(fps))
        if self.video_obj == "" or self.video_obj is None:
            return
        if self.status is VideoBox.STATUS_INIT:
            self.video_init()
        elif self.status is VideoBox.STATUS_PLAYING:
            self.timer.stop()
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.capture.release()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        elif self.status is VideoBox.STATUS_PAUSE:
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.capture.open(self.video_obj)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        self.status = (VideoBox.STATUS_PLAYING,
                       VideoBox.STATUS_PAUSE,
                       VideoBox.STATUS_PLAYING)[self.status]


class Communicate(QObject):
    signal = pyqtSignal(str)


class VideoTimer(QThread):

    def __init__(self, frequent=20):
        QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.timeSignal = Communicate()
        self.mutex = QMutex()

    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            self.timeSignal.signal.emit("1")
            time.sleep(1 / self.frequent)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def is_stopped(self):
        with QMutexLocker(self.mutex):
            return self.stopped

    def set_fps(self, fps):
        self.frequent = fps


def file2arrlist(fname):
    arrlist = []
    playCapture = cv2.VideoCapture()
    playCapture.open(fname)
    while True:
        success, frame = playCapture.read()
        if not success:
            break
        arrlist.append(frame)
    playCapture.release()
    return arrlist


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fileObj="slow_traffic_small.mp4"
    arrObj=file2arrlist(fileObj)
    box = VideoBox(arrObj)
    box.show()
    sys.exit(app.exec_())
