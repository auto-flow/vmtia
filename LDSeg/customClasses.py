# -*- coding: UTF-8 -*-

import pickle
from copy import deepcopy
from itertools import groupby
from pathlib import Path
from platform import platform
from PyQt5.QtWidgets import *  # QMessageBox,QFileDialog,QWidget,QApplication,QMainWindow,QSizePolicy
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

import cv2



class QImgComboBox(QComboBox):

    def __init__(self, parent=None, imgdata=None):
        super(QImgComboBox, self).__init__(parent)
        if imgdata is not None:
            self.name_list = [x['name'] for x in imgdata]
            self.addItems(self.name_list)
        else:
            self.addItem('current image')
            self.setEditable(False)


class QVideoComboBox(QComboBox):

    def __init__(self, parent=None, imgdata=()):
        super(QVideoComboBox, self).__init__(parent)
        self.name_list=[]
        self.index_list=[]
        for i,x in enumerate(imgdata):
            if isinstance(x.get('input', None),list):
                self.name_list.append(x['name'])
                self.index_list.append(i)
        self.addItems(self.name_list)


class QRectButton(QPushButton):
    def __init__(self, parent=None, rect=QRect(0, 0, 0, 0),imgdata=(),video_select:QVideoComboBox=None):
        super(QRectButton, self).__init__(parent)
        self.rect = rect
        self.setRectText()
        self.imgdata=imgdata
        self.video_selecter=video_select
        self.clicked.connect(self.onclick)

    def setRectText(self):
        rect = self.rect
        self.setText(str(rect.getRect()))


    def onclick(self, checked: bool = ...) -> None:
        raw_index=self.video_selecter.currentIndex()
        name=self.video_selecter.name_list[raw_index]
        index=self.video_selecter.index_list[raw_index]
        video=self.imgdata[index]['input']
        if video is None:
            return
        bbox = cv2.selectROI(video[0], False)
        cv2.destroyAllWindows()
        self.rect.setRect(*bbox)
        self.setRectText()