# -*- coding: UTF-8 -*-
import os, sys
from pathlib import Path
from . import globalvar
from .utils import get_config

__version__ = get_config('version')


def main():
    '''
    程序入口
    通过pip打包安装后，有两种调用方式：
    python -m vmtia
    vmtia
    '''
    this_dir = Path(__file__).parent
    print('Execute in ', this_dir)
    os.chdir(this_dir)
    from PyQt5.QtWidgets import QApplication
    from .interface import MyMainWindow, SavebatchDialog
    info = (f'Visual Modeling Tool for Image Algorithm v{__version__}')
    info = get_config('title', info)
    print(info)
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    save_dlg = SavebatchDialog()
    save_dlg.finishSave.connect(myWin.finishSaveEvent)
    globalvar.set_value('save_dlg', save_dlg)
    myWin.show()
    sys.exit(app.exec_())
