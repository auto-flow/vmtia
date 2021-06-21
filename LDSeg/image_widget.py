# -*- coding: UTF-8 -*-
import numpy
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *  # QMessageBox,QFileDialog,QWidget,QApplication,QMainWindow,QSizePolicy
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from .image_viewer import ImageViewer
from imageio import imwrite
import cv2, os
import pylab as plt
from .utils import *


class ImageWidget(object):

    def __init__(self, MainWindow, qlabel_image:QLabel):
        # 当前图片
        self.MainWindow = MainWindow
        self.cur_img = None
        self.image_viewer = ImageViewer(qlabel_image)

        self.action_plus = QtWidgets.QAction(MainWindow)
        self.action_plus.setIcon(QIcon('res/icons/zoom_plus.png'))
        self.action_plus.setShortcut(QKeySequence("Ctrl+="))
        self.action_plus.setToolTip("放大  <U>(Ctrl+\"+\")</U>")
        self.action_plus.setText("放大")

        self.action_minus = QtWidgets.QAction(MainWindow)
        self.action_minus.setIcon(QIcon('res/icons/zoom_minus.png'))
        self.action_minus.setShortcut(QKeySequence("Ctrl+-"))
        self.action_minus.setToolTip("缩小  <U>(Ctrl+\"-\")</U>")
        self.action_minus.setText("缩小")

        self.action_move = QtWidgets.QAction(MainWindow)
        self.action_move.setIcon(QIcon('res/icons/move.png'))
        self.action_move.setToolTip("拖动图片")
        self.action_move.setText("拖动")

        self.action_reset = QtWidgets.QAction(MainWindow)
        self.action_reset.setIcon(QIcon('res/icons/reset.png'))
        self.action_reset.setToolTip("还原图片大小")
        self.action_reset.setText("还原")

        self.action_save = QtWidgets.QAction(MainWindow)
        self.action_save.setIcon(QIcon('res/icons/save_im.png'))
        self.action_save.setShortcut(QKeySequence("Ctrl+S"))
        self.action_save.setToolTip("保存当前图片  <U>(Ctrl+\"S\")</U>")
        self.action_save.setText("保存")

        self.action_plt = QtWidgets.QAction(MainWindow)
        self.action_plt.setIcon(QIcon('res/icons/pyplot.png'))
        self.action_plt.setToolTip("用matplotlib.pyplot.imshow展示图片")
        self.action_plt.setText("pyplot")

        self.action_plus.triggered.connect(self.image_viewer.zoomPlus)
        self.action_minus.triggered.connect(self.image_viewer.zoomMinus)
        self.action_reset.triggered.connect(self.image_viewer.resetZoom)
        self.action_move.triggered.connect(self.move_image)
        self.action_save.triggered.connect(self.saveImg)
        self.action_plt.triggered.connect(self.imshow)
        # 设置图像控件右键菜单
        self.qlabel_image=qlabel_image
        self.qlabel_image.setContextMenuPolicy(Qt.CustomContextMenu)
        self.qlabel_image.setContextMenuPolicy(Qt.CustomContextMenu)
        self.qlabel_image.contextMenu = QMenu(MainWindow)
        self.qlabel_image.contextMenu.addAction(self.action_plus)
        self.qlabel_image.contextMenu.addAction(self.action_minus)
        self.qlabel_image.contextMenu.addAction(self.action_move)
        self.qlabel_image.contextMenu.addAction(self.action_reset)
        self.qlabel_image.contextMenu.addAction(self.action_save)
        self.qlabel_image.contextMenu.addAction(self.action_plt)
        self.qlabel_image.customContextMenuRequested.connect(self.show_image_label_menu)

    def show_image_label_menu(self):
        self.qlabel_image.contextMenu.popup(QCursor.pos())  # 菜单显示的位置
        self.qlabel_image.contextMenu.show()

    def load_image(self, img):
        self.image_viewer.loadImage(img)
        self.cur_img = img

    def saveImg(self):
        '''保存图片'''
        if self.cur_img is None:
            return

        filename, filetype = QFileDialog.getSaveFileName(self.MainWindow, 'save file',
                                                  get_default_dir("saveImg") + '/untitle.jpg',
                                                  ";;".join(image_types),
                                                  image_types[0])

        if filename is None or not filename:
            return
        set_default_dir("saveImg",filename)
        if filetype==image_types[3]:
            numpy.save(filename,self.cur_img)
        else:
            imwrite(filename, self.cur_img)

    def resizeEvent(self, evt):
        '''窗体大小改变时间'''
        if self.image_viewer.qimage is not None:
            self.image_viewer.onResize()

    def move_image(self):
        '''拖动图片'''
        self.image_viewer.enablePan(True)

    def imshow(self):
        if isinstance(self.cur_img,np.ndarray):
            plt.imshow(self.cur_img)
            plt.show()
