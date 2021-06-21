# -*- coding: UTF-8 -*-

import pickle
from copy import deepcopy
from itertools import groupby
from pathlib import Path

from PyQt5.QtWidgets import *  # QMessageBox,QFileDialog,QWidget,QApplication,QMainWindow,QSizePolicy
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

# 导入功能类
import numpy as np
import sys, os
import cv2
from .utils import *
from . import globalvar
import json
import pandas as pd


class StrDialog(QDialog):
    def __init__(self, parent, name, value, comment):
        super(StrDialog, self).__init__(parent)
        self.setWindowTitle(name)
        vbox = QVBoxLayout()
        comment_edit = QTextEdit(self)
        comment_edit.setText(comment)
        comment_edit.setToolTip(f'输出阶段{name}的注释')
        comment_edit.setMaximumHeight(75)
        comment_edit.setReadOnly(True)
        vbox.addWidget(comment_edit)
        hbox = QHBoxLayout()
        button = QToolButton(self)
        button.setIcon(QIcon('res/icons/clipboard.png'))
        button.setToolTip('点击将值复制到剪切板')
        value_edit = QTextEdit(self)
        value_edit.setText(value)
        value_edit.setToolTip(f'输出阶段{name}的值')
        value_edit.setMaximumHeight(75)
        value_edit.setReadOnly(True)
        hbox.addWidget(button)
        hbox.addWidget(value_edit)
        vbox.addWidget(QLabel(f'输出阶段{name}的值'))
        vbox.addLayout(hbox)
        # buttonBox=QDialogButtonBox()
        # vbox.addWidget(buttonBox)
        self.setLayout(vbox)


class TabelDialog(QDialog):
    def __init__(self, parent, name, dataFrame: pd.DataFrame, comment):
        super(TabelDialog, self).__init__(parent)
        self.dataFrame = dataFrame
        self.setWindowTitle(name)
        vbox = QVBoxLayout()
        comment_edit = QTextEdit(self)
        comment_edit.setText(comment)
        comment_edit.setToolTip(f'输出阶段{name}的注释')
        comment_edit.setMaximumHeight(75)
        comment_edit.setReadOnly(True)
        vbox.addWidget(comment_edit)
        columns = list(dataFrame.columns)
        columns.insert(0, 'ID')
        table = QTableWidget(self)
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        values = dataFrame.values
        self.values = values
        table.setRowCount(len(dataFrame.index))
        for i, row in enumerate(values):
            for j, col in enumerate(np.insert(row, 0, i + 1, 0)):
                table.setItem(i, j, QTableWidgetItem(str(col)))
        table.setToolTip(f'输出阶段{name}的值')

        hbox = QHBoxLayout()
        button = QPushButton(self)
        button.setToolTip('点击导出表格')
        button.setText('导出')
        button.clicked.connect(self.export)
        hbox.addWidget(button)
        vbox.addWidget(QLabel(f'输出阶段{name}的值'))
        vbox.addWidget(table)
        vbox.addLayout(hbox)
        # buttonBox=QDialogButtonBox()
        # vbox.addWidget(buttonBox)
        self.setLayout(vbox)

    def export(self):
        typeList = ['CSV Files (*.csv)', 'XLSX Files (*.xlsx)', 'All Files (*)']
        filename, filetype = QFileDialog.getSaveFileName(self, 'save file',
                                                         os.getcwd() + '/untitle.csv',
                                                         ";;".join(typeList),
                                                         typeList[0])
        if not filename:
            return
        p = Path(filename)
        if filetype == typeList[1]:
            savePath = str(p.parent / f'{p.stem}.xlsx')
            self.dataFrame.to_excel(savePath, index=True)
        else:
            savePath = str(p.parent / f'{p.stem}.csv')
            self.dataFrame.to_csv(savePath)


class TifChannelDialog(QDialog):
    def __init__(self,parent,path_list,max_channel):
        super(TifChannelDialog, self).__init__(parent)
        self.setWindowTitle('tiff channel choose dialog')
        vbox = QVBoxLayout(self)
        path_list_widget=QListWidget(self)
        path_list_widget.addItems(path_list)
        vbox.addWidget(path_list_widget)
        path_list_widget.setToolTip(f'最大通道数为{max_channel}的tiff文件的路径列表')
        hbox = QHBoxLayout(self)
        label=QLabel(self)
        label.setText('choose channel')
        self.channel_com=QComboBox(self)
        self.channel_com.addItems([str(i) for i in range(max_channel)])
        self.channel_com.setToolTip('choose which channel you want')
        hbox.addWidget(label)
        hbox.addWidget(self.channel_com)
        ok=QPushButton(self)
        ok.setText('确定')
        vbox.addLayout(hbox)
        vbox.addWidget(ok)
        self.setLayout(vbox)
        ok.clicked.connect(self.close)
        self.channel_com.currentIndexChanged.connect(self.setChannel)
        self.channel=0

    def setChannel(self):
        self.channel=self.channel_com.currentIndex()