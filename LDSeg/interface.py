# -*- coding: UTF-8 -*-
'''
主界面
'''

# 导入PyQt
import pickle
from copy import deepcopy
from itertools import groupby
from pathlib import Path
from platform import platform

from PIL import Image
from PyQt5.QtWidgets import *  # QMessageBox,QFileDialog,QWidget,QApplication,QMainWindow,QSizePolicy
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

# 导入界面类
import warnings

from .image_viewer import ImageViewer
from .ui_interface import Ui_MainWindow
from .savebatch_dialog import SavebatchDialog
from .image_widget import ImageWidget
# 导入功能类
import numpy as np
import sys, os
import cv2
from .utils import *
from .cmd_manage import *
from . import globalvar
import json
import pandas as pd
from .videoBox import VideoBox
from .customDialog import *
from .customClasses import *

if get_config('productType', 'container') == 'tool':
    from .pipeline_dialog import PipelineDialog

globalvar._init()


class MyMainWindow(QMainWindow, Ui_MainWindow, ImageWidget):

    # --------------------------初始化部分-------------------------------------

    def __init__(self, parent=None):
        '''
        窗口初始化
        '''
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)

        ImageWidget.__init__(self, self, self.qlabel_image)
        # 初始化一些数据
        self.init_data()
        # 生成调参界面
        self.generate_paramColumn()
        self.init_statusbar()
        # 以最大化形式展示
        self.showMaximized()
        # 自动加载工作空间
        if get_config('autoSave'):
            savePath = get_config('savePath')
            if os.path.exists(savePath):
                try:
                    self.import_workspace_file(savePath)
                except Exception as e:
                    warn(str(e) + f'\n不能导入工作空间\n{str(e)}', True)
            else:
                warn('savePath of config.json is invalid')
        # 初始化一些工具栏
        self.init_toolBar()
        # 绑定控件事件
        self.create_connection()

    def init_statusbar(self):
        self.statusbar1 = QLabel('Image information')
        self.statusbar1.setFrameStyle(QFrame.Plain)
        self.statusbar2 = QLabel('Output annotation')
        self.statusbar1.setFrameStyle(QFrame.Plain)
        self.statusbar.addPermanentWidget(self.statusbar1, 1)
        self.statusbar.addPermanentWidget(self.statusbar2, 2)

    def init_data(self):
        '''
        初始化一些数据
        '''
        # 设置程序图标
        self.setWindowIcon(QIcon('./res/logo.png'))
        self.setWindowTitle(get_config('title'))
        # self.imgdata是数据列表，列表的每一项是一个字典，保存打开的图片对应的数据
        self.imgdata = []
        # self.cur_phase 当前的状态
        self.cur_phase = 'input'
        # 调参区域所有控件列表（保存起来用来销毁和再生）
        self.widget_list = []
        # 当前函数名（调参界面解析的目标函数）
        self.method = None
        # 当前模块名
        self.module = None
        # 打开图片的路径集合
        self.path_set = set()
        # 设置快捷键
        self.set_shortcut()
        # 无模式对话框列表
        self.dlg_list = []
        # 历史记录用于切换
        self.history_images_row = []
        self.history_phases_index = []
        # 输出阶段对应的type
        self.phase2type = {}
        # 把主窗口的指针保存起来
        globalvar.set_value('MainWindow', self)
        # 图片列表最小宽度
        self.image_list.setMinimumWidth(get_config('listWidgetWidth', 200))
        # 初始化状态树
        self.inputItem = QTreeWidgetItem(self.phase_tree)
        self.inputItem.setText(0, 'input')
        self.inputItem.setIcon(0, QIcon('res/icons/input.png'))
        self.outputItem = QTreeWidgetItem(self.phase_tree)
        self.outputItem.setText(0, 'output')
        self.outputItem.setIcon(0, QIcon('res/icons/output.png'))
        self.phase_tree.addTopLevelItems([self.inputItem, self.outputItem])
        # 添加视频控件
        self.videoBox = VideoBox(self)
        self.videoBox.hide()
        self.imageLayout.addWidget(self.videoBox)

    def init_toolBar(self):
        # 添加一些工具栏控件
        self.action_savebat = QAction(self)
        self.action_savebat.setIcon(QIcon('res/icons/save_bat.png'))
        self.action_savebat.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.action_savebat.setToolTip("将工作空间中所有图片进行批处理后保存 <U>Ctrl+Shift+S</U>")
        self.action_savebat.setText("批量保存")

        self.action_import = QAction(self)
        self.action_import.setIcon(QIcon('res/icons/import.png'))
        self.action_import.setShortcut(QKeySequence("Ctrl+I"))
        self.action_import.setText('导入')
        self.action_import.setToolTip("导入<U>*.pkl</U>文件中的数据到当前工作空间中<br><U>(Ctrl+I)</U>")
        self.action_export = QAction(self)

        self.action_export.setIcon(QIcon('res/icons/export.png'))
        self.action_export.setShortcut(QKeySequence("Ctrl+E"))
        self.action_export.setText('导出')
        self.action_export.setToolTip("将当前工作空间的数据中导出到<U>*.pkl</U>文件中<U>(Ctrl+E)</U>")

        self.action_setting = QAction(self)
        self.action_setting.setIcon(QIcon('res/icons/setting.png'))
        self.action_setting.setShortcut(QKeySequence("Ctrl+Alt+S"))
        self.action_setting.setToolTip("设置")
        self.action_setting.setText("设置")

        self.action_clear = QAction(self)
        self.action_clear.setIcon(QIcon('res/icons/clear.png'))
        self.action_clear.setShortcut(QKeySequence("Ctrl+Alt+C"))
        self.action_clear.setToolTip("清空工作空间")
        self.action_clear.setText("清空工作空间")



        # 初始化工具栏
        self.toolBar.addAction(self.action_savebat)
        self.toolBar.addAction(self.action_save)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_plus)
        self.toolBar.addAction(self.action_minus)
        self.toolBar.addAction(self.action_reset)
        self.toolBar.addAction(self.action_move)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_import)
        self.toolBar.addAction(self.action_export)
        self.toolBar.addAction(self.action_setting)
        self.toolBar.addAction(self.action_clear)
        # 将一些action添加到主菜单
        self.menu_file.addAction(self.action_setting)
        self.menu_workspace.addAction(self.action_import)
        self.menu_workspace.addAction(self.action_export)
        self.menu_workspace.addAction(self.action_clear)
        self.menu_image.addAction(self.action_plus)
        self.menu_image.addAction(self.action_minus)
        self.menu_image.addAction(self.action_move)
        self.menu_image.addAction(self.action_reset)
        self.menu_image.addAction(self.action_save)
        self.menu_image.addAction(self.action_savebat)
        self.menu_image.addAction(self.action_plt)
        # 帮助文档
        self.menu_help=QAction(self)
        self.menu_help.setText('帮助')
        self.menubar.addAction(self.menu_help)
        # 图片右键菜单再增加一个控件
        self.qlabel_image.contextMenu.addAction(self.action_savebat)
        # disable
        if not get_config('supportVideo', False):
            self.menu_open_video.setEnabled(False)

    def set_shortcut(self):
        # self.zoom_plus.setShortcut(QKeySequence("Ctrl+="))
        # self.zoom_minus.setShortcut(QKeySequence("Ctrl+-"))
        self.action_open_dir.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self.action_open.setShortcut(QKeySequence("Ctrl+O"))
        # self.save_im.setShortcut(QKeySequence("Ctrl+S"))
        # self.save_bat.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.action_toggle_phase.setShortcut(QKeySequence("Ctrl+Tab"))
        self.action_toggle_image.setShortcut(QKeySequence("Ctrl+Shift+Tab"))
        self.action_select_input.setShortcut(QKeySequence("Alt+I"))

    def create_connection(self):
        '''
        绑定控件事件
        '''
        # 打开文件夹按钮
        self.open_folder.clicked.connect(self.open_dir_img)
        # 打开文件按钮
        self.open_file.clicked.connect(self.open_file_img)
        # 图片文件列表点击
        self.image_list.currentRowChanged.connect(self.image_list_change)
        # 处理阶段列表点击
        self.phase_tree.currentItemChanged.connect(self.phase_tree_change)
        self.phase_tree.itemClicked.connect(self.phase_tree_change)

        # 主菜单
        self.action_savebat.triggered.connect(self.save_batch)
        self.action_import.triggered.connect(self.open_pkl)
        self.action_export.triggered.connect(self.save_pkl)
        self.action_setting.triggered.connect(self.setting)
        self.action_open.triggered.connect(self.open_file_img)
        self.action_open_dir.triggered.connect(self.open_dir_img)
        self.action_close.triggered.connect(self.close)
        self.action_toggle_image.triggered.connect(self.toggle_image)
        self.action_toggle_phase.triggered.connect(self.toggle_phase)
        self.action_select_input.triggered.connect(self.select_inputItem)
        self.action_clear.triggered.connect(self.clear_workspace)
        self.action_open_mulimg.triggered.connect(self.open_mulimg)
        self.action_open_video.triggered.connect(self.open_video)
        self.menu_help.triggered.connect(self.get_help)
        # 设置图片列表右键菜单
        self.image_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_list.customContextMenuRequested.connect(self.show_image_list_menu)
        # 设置阶段输出列表右键菜单
        self.phase_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.phase_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.phase_tree.customContextMenuRequested.connect(self.show_phase_tree_menu)

    def get_help(self):
        clickfile(Path('res')/'doc'/'index.html')

    def add_modeless_dialog(self, obj):
        # todo: 怎样才能判断对话框关闭，然后释放内存
        self.dlg_list.append(obj)
        obj.show()

    def setting(self):
        # 打开设置文件夹
        dpath = Path('config')
        with open((dpath / 'main.json'), 'r', encoding='utf8') as f:
            configFile = json.load(f)["configFile"]
        fpath = dpath / configFile
        clickfile(fpath)
        if 'windows' in platform().lower():
            convertToCRLF(dpath.as_posix())

    def set_status_bar(self):
        msg = ''
        for k, v in self.img_attr.items():
            msg += f'{k} = {v}    '
        self.statusbar1.setText(msg)

    # --------------------------文件打开与保存功能-------------------------------------

    def get_dir_img(self, folder):
        ''' Get the names and paths of all the images in a directory. '''
        image_list = []
        channel=-1
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                im_path = os.path.join(folder, file)
                # 处理tiff
                # if Path(im_path).suffix in ('.tif','.tiff'):
                #     if channel==-1:
                #         tiff = Image.open(im_path)
                #         tiffs = get_tiff_channel(tiff)
                #         max_channel = len(tiffs)
                #         channel = self.choose_channel(im_path, max_channel)
                #         input = tiffs[channel]
                #     else:
                #         tiff = Image.open(im_path)
                #         tiffs = get_tiff_channel(tiff)
                #         input = tiffs[channel]
                # else:
                #     input=None
                input=None
                image_obj = self.get_file_img(im_path,input)
                if image_obj:
                    image_list.append(image_obj)
        return image_list

    def get_file_img(self, im_path,input=None):
        ''' Get the names and paths of all the images in a specific file. '''
        image_obj = {}
        if im_path.upper().endswith(VALID_FORMAT):
            # im_data = load_img(im_path)
            file = os.path.split(im_path)[-1]
            # todo: 通过lazy的方式加载图片
            image_obj = {
                'name': file,
                'path': im_path,
                'input': input,
                'ndim': input.ndim if input is not None else None
            }
        return image_obj

    def open_dir_img(self):
        '''
        打开图片文件夹
        '''
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", get_default_dir("open_dir_img"))
        if not folder:
            warn('Please select a valid Folder')
            return
        set_default_dir("open_dir_img", folder)
        imgdata = self.get_dir_img(folder)
        valid_data = imgdata  # list(filter(self.__validate_imgdata, imgdata))
        if len(valid_data) > 0:
            # self.imgdata += valid_data
            for data in valid_data:
                self.add_imageitem(data)

    def choose_channel(self,fileDir,max_channel):

        channel = 0
        dlg = TifChannelDialog(self, [fileDir],max_channel )
        dlg.exec()
        channel = dlg.channel
        return channel

    def open_file_img(self):
        '''
        打开文件
        '''
        fileDir, filetype = QFileDialog.getOpenFileName(self,
                                                        "Select File",
                                                        get_default_dir('open_file_img'),
                                                        "All Files (*)")

        if not fileDir:
            return
        set_default_dir('open_file_img', fileDir)

        type = Path(fileDir).suffix

        # 处理tiff通道
        # if type in ( '.tif','.tiff'):
        #     tiff = Image.open(fileDir)
        #     tiffs = get_tiff_channel(tiff)
        #     max_channel=len(tiffs)
        #     channel=self.choose_channel(fileDir,max_channel)
        #     input=tiffs[channel]
        # else:
        #     input = None
        input=None
        data=self.get_file_img(fileDir,input)
        if not data :
            return
        # if self.__validate_imgdata(data):
        # self.imgdata.append(data)
        self.add_imageitem(data)

    def open_mulimg(self):
        fileDirs, filetype = QFileDialog.getOpenFileNames(self,
                                                          "Select Files",
                                                          get_default_dir("open_mulimg"),
                                                          ";;".join(image_types))
        if fileDirs is None or not fileDirs:
            return
        set_default_dir("open_mulimg",fileDirs[0])
        video = [load_img(fileDir) for fileDir in fileDirs]
        self.add_imageitem({
            'name': str(Path(fileDirs[0]).name) + f"_x{len(video)}",
            'path': str(Path(fileDirs[0]).parent),
            'input': video
        })

    def open_video(self):

        fileDir, filetype = QFileDialog.getOpenFileName(self,
                                                        "Select File",
                                                        get_default_dir("open_video"),
                                                        ";;".join(video_types))
        if fileDir is None or not fileDir:
            return
        set_default_dir("open_video",fileDir)
        arrlist = vediofile_to_arrlist(fileDir)
        self.add_imageitem({
            'name': str(Path(fileDir).name),
            'path': fileDir,
            'input': arrlist
        })

    def open_pkl(self):
        fileDir, filetype = QFileDialog.getOpenFileName(self,
                                                        "Select File",
                                                        get_default_dir("open_pkl"),
                                                        "Python Pickle Files (*.pkl);;All Files (*)")
        if not fileDir or not os.path.exists(fileDir):
            return
        set_default_dir("open_pkl",fileDir)
        self.import_workspace_file(fileDir)

    def save_pkl(self):
        fileDir, filetype = QFileDialog.getSaveFileName(self, 'Save File',
                                                        get_default_dir("save_pkl") + '/workspace.pkl',
                                                        "Python Pickle Files (*.pkl);;All Files (*)")
        if not fileDir:
            return
        set_default_dir("save_pkl",fileDir)
        self.export_workspace_file(fileDir)

    def save_batch(self):
        save_dlg = globalvar.get_value('save_dlg')
        # 对图片列表进行异常判断
        if len(self.imgdata)==0:
            warn('请先导入图片数据。批量保存失败', True)
            return
        globalvar.set_value('imgdata', self.imgdata)
        # 对输出阶段树进行异常判断
        phase_tree=self.get_phase_dict()
        cache_path = Path('config') / 'phase_tree.json'
        if not phase_tree:
            if cache_path.exists():
                with open(cache_path.as_posix(),'r') as f:
                    phase_tree=json.load(f)
            else:
                ret=self.apply_param()
                if not ret:
                    warn('参数应用失败，不能获取phase_tree数据，批量保存失败',True)
                    return
                phase_tree = self.get_phase_dict()
        with open(cache_path.as_posix(), 'w+') as f:
            json.dump(phase_tree,f)
        globalvar.set_value('phase_tree', phase_tree)
        # 载入界面
        save_dlg.view()

    # --------------------------工作空间相关函数-------------------------------------

    def clear_workspace(self):
        self.cur_phase = 'input'
        self.method = 'input'
        self.phase_name = 'input'
        self.imgdata = []
        self.load_imgdata_to_list()
        for i in range(self.outputItem.childCount()):
            self.outputItem.removeChild(self.outputItem.child(0))

    def import_workspace_file(self, fname):
        with open(fname, 'rb') as f:
            data = pickle.load(f)
        self.clear_workspace()
        self.imgdata = data.get('imgdata', [])
        phase_dict = data.get('phase_dict', {})
        self.phase2type = data.get('phase2type', {})
        self.module = data.get('module_name', None)
        self.module_selecter.setCurrentText(self.module)
        n = len(self.imgdata)
        if n:
            self.load_imgdata_to_list()
            self.set_phase_dict(phase_dict)
            self.phase_tree.expandAll()

    def export_workspace_file(self, fname):
        data = {
            'imgdata': self.imgdata,
            'phase_dict': self.get_phase_dict(),
            'module_name': self.module,
            'phase2type': self.phase2type,
        }
        with open(fname, 'wb') as f:
            pickle.dump(data, f, protocol=2)

    # -----------------------图像列表 相关事件-------------------------------------
    def load_img_icon(self, data):
        gray = QIcon('res/icons/gray.png')
        rgb = QIcon('res/icons/rgb.png')
        video = QIcon('res/icons/cvideo.png')
        if isinstance(data['input'], list):
            return video
        if 'ndim' not in data or data['ndim'] is None:
            return None
        else:
            if data['ndim'] == 2:
                return gray
            else:
                return rgb

    def toggle_image(self):
        try:
            if len(self.history_images_row) >= 2:
                self.history_images_row = [x[0] for x in groupby(self.history_images_row)]
                row = self.history_images_row[-2]
                self.image_list.setCurrentRow(row)
                self.history_images_row = self.history_images_row[-2:]
        except Exception as e:
            warn(e)

    def show_image_list_menu(self):
        table = self.image_list
        table.contextMenu = QMenu(self)
        action1 = table.contextMenu.addAction(u'删除表项')
        action1.triggered.connect(self.remove_current_imageitem)
        if get_config('productType', 'container') == 'tool':
            action2 = table.contextMenu.addAction(u'查看结点')
            action2.triggered.connect(self.view_node("image"))
        table.contextMenu.popup(QCursor.pos())  # 菜单显示的位置
        table.contextMenu.show()

    def remove_current_imageitem(self):
        row = self.image_list.currentRow()
        self.remove_imageitem(row)
        pass

    def add_imageitem(self, data):
        self.imgdata.append(data)
        item = QListWidgetItem(data['name'])
        icon = self.load_img_icon(data)
        if icon is not None:
            item.setIcon(icon)
        self.image_list.addItem(item)

    def remove_imageitem(self, row):
        if not 0 <= row < self.image_list.count():
            return
        item = self.image_list.takeItem(row)
        item = None
        del self.imgdata[row]

    def load_imgdata_to_list(self):
        self.image_list.clear()
        for data in self.imgdata:
            item = QListWidgetItem(data['name'])
            icon = self.load_img_icon(data)
            if icon is not None:
                item.setIcon(icon)
            self.image_list.addItem(item)
        self.image_viewer.enablePan(True)
        if len(self.imgdata) > 0:
            item = self.imgdata[0]
            self.load_object(get_imgdata_input(item))

    def image_list_change(self, row):
        if not 0 <= row < len(self.imgdata):
            return
        it = self.imgdata[row]
        self.load_object(self.get_imgdata_value(it))
        if self.image_list.item(row).icon().isNull():
            self.image_list.item(row).setIcon(self.load_img_icon(it))
        self.history_images_row.append(row)

    # -----------------------输出阶段树 相关事件-------------------------------------

    def toggle_phase(self):
        try:
            if len(self.history_phases_index) >= 2:
                self.history_phases_index = [x[0] for x in groupby(self.history_phases_index)]
                index = self.history_phases_index[-2]
                self.phase_tree.setCurrentIndex(index)
                self.history_phases_index = self.history_phases_index[-2:]
        except Exception as e:
            warn(e)
        pass

    def show_phase_tree_menu(self):
        table = self.phase_tree
        table.contextMenu = QMenu(self)
        action1 = table.contextMenu.addAction(u'删除表项')
        action1.triggered.connect(self.remove_current_phaseitem)
        if get_config('productType', 'container') == 'tool':
            action2 = table.contextMenu.addAction(u'查看结点')
            action2.triggered.connect(self.view_node('phase'))
            action4 = table.contextMenu.addAction(u'移至上层')
            action4.triggered.connect(self.moveto_imagelist)
        table.contextMenu.popup(QCursor.pos())  # 菜单显示的位置
        table.contextMenu.show()

    def remove_current_phaseitem(self):
        item = self.phase_tree.selectedItems()[0]
        item.parent().removeChild(item)

    def get_phase_dict(self):
        root = self.outputItem
        ans = {}

        def recursion(item: QTreeWidgetItem, data: dict):
            n = item.childCount()
            for i in range(n):
                child = item.child(i)
                name = child.data(0, 0)
                data[name] = {}
                recursion(child, data[name])

        recursion(root, ans)
        return ans

    def set_phase_dict(self, data):
        path = []

        def recursion(data: dict):
            if not data:
                self.add_leaf(path)
                return
            for name in data.keys():
                path.append(name)
                recursion(data[name])
                path.pop()

        recursion(data)
        # recursion(root, data, 0)

    def phase_tree_change(self, item, prev):
        '''响应输出阶段树改变'''
        index = self.phase_tree.indexFromItem(item)
        self.history_phases_index.append(index)
        absPath = self.getAbsPath(index)
        row = self.image_list.currentRow()
        if not 0 <= row < len(self.imgdata):
            return
        img_item = self.imgdata[row]
        if len(absPath) == 4 and absPath[0] == 'output':
            _, module_name, method_name, phase = absPath
            self.cur_phase = phase
            self.module = module_name
            if self.method != method_name:
                self.method = method_name
                self.generate_paramColumn(self.module, self.method)
            self.load_object(self.get_imgdata_value(img_item))
        else:
            self.load_object(get_imgdata_input(img_item))
            self.cur_phase = 'input'

    # -----------------------输出阶段树 叶子结点相关操作-------------------------------------

    def select_leaf(self, leaf_path):
        self.phase_tree.clearSelection()
        root = self.outputItem  # self.phase_tree.topLevelItem(1)
        for index, node in enumerate(leaf_path):
            for i in range(root.childCount()):
                if root.child(i).data(0, 0) == node:
                    root = root.child(i)
                    break
        root.setSelected(True)
        self.phase_tree.setCurrentItem(root)

    def select_inputItem(self):
        self.phase_tree.clearSelection()
        self.inputItem.setSelected(True)
        self.phase_tree.setCurrentItem(self.inputItem)

    def add_leaf(self, leaf_path):
        if len(leaf_path) != 3:
            return
        iconlist = ['module', 'method']
        phase_type = self.phase2type.get(tuple(leaf_path), None)
        if phase_type == np.ndarray:
            iconlist.append('imagePhase')
        elif phase_type == pd.DataFrame:
            iconlist.append('tablePhase')
        elif phase_type == list:
            iconlist.append('videoPhase')
        else:
            iconlist.append('strPhase')

        def build(root, name, hit, new_root, index):
            nonlocal iconlist
            if not hit:
                child = QTreeWidgetItem(root)
                child.setText(0, name)
                icon = QIcon(f'res/icons/{iconlist[index]}.png')
                child.setIcon(0, icon)
                return child
            return new_root

        root = self.outputItem  # self.phase_tree.topLevelItem(1)
        # module, method, phase = leaf_path
        # module
        for index, node in enumerate(leaf_path):
            hit, new_root = False, None
            for i in range(root.childCount()):
                if root.child(i).data(0, 0) == node:
                    hit = True
                    new_root = root.child(i)
                    break
            new_root = build(root, node, hit, new_root, index)
            root = new_root

    def getAbsPath(self, index):
        ans = []
        while index.isValid():
            ans.insert(0, index.data())
            index = index.parent()
        return ans

    # -----------------------图片显示区域相关事件-------------------------------------
    def load_object(self, obj):
        try:
            comment = self.return_comment[self.cur_phase]

        except Exception as e:
            comment = '当前输出阶段无注释'
        if isinstance(obj, np.ndarray):
            self.videoBox.hide()
            self.qlabel_image.show()
            ImageWidget.load_image(self, obj)
            self.img_attr = get_img_attr(obj)
            self.set_status_bar()
            self.qlabel_image.setToolTip(comment)
            self.statusbar2.setText(comment)

        elif isinstance(obj, str) or isinstance(obj, int) or isinstance(obj, float):
            StrDialog(self, self.cur_phase, str(obj), comment).exec()
        elif isinstance(obj, pd.DataFrame):
            TabelDialog(self, self.cur_phase, obj, comment).exec()
        elif isinstance(obj, list):
            try:
                self.cur_img = obj
            except Exception as e:
                warn(e)
            self.img_attr = get_img_attr(obj)
            self.set_status_bar()
            self.videoBox.video_obj = obj
            self.videoBox.setup_object()
            self.qlabel_image.hide()
            self.videoBox.show()

    def get_imgdata_value(self, item):
        if self.cur_phase == 'input':
            return get_imgdata_input(item)
        if not os.path.exists(f'cmd/{self.module}/{self.method}.py'):
            self.apply_param()
        try:
            self.statusbar1.setText('正在进行图像运算，请耐心等待')
            value = get_imgdata_value(item, self.module, self.method, self.cur_phase, self.imgdata)
            return value
        except Exception as e:
            info = str(e) + f'\n数据获取错误\n数据获取路径' \
                f'{self.module}/{self.method}/{self.cur_phase}可能已经失效\n{str(e)}'
            warn(info, True)
            return None

    # -----------------------参数设置区相关函数-------------------------------------

    def get_params_dict(self):
        '''
        根据调参控件列表获取参数字典
        '''
        # 需要返回的参数字典
        params_dict = {}
        # 对于调参区域参数容器列表中的每一项
        for item in self.param_widget_list:
            # QWidget对象
            widget = item['widget']
            # 参数名
            name = item['name']
            # 依据QWidget对象不同的类型，调用不同的方法获取控件中的值
            if isinstance(widget, QSpinBox):
                # 整数微调框
                params_dict[name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                # 小数微调框
                params_dict[name] = widget.value()
            elif isinstance(widget, QLineEdit):
                # 文本框
                params_dict[name] = widget.text()
            elif isinstance(widget, QCheckBox):
                # 选择框
                params_dict[name] = True if widget.checkState() == Qt.Checked else False
            elif isinstance(widget, QImgComboBox):  # and multiImg
                # 图片选择器
                if not widget.isEnabled():
                    value = self.image_list.currentRow()
                else:
                    value = widget.currentIndex()
                if 'multiImg' not in params_dict:
                    params_dict['multiImg'] = []
                params_dict['multiImg'].append((name, value))
            elif isinstance(widget, QComboBox):
                # 下拉列表
                params_dict[name] = widget.currentText()
        return params_dict

    def load_param(self):
        '''获取参数缓存'''
        path = Path('./param_cache')
        module_dir = path / self.module
        method_dir = module_dir / f'{self.method}.json'
        module_dir.mkdir(parents=True, exist_ok=True)
        if not method_dir.exists():
            return {}
        try:
            with open(str(method_dir), 'r', encoding='utf8') as f:
                return json.load(f)
        except Exception as e:
            warn(e)
            return {}

    def apply_param(self)->bool:
        '''
        在调参控件区域中完成调参后，应用参数到图片中
        '''
        # 处理不导入图片就应用参数的异常
        if len(self.imgdata) <= 0:
            warn('请先导入图片', True)
            return False
        # 从模块选择器和方法选择器中选取
        self.method = self.method_selecter.currentText()
        self.module = self.module_selecter.currentText()
        if self.method == 'input':
            warn('self.method_name cannot be `input`')
            return False
        # 从调参控件中获取函数的参数字典
        self.param_dict = self.get_params_dict()
        # 根据当前的函数名和参数字典，把需要执行的命令写到外存文件“cmd.py”中
        globalvar.set_value('imgdata', self.imgdata)
        writeout_cmd_from_paramdict(self.method, self.param_dict, self.module)
        # 所有图片的phase清空，清除缓存
        for obj in self.imgdata:
            create_dict_path(obj, [self.module, self.method])
            obj = obj[self.module]
            if self.method in obj:
                method_dict = obj[self.method]
                if method_dict is None:
                    continue
                for key, value in method_dict.items():
                    method_dict[key] = None
        # 获取当前图片数据（字典类型）
        item = self.imgdata[self.image_list.currentRow()]
        # 获取输入
        input = get_imgdata_input(item)
        # 根据生成的命令脚本（对功能函数的调用）获取输出
        globalvar.set_value('imgdata', self.imgdata)
        self.statusbar1.setText('正在进行图像运算，请耐心等待')
        out = image_process_from_cmd(self.module, self.method, input, self.imgdata)
        if out is None:
            warn('输出为空, 图片运算错误', True)
            return False
        # 新的状态列表（input是默认项目）
        leaf_paths = []
        # 对于功能函数返回的字典
        create_dict_path(item, [self.module, self.method])
        method_dict = item[self.module][self.method]
        if self.cur_phase in out.keys():
            phase = self.cur_phase
        else:
            phase = list(out.keys())[0]
        for key, value in out.items():
            # 新的状态
            self.phase2type[(self.module, self.method, key)] = type(value)
            leaf_paths.append([self.module, self.method, key])
            # item是self.imgdata对于当前图片的字典。这一步相当于建立缓存
            method_dict[key] = value
        for leaf_path in leaf_paths:
            self.add_leaf(leaf_path)
        # 根据当前状态获取输出图，载入图片控件
        self.load_object(self.get_imgdata_value(item))
        # 将应用的参数保存到缓存中
        self.dump_param()
        # 树展开
        self.phase_tree.expandAll()
        # 选中phase_tree目标
        self.select_leaf([self.module, self.method, phase])
        return True

    def dump_param(self):
        path = Path('./param_cache')
        module_dir = path / self.module
        method_dir = module_dir / f'{self.method}.json'
        module_dir.mkdir(parents=True, exist_ok=True)
        with open(str(method_dir), 'w+', encoding='utf8') as f:
            json.dump(self.param_dict, f)

    def generate_paramColumn(self, module=None, method=None):
        '''
        解析功能模块，并且解析功能模块的所有函数的参数，生成对应的调参界面
        :param method: 调参使用的函数名。如果method_name为None或False，默认用函数列表的第一个函数
        '''
        # 设置模块名

        module_list = get_config('includeList')
        if module is None or not module:
            module = module_list[0]
        self.module = module
        # 根据widget_list清除布局内部的控件
        for widget in self.widget_list:
            widget.deleteLater()
        # 清空widget_list
        self.widget_list = []
        # 解析功能模块内的功能函数，得到一个字典{method_name:attribute}
        function_dict = get_function_dict(module)
        if not function_dict:
            raise Exception('无法从功能模块中解析功能函数')
        # 得到函数名列表
        method_name_list = list(function_dict.keys())
        if method is None or not method or method == 'input':
            method = method_name_list[0]
        # 当前函数名
        self.method = method
        # 当前参数列表
        parameters = function_dict[method]['parameters']
        return_comment = function_dict[method]['return_comment']
        function_comment = function_dict[method]['function_comment']
        # return_comment = '当前方法没有添加返回值注释' if return_comment is None  else html.escape(return_comment)
        function_comment = '当前方法没有添加注释' \
            if function_comment is None or not function_comment \
            else (function_comment)
        # 参数缓存
        param_cache = self.load_param()
        # 调参区域参数容器列表
        self.param_widget_list = []
        # ------------生成模块选择器和方法选择器和刷新按钮-------------------
        paramWidgetWidth = get_config('paramWidgetWidth', 200)
        # 上方的frame
        self.head_frame = QFrame()
        self.head_frame.setMinimumWidth(paramWidgetWidth)
        head_layout = QVBoxLayout()
        # 模块选择器
        self.module_selecter = QComboBox()
        self.module_selecter.addItems(module_list)
        self.module_selecter.setCurrentText(module)
        self.module_selecter.setToolTip('选择图像处理模块')
        # 方法选择器
        self.method_selecter = QComboBox()
        self.method_selecter.addItems(method_name_list)
        self.method_selecter.setCurrentText(method)
        self.method_selecter.setToolTip(function_comment)
        # 刷新按钮

        # 用水平布局结合两个widget
        hlayout1 = QHBoxLayout()
        hlayout2 = QHBoxLayout()

        label1 = QLabel('module selecter:')
        label1.setToolTip('模块选择器')
        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.setIcon(QIcon('res/icons/refresh.png'))
        self.refresh_button.setToolTip('刷新按钮，点击后重建右侧的调参工作区')
        hlayout1.addWidget(label1)
        hlayout1.addWidget(self.refresh_button)

        label2 = QLabel('method selecter:')
        label2.setToolTip('方法选择器')
        self.tree_viewer_button = QPushButton('tree viewer')
        self.tree_viewer_button.setIcon(QIcon('res/icons/tree.png'))
        self.tree_viewer_button.setToolTip('树形选择按钮，点击后层次化地选择您想要的模块和方法')
        self.tree_viewer_button.setEnabled(False)
        hlayout2.addWidget(label2)
        hlayout2.addWidget(self.tree_viewer_button)

        head_layout.addLayout(hlayout1)
        head_layout.addWidget(self.module_selecter)
        head_layout.addLayout(hlayout2)
        head_layout.addWidget(self.method_selecter)
        # head_layout.addWidget(label3)
        self.head_frame.setLayout(head_layout)
        self.head_frame.setFixedHeight(150)
        # self.head_frame.setFixedWidth(200)
        self.head_frame.setFrameShape(QFrame.Box)
        self.head_frame.setFrameShadow(QFrame.Plain)
        self.verticalLayout_function.addWidget(self.head_frame)
        self.widget_list += [self.method_selecter, self.refresh_button, self.module_selecter, self.head_frame,
                             self.tree_viewer_button, label1, label2]
        # ------------根据参数生成调参控件-------------------
        # 方法名
        label3 = QLabel(self.method)  # 'Parameter fine tuning:'
        label3.setToolTip(f'{self.method}方法的参数微调界面')
        label3.setFrameShape(QFrame.Box)
        label3.setFrameShadow(QFrame.Plain)
        font = QtGui.QFont()
        font.setPointSize(10)
        label3.setFont(font)
        label3.setStyleSheet('background-color:white;')
        label3.setAlignment(Qt.AlignCenter)
        label3.setMinimumHeight(25)
        self.verticalLayout_function.addWidget(label3)
        # 方法注释
        edit = QTextBrowser()
        edit.setText(function_comment)
        edit.setOpenExternalLinks(True)
        # QLabel().setOpenExternalLinks()
        # edit.setReadOnly(False)
        edit.setToolTip(f'当前方法{self.method}的注释')
        edit.setFrameShape(QFrame.Box)
        edit.setFrameShadow(QFrame.Plain)
        edit.setMaximumHeight(60)
        self.widget_list += [label3, edit]
        self.verticalLayout_function.addWidget(edit)
        self.head_frame.setFrameShape(QFrame.Box)
        self.head_frame.setFrameShadow(QFrame.Plain)
        self.filler = QWidget()
        self.verticalLayout_function.addWidget(self.filler)
        x, y, dy = paramWidgetWidth * .05, 10, 30

        # 设置控件的位置
        def set_geo(o1, o2):
            nonlocal x, y, dy
            tx = x
            flag = isinstance(o2, QComboBox) or not get_config('twoColumn')
            if o1.text():
                o1.move(tx, y)
                o1.setMinimumWidth(int(paramWidgetWidth * .45))
                if flag:
                    y += dy
                else:
                    tx += paramWidgetWidth * .5
            else:
                o1.move(0, 0)
            o2.move(tx, y)
            if flag:
                o2.setMinimumWidth(int(paramWidgetWidth * .95))
            else:
                o2.setMinimumWidth(int(paramWidgetWidth * .45))
            y += dy

        is_first_img = True
        for parameter in parameters:
            param_name, param_type, param_default, param_comment = parameter
            # param_layout = QHBoxLayout(self.filler)
            label = QLabel(self.filler)
            if param_type != 'bool':
                label.setText(param_name + ' : ')
            else:
                label.setText('')
            if isinstance(param_type, str) and param_type.endswith('ndarray'):
                if is_first_img:
                    is_first_img = False
                    widget = QImgComboBox(self.filler)
                    widget.setEnabled(False)
                    self.is_multiImg_method = False
                else:
                    widget = QImgComboBox(self.filler, self.imgdata)
                    self.is_multiImg_method = True
            elif param_type == 'list':  # 视频类型
                widget = QVideoComboBox(self.filler, self.imgdata)
                self.video_selecter = widget
            elif param_type == 'QRect':
                widget = QRectButton(self.filler, QRect(0, 0, 0, 0), self.imgdata, self.video_selecter)
            elif param_type == 'float':
                widget = QDoubleSpinBox(self.filler)
                widget.setMinimum(-1000)
                widget.setMaximum(1000)
                if param_default is not None:
                    widget.setValue(float(param_cache.get(param_name, param_default)))
                else:
                    widget.setValue(0)
                widget.setSingleStep(.01)
            elif param_type == 'str':
                widget = QLineEdit(self.filler)
                text = param_default if param_default is not None else ''
                widget.setText(str(param_cache.get(param_name, text)))
            elif isinstance(param_type, list):  # 穷举类型
                widget = QComboBox(self.filler)
                widget.addItems(param_type)
                widget.setCurrentText(str(param_cache.get(param_name, param_default)))
            elif param_type == 'bool':
                widget = QCheckBox(self.filler)
                widget.setText(param_name)
                value = param_cache.get(param_name, param_default)
                if value:
                    widget.setCheckState(Qt.Checked)
                else:
                    widget.setCheckState(Qt.Unchecked)
            else:  # int
                widget = QSpinBox(self.filler)
                widget.setMinimum(-1000)
                widget.setMaximum(1000)
                if param_default is not None:
                    widget.setValue(int(param_cache.get(param_name, param_default)))
                else:
                    widget.setValue(0)
            set_geo(label, widget)
            param_comment = '该参数无注释' if param_comment is None else (param_comment)
            widget.setToolTip(param_comment)
            label.setToolTip(param_comment)
            self.param_widget_list.append({'name': param_name, 'widget': widget})
            self.widget_list += [label, widget]
        # middle_frame.setLayout(middle_layout)
        self.filler.setMinimumSize(paramWidgetWidth, y + 20)
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.filler)
        self.scroll.setFrameShape(QFrame.Box)
        self.scroll.setFrameShadow(QFrame.Plain)
        self.verticalLayout_function.addWidget(self.scroll)
        self.widget_list += [self.scroll]
        # -----------生成底返回值注释----------------------------------
        self.return_comment = return_comment
        if return_comment is not None and return_comment:
            tab = QTabWidget()
            for k, v in return_comment.items():
                edit = QTextEdit(v)
                edit.setReadOnly(False)
                edit.setToolTip(f'当前输出阶段{k}的注释')
                tab.addTab(edit, k)
            tab.setMaximumHeight(120)
            self.verticalLayout_function.addWidget(tab)
            self.widget_list += [tab]
        # -----------生成底部控件按钮----------------------------------
        bottom_layout = QHBoxLayout()
        bottom_frame = QFrame()
        bottom_frame.setMinimumWidth(paramWidgetWidth)
        bottom_frame.setFrameShape(QFrame.Box)
        bottom_frame.setFrameShadow(QFrame.Plain)
        self.apply_button = QPushButton('Apply')
        self.apply_button.setToolTip('点击应用按钮，将调参控件区域的参数应用到图片中<br><u>(Alt+S)</u>')
        bottom_layout.addWidget(self.apply_button)
        bottom_frame.setLayout(bottom_layout)
        bottom_frame.setFixedHeight(75)
        self.verticalLayout_function.addWidget(bottom_frame)
        self.widget_list += [self.apply_button, bottom_frame]
        # -----------绑定新生成控件的件----------------------------------
        self.apply_button.setShortcut(QKeySequence("Alt+S"))
        self.apply_button.clicked.connect(self.apply_param)
        self.refresh_button.clicked.connect(self.refresh)
        self.module_selecter.currentTextChanged.connect(self.module_selecter_change)
        self.method_selecter.currentTextChanged.connect(self.method_selecter_change)

    def refresh(self):
        self.generate_paramColumn(self.module, self.method)
        # 图片列表宽度
        self.image_list.setMinimumWidth(get_config('listWidgetWidth', 300))
        # 参数设置栏宽度
        self.head_frame.setMinimumWidth(get_config('paramWidgetWidth', 200))

    def module_selecter_change(self, text):
        '''响应模块选择器（下拉框）改变'''
        self.module = text
        self.generate_paramColumn(self.module, None)
        # 清空阶段输出列表
        # self.phase_tree.clear()

    def method_selecter_change(self, text):
        '''响应方法选择器（下拉框）改变'''
        self.method = text
        self.generate_paramColumn(self.module, self.method)

    # -----------------------管道相关功能-------------------------------------

    def init_pipeline(self, img_dict, ):
        if 'pipeline' not in img_dict:
            img_dict['pipeline'] = []
        pre_pipeline = img_dict['pipeline']
        # 添加初始化结点
        if not pre_pipeline:
            input_img = get_imgdata_input(img_dict)
            origin_node = {
                'path': img_dict['path'],  # 初始结点特有的属性
                'name': img_dict['name'],
                'module': None,
                'method': 'input',
                'phase': 'input',
                'param': None,
                'cmd': None,
                'image': input_img,
                'image_attr': get_img_attr(input_img),
            }
            pre_pipeline.append(origin_node)
        return pre_pipeline

    def validate(self, absPath) -> bool:
        if len(absPath) != 4:
            QMessageBox.information(self, '通知', '请选择`output`的阶段的图片输出', QMessageBox.Ok, QMessageBox.Ok)
            return False
        return True

    def moveto_imagelist(self):
        absPath = self.getAbsPath(self.phase_tree.currentIndex())
        if not self.validate(absPath):
            return
        _, module, method, phase = absPath
        cur_type = self.phase2type.get((module, method, phase), None)
        if cur_type not in (np.ndarray, list):
            QMessageBox.information(self, '通知', f'当前输出阶段{phase}不是图片格式，而是{cur_type}格式', QMessageBox.Ok, QMessageBox.Ok)
            return
        # 弹出一个对话框获取结点名称
        name, ok = QInputDialog.getText(self, 'Set node name',
                                        '请输入当前管道结点的名称',
                                        text=f'{method}_{phase}')
        if not ok:
            return
        if not name:
            warn('不能输入空字符串', True)
            return
        pre_img_dict = self.imgdata[self.image_list.currentRow()]
        # 判断是分支结构还是线型结构
        param_dict = self.get_params_dict()
        multiImg = param_dict['multiImg']
        if len(multiImg) == 1:
            pre_pipeline = self.init_pipeline(pre_img_dict)
            new_pipeline = deepcopy(pre_pipeline)  # todo: if bug ,deepcopy
        else:
            pre_pipeline = []
            for img_name, index in multiImg:
                img_dict = self.imgdata[index]
                pre_pipeline.append(self.init_pipeline(img_dict))
            new_pipeline = [pre_pipeline]
        # 构造新节点
        output = self.get_imgdata_value(pre_img_dict)
        new_pipeline.append({
            'name': name,
            'module': module,
            'method': method,
            'phase': phase,
            'param': param_dict,
            'cmd': None,
            'image': output,
            'image_attr': get_img_attr(output),
        })
        try:
            ndim = output.ndim
        except Exception:
            ndim = None
        cur_img_dict = {
            'name': name,
            'path': pre_img_dict['path'],
            'input': output.copy(),
            'pipeline': new_pipeline,
            'ndim': ndim
        }
        # 界面更新
        self.cur_phase = 'input'
        self.add_imageitem(cur_img_dict)

    def view_node(self, mode):
        # 通过闭包生成回调函数
        # self.image_list.currentRow()

        def func():
            def notice():
                QMessageBox.information(self, '通知', '只有图片格式(numpy.ndarray)的结点才能查看\n对于视频结点，您可以移至上层做管道处理', QMessageBox.Ok,
                                        QMessageBox.Ok)

            # 获取图片列表中的pipeline
            if not 0 <= self.image_list.currentRow() < len(self.imgdata):
                QMessageBox.information(self, '通知', '请先导入图片', QMessageBox.Ok, QMessageBox.Ok)
                return
            img_dict = self.imgdata[self.image_list.currentRow()]
            pipeline = self.init_pipeline(img_dict)

            # 如果是阶段输出， 加上当前信息
            if mode == 'phase':
                # 不是叶子结点，不能查看
                absPath = self.getAbsPath(self.phase_tree.currentIndex())
                if not self.validate(absPath):
                    return
                _, module, method, phase = absPath
                # 多输入方法，不能查看
                if self.is_multiImg_method:
                    QMessageBox.information(self, '通知', '该结点不能在`输出阶段`列表查看，点击右键`移至上层`后查看', QMessageBox.Ok,
                                            QMessageBox.Ok)
                    return
                # 不是图片格式，不能查看
                if not isinstance(self.cur_img, np.ndarray):
                    notice()
                    return
                self.param_dict = self.get_params_dict()
                pipeline = deepcopy(pipeline)
                pipeline.append({
                    'name': f'{self.method}_{self.cur_phase}',
                    'module': self.module,
                    'method': self.method,
                    'phase': self.cur_phase,
                    'param': self.param_dict,
                    'cmd': None,
                    'image': self.cur_img,
                    'image_attr': get_img_attr(self.cur_img),
                })
            else:
                # 不是图片格式，不能查看
                if not isinstance(get_imgdata_input(img_dict), np.ndarray):
                    notice()
                    return
            # 打开对话框
            pipeline_dlg = PipelineDialog(self, pipeline)
            self.add_modeless_dialog(pipeline_dlg)

        return func

    # -----------------------其他事件-------------------------------------

    def finishSaveEvent(self):
        self.imgdata = globalvar.get_value('imgdata', self.imgdata)

    def closeEvent(self, event):
        '''关闭事件'''
        if get_config('autoSave'):
            savePath = get_config('savePath')
            savePath_parent = os.path.dirname(savePath)
            if os.path.exists(savePath_parent):
                self.export_workspace_file(savePath)
            else:
                warn('savePath of config.json is invalid')
        exit(0)

    def paintEvent(self, event):
        '''绘图事件'''
        pass

    def mousePressEvent(self, event):
        '''鼠标按下事件'''
        if event.button() == QtCore.Qt.LeftButton:
            pass
        if event.button() == QtCore.Qt.RightButton:
            pass

    def mouseReleaseEvent(self, event):
        '''鼠标释放事件'''
        pass

    def mouseMoveEvent(self, event):  # 鼠标移动
        '''鼠标移动事件'''
        x = event.pos().x()
        y = event.pos().y()

    def wheelEvent(self, event):
        '''鼠标滚轮事件'''
        delta = event.angleDelta().y()

    def mouseDoubleClickEvent(self, event):  # 双击
        '''鼠标双击事件'''
        pass

    def keyPressEvent(self, event):
        '''键盘按下事件'''
        self.update()


if __name__ == "__main__":
    global save_dlg
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    save_dlg = SavebatchDialog()
    save_dlg.finishSave.connect(myWin.finishSaveEvent)
    # 批量保存图片按钮
    # myWin.save_bat.clicked.connect(save_dlg.view)
    myWin.show()
    sys.exit(app.exec_())
