# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_pipeline.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1166, 692)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.QVBoxLayout = QtWidgets.QVBoxLayout()
        self.QVBoxLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.QVBoxLayout.setSpacing(12)
        self.QVBoxLayout.setObjectName("QVBoxLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_multi = QtWidgets.QLabel(self.centralwidget)
        self.label_multi.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_multi.setFont(font)
        self.label_multi.setStyleSheet("background-color:white")
        self.label_multi.setFrameShape(QtWidgets.QFrame.Box)
        self.label_multi.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_multi.setAlignment(QtCore.Qt.AlignCenter)
        self.label_multi.setObjectName("label_multi")
        self.verticalLayout_2.addWidget(self.label_multi)
        self.qlist_multi = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qlist_multi.sizePolicy().hasHeightForWidth())
        self.qlist_multi.setSizePolicy(sizePolicy)
        self.qlist_multi.setMaximumSize(QtCore.QSize(16777215, 100))
        self.qlist_multi.setFrameShape(QtWidgets.QFrame.Box)
        self.qlist_multi.setFrameShadow(QtWidgets.QFrame.Plain)
        self.qlist_multi.setObjectName("qlist_multi")
        self.verticalLayout_2.addWidget(self.qlist_multi)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet("background-color:white")
        self.label_6.setFrameShape(QtWidgets.QFrame.Box)
        self.label_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_2.addWidget(self.label_6)
        self.qlist_pipes = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qlist_pipes.sizePolicy().hasHeightForWidth())
        self.qlist_pipes.setSizePolicy(sizePolicy)
        self.qlist_pipes.setFrameShape(QtWidgets.QFrame.Box)
        self.qlist_pipes.setFrameShadow(QtWidgets.QFrame.Plain)
        self.qlist_pipes.setObjectName("qlist_pipes")
        self.verticalLayout_2.addWidget(self.qlist_pipes)
        self.cnnn = QtWidgets.QHBoxLayout()
        self.cnnn.setObjectName("cnnn")
        self.topo_button = QtWidgets.QPushButton(self.centralwidget)
        self.topo_button.setObjectName("topo_button")
        self.cnnn.addWidget(self.topo_button)
        self.verticalLayout_2.addLayout(self.cnnn)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.fuck = QtWidgets.QFormLayout()
        self.fuck.setObjectName("fuck")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.fuck.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.module_edit = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.module_edit.sizePolicy().hasHeightForWidth())
        self.module_edit.setSizePolicy(sizePolicy)
        self.module_edit.setReadOnly(True)
        self.module_edit.setObjectName("module_edit")
        self.fuck.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.module_edit)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.fuck.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.method_edit = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.method_edit.sizePolicy().hasHeightForWidth())
        self.method_edit.setSizePolicy(sizePolicy)
        self.method_edit.setReadOnly(True)
        self.method_edit.setObjectName("method_edit")
        self.fuck.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.method_edit)
        self.phase_edit = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.phase_edit.sizePolicy().hasHeightForWidth())
        self.phase_edit.setSizePolicy(sizePolicy)
        self.phase_edit.setReadOnly(True)
        self.phase_edit.setObjectName("phase_edit")
        self.fuck.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.phase_edit)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.fuck.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.verticalLayout.addLayout(self.fuck)
        self.param_edit = QtWidgets.QTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.param_edit.sizePolicy().hasHeightForWidth())
        self.param_edit.setSizePolicy(sizePolicy)
        self.param_edit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.param_edit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.param_edit.setReadOnly(True)
        self.param_edit.setObjectName("param_edit")
        self.verticalLayout.addWidget(self.param_edit)
        self.cmd_edit = QtWidgets.QTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmd_edit.sizePolicy().hasHeightForWidth())
        self.cmd_edit.setSizePolicy(sizePolicy)
        self.cmd_edit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.cmd_edit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.cmd_edit.setReadOnly(True)
        self.cmd_edit.setObjectName("cmd_edit")
        self.verticalLayout.addWidget(self.cmd_edit)
        self.attr_edit = QtWidgets.QTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.attr_edit.sizePolicy().hasHeightForWidth())
        self.attr_edit.setSizePolicy(sizePolicy)
        self.attr_edit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.attr_edit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.attr_edit.setReadOnly(True)
        self.attr_edit.setObjectName("attr_edit")
        self.verticalLayout.addWidget(self.attr_edit)
        self.sb = QtWidgets.QHBoxLayout()
        self.sb.setObjectName("sb")
        self.generate_button = QtWidgets.QPushButton(self.centralwidget)
        self.generate_button.setObjectName("generate_button")
        self.sb.addWidget(self.generate_button)
        self.generate_function_button = QtWidgets.QPushButton(self.centralwidget)
        self.generate_function_button.setObjectName("generate_function_button")
        self.sb.addWidget(self.generate_function_button)
        self.verticalLayout.addLayout(self.sb)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.shit = QtWidgets.QVBoxLayout()
        self.shit.setObjectName("shit")
        self.qlabel_image = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qlabel_image.sizePolicy().hasHeightForWidth())
        self.qlabel_image.setSizePolicy(sizePolicy)
        self.qlabel_image.setMinimumSize(QtCore.QSize(600, 600))
        self.qlabel_image.setMaximumSize(QtCore.QSize(10000, 10000))
        self.qlabel_image.setStyleSheet("background-color:white\n"
"")
        self.qlabel_image.setFrameShape(QtWidgets.QFrame.Box)
        self.qlabel_image.setFrameShadow(QtWidgets.QFrame.Plain)
        self.qlabel_image.setLineWidth(1)
        self.qlabel_image.setMidLineWidth(0)
        self.qlabel_image.setText("")
        self.qlabel_image.setObjectName("qlabel_image")
        self.shit.addWidget(self.qlabel_image)
        self.horizontalLayout.addLayout(self.shit)
        self.QVBoxLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.QVBoxLayout, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.RightToolBarArea, self.toolBar)
        self.actionopen = QtWidgets.QAction(MainWindow)
        self.actionopen.setObjectName("actionopen")
        self.actionopen_dir = QtWidgets.QAction(MainWindow)
        self.actionopen_dir.setObjectName("actionopen_dir")
        self.action = QtWidgets.QAction(MainWindow)
        self.action.setObjectName("action")
        self.action_2 = QtWidgets.QAction(MainWindow)
        self.action_2.setObjectName("action_2")
        self.action_3 = QtWidgets.QAction(MainWindow)
        self.action_3.setObjectName("action_3")
        self.action_4 = QtWidgets.QAction(MainWindow)
        self.action_4.setObjectName("action_4")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PipeLine Dialog"))
        self.label_multi.setText(_translate("MainWindow", "Multi Source"))
        self.qlist_multi.setToolTip(_translate("MainWindow", "图像处理流水线的各个结点"))
        self.label_6.setText(_translate("MainWindow", "Pipe Line"))
        self.qlist_pipes.setToolTip(_translate("MainWindow", "图像处理流水线的各个结点"))
        self.topo_button.setToolTip(_translate("MainWindow", "查看管道各个结点的拓扑结构图"))
        self.topo_button.setText(_translate("MainWindow", "Topological graph"))
        self.label.setText(_translate("MainWindow", "module"))
        self.module_edit.setToolTip(_translate("MainWindow", "当前结点的模块名"))
        self.label_2.setText(_translate("MainWindow", "method"))
        self.method_edit.setToolTip(_translate("MainWindow", "当前结点的方法名"))
        self.phase_edit.setToolTip(_translate("MainWindow", "当前结点的输出阶段"))
        self.label_3.setText(_translate("MainWindow", "phase"))
        self.param_edit.setToolTip(_translate("MainWindow", "当前结点的参数信息"))
        self.cmd_edit.setToolTip(_translate("MainWindow", "当前结点的命令"))
        self.attr_edit.setToolTip(_translate("MainWindow", "当前结点的图像属性信息"))
        self.generate_button.setToolTip(_translate("MainWindow", "将生成管道的命令流全部导出"))
        self.generate_button.setText(_translate("MainWindow", "Genetate Code"))
        self.generate_function_button.setText(_translate("MainWindow", "Genetate Function"))
        self.qlabel_image.setToolTip(_translate("MainWindow", "当前结点的输出图像"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionopen.setText(_translate("MainWindow", "打开文件"))
        self.actionopen_dir.setText(_translate("MainWindow", "打开文件夹"))
        self.action.setText(_translate("MainWindow", "关闭"))
        self.action_2.setText(_translate("MainWindow", "快捷键表"))
        self.action_3.setText(_translate("MainWindow", "使用手册"))
        self.action_4.setText(_translate("MainWindow", "关于我们"))


