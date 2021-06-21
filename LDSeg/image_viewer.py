# -*- coding: UTF-8 -*-

'''
图片控件库
实现了图片的放大，缩小，平移，还原
'''
from platform import platform

from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QSizePolicy

import numpy as np
from .utils import *
from imageio import imwrite


class ImageViewer:
    ''' Basic image viewer class to show an image with zoom and pan functionaities.
        Requirement: Qt's Qlabel widget name where the image will be drawn/displayed.
    '''

    def __init__(self, qlabel):
        self.qimage=None
        self.qlabel_image = qlabel  # widget/window name where image is displayed (I'm usiing qlabel)
        self.qimage_scaled = QImage()  # scaled image to fit to the size of qlabel_image
        self.qpixmap = QPixmap()  # qpixmap to fill the qlabel_image
        self.zoomX = 1  # zoom factor w.r.t size of qlabel_image
        self.position = [0, 0]  # position of top left corner of qimage_label w.r.t. qimage_scaled
        self.panFlag = False  # to enable or disable pan
        self.qlabel_image.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.pressed=None
        self.__connectEvents()

    def __connectEvents(self):
        # Mouse events
        self.qlabel_image.mousePressEvent = self.mousePressAction
        self.qlabel_image.mouseMoveEvent = self.mouseMoveAction
        self.qlabel_image.mouseReleaseEvent = self.mouseReleaseAction

    def onResize(self):
        ''' things to do when qlabel_image is resized '''
        self.qpixmap = QPixmap(self.qlabel_image.size())
        self.qpixmap.fill(QtCore.Qt.gray)
        self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX,
                                                self.qlabel_image.height() * self.zoomX,
                                                QtCore.Qt.KeepAspectRatio)
        self.update()


    def process(self,img):
        ans=img.astype('uint8')
        if get_config('imgAlwaysNormalize',True):
            return img_norm(ans)
        ans=img.copy()
        if img.max()<10:
            ans=img_norm(ans)
        return ans

    def loadImage(self, imageObj):
        ''' To load and display new image.'''
        if isinstance(imageObj, str):
            self.qimage = QImage(imageObj)
        elif isinstance(imageObj, np.ndarray):
            # 做一个判断处理
            imageObj=self.process(imageObj)
            if get_config('pyqtImgModel')=='file' or ('darwin' in platform().lower()):
                imwrite('.temp.jpg',imageObj)
                self.qimage = QImage('.temp.jpg')
            else:
                self.qimage = self.img2qimage(imageObj)
        else:
            raise AttributeError("imageObj must be a string of image path, or a ndarray image data")
        self.qpixmap = QPixmap(self.qlabel_image.size())
        if get_config('keepZoom'):
            pass
        else:
            self.zoomX=1
            self.position=[0,0]
        self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX,
                                                self.qlabel_image.height() * self.zoomX,
                                                QtCore.Qt.KeepAspectRatio)
        self.update()   # 不进行还原


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

    def update(self):
        ''' This function actually draws the scaled image to the qlabel_image.
            It will be repeatedly called when zooming or panning.
            So, I tried to include only the necessary operations required just for these tasks. 
        '''

        if not self.qimage_scaled.isNull():
            # check if position is within limits to prevent unbounded panning.
            px, py = self.position
            px = px if (px <= self.qimage_scaled.width() - self.qlabel_image.width()) else (
                        self.qimage_scaled.width() - self.qlabel_image.width())
            py = py if (py <= self.qimage_scaled.height() - self.qlabel_image.height()) else (
                        self.qimage_scaled.height() - self.qlabel_image.height())
            px = px if (px >= 0) else 0
            py = py if (py >= 0) else 0
            self.position = (px, py)

            if self.zoomX == 1:
                self.qpixmap.fill(QtCore.Qt.white)

            # the act of painting the qpixamp
            painter = QPainter()
            painter.begin(self.qpixmap)
            painter.drawImage(QtCore.QPoint(0, 0), self.qimage_scaled,
                              QtCore.QRect(self.position[0], self.position[1],
                            self.qlabel_image.width(),self.qlabel_image.height()))
            painter.end()

            self.qlabel_image.setPixmap(self.qpixmap)
        else:
            pass

    def mousePressAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        if self.panFlag:
            self.pressed = QMouseEvent.pos()  # starting point of drag vector
            self.anchor = self.position  # save the pan position when panning starts

    def mouseMoveAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        if self.pressed:
            dx, dy = x - self.pressed.x(), y - self.pressed.y()  # calculate the drag vector
            self.position = self.anchor[0] - dx, self.anchor[1] - dy  # update pan position using drag vector
            self.update()  # show the image with udated pan position

    def mouseReleaseAction(self, QMouseEvent):
        self.pressed = None  # clear the starting point of drag vector

    def zoomPlus(self):
        self.zoomX += 1
        px, py = self.position
        px += self.qlabel_image.width() / 2
        py += self.qlabel_image.height() / 2
        self.position = (px, py)
        self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX,
                                                self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
        self.update()

    def zoomMinus(self):
        if self.zoomX > 1:
            self.zoomX -= 1
            px, py = self.position
            px -= self.qlabel_image.width() / 2
            py -= self.qlabel_image.height() / 2
            self.position = (px, py)
            self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX,
                                                    self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
            self.update()

    def resetZoom(self):
        self.zoomX = 1
        self.position = [0, 0]
        self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX,
                                                self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
        self.update()

    def enablePan(self, value):
        self.panFlag = value
