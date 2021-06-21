# -*- coding: UTF-8 -*-

import sys, os
from pathlib import Path
import pandas as pd
import cv2
from PyQt5.QtWidgets import *  # QMessageBox,QFileDialog,QWidget,QApplication,QMainWindow,QSizePolicy
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from . import globalvar
from .utils import *
from .cmd_manage import *
from imageio import imwrite
from .ui_savebatch import Ui_MainWindow

spliter = '\t/'


class SavebatchDialog(QMainWindow, Ui_MainWindow):
    finishSave = pyqtSignal()

    def __init__(self, parent=None):
        super(SavebatchDialog, self).__init__(parent)
        self.setupUi(self)
        # 给控件绑定事件
        self.start_button.clicked.connect(self.start)
        self.terminate_button.clicked.connect(self.terminate_thread)
        self.fold_button.clicked.connect(self.select_bat_dir)
        # 初始化一些变量
        self.work_path = ''
        self.print_info = ''
        self.image_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.phase_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_table.customContextMenuRequested.connect(self.show_image_table_menu(self.image_table))
        self.phase_table.customContextMenuRequested.connect(self.show_image_table_menu(self.phase_table))
        self.progress.setValue(0)

    def show_image_table_menu(self, table):
        def func():
            table.contextMenu = QMenu(self)
            action1 = table.contextMenu.addAction(u'全部选择')
            action2 = table.contextMenu.addAction(u'全部不选')
            table.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
            action1.triggered.connect(self.select_all_for_table(table))
            action2.triggered.connect(self.select_none_for_table(table))
            table.contextMenu.show()

        return func

    def select_all_for_table(self, table):
        def func():
            model = table.model()
            row_cnt = model.rowCount()
            for row in range(row_cnt):
                model.item(row, 0).setCheckState(2)

        return func

    def select_none_for_table(self, table):
        def func():
            model = table.model()
            row_cnt = model.rowCount()
            for row in range(row_cnt):
                model.item(row, 0).setCheckState(0)

        return func

    def view(self):
        if self.isVisible(): return
        self.imgdata = globalvar.get_value('imgdata')
        self.generate_tables()
        self.image_table.setColumnWidth(1, 300)
        self.phase_table.setColumnWidth(1, 400)
        self.show()
        self.showMaximized()

    def select_bat_dir(self):
        self.work_path = str(QFileDialog.getExistingDirectory(self, "Select Directory",get_default_dir('select_bat_dir')))
        if not self.work_path:
            QMessageBox.warning(self, 'No Folder Selected', 'Please select a valid Folder')
            return
        set_default_dir('select_bat_dir',self.work_path)
        self.fold_edit.setText(self.work_path)

    def closeEvent(self, QCloseEvent):
        self.hide()
        QCloseEvent.ignore()

    def __set_table_data(self, table: QTableWidget, data_list, title):
        self.model = QStandardItemModel(table)
        # 设置数据层次结构
        row_num = len(data_list)
        col_num = 2
        self.model = QStandardItemModel(row_num, col_num)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(['选择', title])
        is_phase_table = table is self.phase_table
        recommendPhases = get_config("recommendPhases", [])
        if is_phase_table:
            phase_list = [item.split(spliter)[-1] for item in data_list]
        for i, row in enumerate(data_list):
            # 设置复选框
            item_checked = QStandardItem()
            item_checked.setCheckable(True)
            if is_phase_table:
                cur_phase = phase_list[i]
                if cur_phase in recommendPhases:
                    item_checked.setCheckState(Qt.Checked)
                else:
                    item_checked.setCheckState(Qt.Unchecked)
            else:
                item_checked.setCheckState(Qt.Checked)
            self.model.setItem(i, 0, item_checked)
            # 设置文本
            item = QStandardItem(data_list[i])
            self.model.setItem(i, 1, item)
        table.setModel(self.model)
        # 根据内容自适应宽度
        # table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def generate_tables(self):
        # -----------设置图片列表------------------------
        try:
            img_list = [item['name'] for item in self.imgdata]
        except Exception:
            QMessageBox.warning(self, '警告', '数据异常')
            self.close()
            return
        if len(img_list) == 0:
            QMessageBox.warning(self, '警告', '图片列表为空')
            self.close()
            return
        self.__set_table_data(self.image_table, img_list, '图片名')
        # -----------设置阶段输出列表------------------------
        phase_tree = globalvar.get_value('phase_tree')
        fixedModule = get_config("fixedModule")
        fixedMethod = get_config("fixedMethod")
        if fixedModule is not None and fixedModule in phase_tree:
            phase_tree = phase_tree[fixedModule]
        if fixedMethod is not None and fixedMethod in phase_tree:
            phase_tree = phase_tree[fixedMethod]
        self.phase_list = []
        self.tree2list(phase_tree)
        self.phase_list.sort()
        self.phase_list.insert(0, 'input')
        if self.phase_list is None or not self.phase_list:
            self.phase_list = ['input']
        if len(self.phase_list) == 0:
            QMessageBox.warning(self, '警告', '阶段输出列表为空')
            self.close()
            return
        self.__set_table_data(self.phase_table, self.phase_list, '阶段输出名')

    def tree2list(self, tree, s='', cnt=0):
        if not tree:
            self.phase_list.append(s)
        for i, key in enumerate(tree.keys()):
            if cnt:
                ns = s + spliter + key
            else:
                ns = key
            self.tree2list(tree[key], ns, cnt + 1)

    def get_selected_items(self, table):
        model = table.model()
        row_cnt = model.rowCount()
        ans_list = []
        for row in range(row_cnt):
            checkbox = model.item(row, 0)
            tableitem = model.item(row, 1)
            checkState = checkbox.checkState()
            text = tableitem.text()
            if checkState == 2:
                ans_list.append(text)
        return ans_list

    def start(self):
        # 获得一些模式
        self.mode = self.save_model_combo.currentText().split()[-2]
        self.imageFormat = self.imageFormat_combo.currentText()
        self.tableFormat = self.tableFormat_combo.currentText()
        # 如果没有选择路径，不能开始
        if not self.work_path:
            QMessageBox.warning(self, '警告', '请选择路径')
            return
        if not os.path.exists(self.work_path):
            QMessageBox.warning(self, '警告', '请选择合法路径')
            return
        # 从两个列表中获取选中的表项
        image_list = self.get_selected_items(self.image_table)
        self.phase_list = self.get_selected_items(self.phase_table)
        self.image_set = set(image_list)
        # 设置进度条
        self.progress.setValue(0)
        self.finished_cnt = 0
        self.all_cnt = len(self.phase_list) * len(self.image_set)
        # 设置线程
        self.thread = ProcessThread(self.imgdata, self.image_set,
                                    self.phase_list, self.work_path,
                                    self.mode, self.imageFormat, self.tableFormat)
        self.thread.finished_one.connect(self.finishedOneEvent)
        self.thread.finished_all.connect(self.finishedAllEvent)
        self.thread.start()

    def finishedOneEvent(self, info):
        cur_info = f'文件 {info} 已保存\n'
        self.print_info += cur_info
        self.info_edit.setText(self.print_info)
        self.finished_cnt += 1
        cur = int((self.finished_cnt / self.all_cnt) * 100)
        self.progress.setValue(cur)

    def finishedAllEvent(self):
        self.progress.setValue(100)
        self.print_info += "当前任务全部完成\n"
        self.info_edit.setText(self.print_info)
        # 保存之后相当于已经得到了一些图片的数据，可以把这些数据传到parent中避免重复计算
        globalvar.set_value('imgdata', self.imgdata)
        self.print_info += "主窗口缓存已写入\n"
        self.info_edit.setText(self.print_info)
        QMessageBox.information(self, '通知', '保存完毕')

    def terminate_thread(self):
        try:
            self.thread.terminate()
        except Exception as e:
            warnings.warn('无法结束线程')


class ProcessThread(QThread):
    # create the signals that will be emitted from this QThread
    finished_all = pyqtSignal()
    finished_one = pyqtSignal(str)

    def __init__(self, imgdata, image_set, phase_list, work_path, mode, imageFormat, tableFormat):
        self.imgdata = imgdata
        self.image_set = image_set
        self.phase_list = phase_list
        self.work_path = work_path
        self.mode = mode
        self.imageFormat = imageFormat
        self.tableFormat = tableFormat
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def __get_phase_set(self, phase_list):
        phase_list.remove('input')
        true_phase_list = [item.split('->')[0] for item in phase_list]
        return set(true_phase_list)

    def __has_single_phase(self, phase_list):
        try:
            phase_list.remove('input')
            true_phase_list = [item.split('->')[0] for item in phase_list]
            return len(set(true_phase_list)) == 1
        except Exception:
            return False

    def get_phase_path(self, raw):
        if raw == 'input':
            return ['input']
        else:
            return raw.split(spliter)

    def run(self):
        for item in self.imgdata:
            if item['name'] not in self.image_set:
                continue
            name = item['name'].split('.')[0]
            for rawphase in self.phase_list:
                path = Path(self.work_path)
                if rawphase == 'input':
                    if self.mode == 'single':
                        cur_path = path / f'{name}'
                    else:
                        cur_path = path / name / f'input'
                    output = get_imgdata_input(item)
                else:
                    phase_path = self.get_phase_path(rawphase)
                    fixedModule = get_config("fixedModule")
                    fixedMethod = get_config("fixedMethod")
                    f_module, f_method = '', ''  # 文件名 中 的模块方法名
                    if fixedMethod is not None:
                        phase_path.insert(0, fixedMethod)
                    if fixedModule is not None:
                        phase_path.insert(0, fixedModule)
                    module, method, phase = phase_path
                    if fixedMethod is None:
                        f_method=method
                    if fixedModule is None:
                        f_module=module
                    if '.py' in f_module:
                        f_module = f_module.replace('.py', '')
                    if self.mode == 'single':
                        cur_path = path / f'{name} {f_module} {f_method} {phase}'
                    else:
                        cur_path = path / name / f_module / f_method / phase
                    output = get_imgdata_value(item, module, method, phase, self.imgdata)
                # 根据各种判断条件生成路径和图像，保存
                cur_path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(output, np.ndarray):
                    if self.imageFormat == 'npy':
                        np.save(str(cur_path) + f'.{self.imageFormat}', output)
                    else:
                        imwrite(str(cur_path) + f'.{self.imageFormat}', output)
                elif isinstance(output, pd.DataFrame):
                    table_path = str(cur_path) + f'.{self.tableFormat}'
                    if self.tableFormat == 'xlsx':
                        output.to_excel(table_path)
                    else:
                        output.to_csv(table_path)
                else:
                    txt_path = str(cur_path) + '.txt'
                    with open(txt_path, 'w') as f:
                        f.write(str(output))
                self.finished_one.emit(str(cur_path))
        self.finished_all.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = SavebatchDialog()
    myWin.show()

    sys.exit(app.exec_())
