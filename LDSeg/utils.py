# -*- coding: UTF-8 -*-
'''
功能函数库
'''

import json
import os
import warnings
from pathlib import Path
from platform import platform

from PIL import ImageSequence, Image

from . import globalvar
import numpy as np
import cv2
from PyQt5.QtWidgets import QMessageBox
from random import randint

# Image formats supported by Qt
VALID_FORMAT = ('.BMP', '.GIF', '.JPG', '.JPEG', '.PNG', '.PBM',
                '.PGM', '.PPM', '.TIFF', '.XBM', 'TIF', 'NPY')

video_types = [
    "MP4 Files (*.mp4)",
    "AVI Files (*.avi)",
    "MKV Files (*.mkv)",
    "All Files (*)"
]

image_types = [
    'JPG Files (*.jpg)',
    'PNG Files (*.png)',
    'TIFF Files (*.tif)',
    'Numpy Files (*.npy)',
    'BMP Files (*.bmp)',
    'GIF Files (*.gif)',
    'All Files (*)'
]


def get_color(type='hex'):  # hex rgb
    color = []
    for i in range(3):
        color.append(randint(0, 255))
    if type == 'hex':
        hex = '#' + ''.join(f"{x:02x}" for x in color)
        return hex
    else:
        return color


def get_config(name, default=None):
    return get_config_dict().get(name, default)


def get_config_dict():
    '''获取配置字典'''
    config_path = Path(__file__).parent/'config'
    with open((config_path / 'main.json'), 'r', encoding='utf8') as f:
        configFile = json.load(f)["configFile"]
    configFile = config_path / configFile
    with open(configFile, 'r', encoding='utf8') as f:
        return json.load(f)


def set_config(config):
    '''获取配置字典'''
    try:
        with open('config/main.json', 'r', encoding='utf8') as f:
            configFile = json.load(f)["configFile"]
        configFile = 'config/' + configFile
        with open(configFile, 'w', encoding='utf8') as f:
            return json.dump(config, f, indent=4)
    except Exception as e:
        warn(str(e) + '\nconfig file is loss, return default value as None')
        return None


def to_json(obj):
    return json.dumps(obj, indent=2)


def vediofile_to_arrlist(fname):
    ''''''
    arrlist = []
    playCapture = cv2.VideoCapture()
    playCapture.open(fname)
    while True:
        success, frame = playCapture.read()
        if not success:
            break
        if len(frame.shape) == 3:
            frame = frame[:, :, ::-1]
        arrlist.append(frame)
    playCapture.release()
    return arrlist


def warn(info, useGUI=False):
    info = str(info)
    warnings.warn(info)
    if useGUI:
        QMessageBox.warning(globalvar.get_value('MainWindow'), 'Warning', info)


def convertToCRLF(dpath):
    for file in Path(dpath).iterdir():
        if file.is_file():
            try:
                txt = file.read_text()
                if '\r' not in txt and '\n\n\n' not in txt:
                    txt = txt.replace('\n', '\r\n')
                    file.write_text(txt)
            except:
                pass

def clickfile(fpath):
    if 'windows' in platform().lower():
        if Path(fpath).suffix=='.html':
            os.system(f'start {fpath}')
        else:
            os.system(f'start notepad {fpath}')
    elif 'linux' in platform().lower():
        os.system(f'xdg-open {fpath}')
    elif 'darwin' in platform().lower():  # mac
        os.system(f'open {fpath}')

def get_default_dir(ID):
    jpath='config/store.json'
    if not Path(jpath).exists():
        Path(jpath).write_text('{}')
    with open(jpath) as f:
        store = json.load(f)
    if ID in store and Path(store[ID]).exists():
        return store[ID]
    else:
        return os.getcwd()


def set_default_dir(ID, dir):
    try:
        if Path(dir).is_file():
            dir = Path(dir).parent
        dir = str(dir)
        if not Path(dir).exists():
            return
    except Exception as e:
        warn(e)

    with open('config/store.json') as f:
        store = json.load(f)
        store[ID] = dir
    with open('config/store.json', 'w') as f:
        json.dump(store, f, indent=4)


def get_tiff_channel(tiff):
    frame_list = []
    for frame in ImageSequence.Iterator(tiff):
        frame = np.array(frame)
        frame = img_norm(frame)
        frame_list.append(frame)
    return frame_list


def load_img(path):
    if Path(path).suffix == '.npy':
        img = np.load(path)
        return img
    elif Path(path).suffix in ('.tif','.tiff'):
        tiff = Image.open(path)
        tiffs = get_tiff_channel(tiff)
        if len(tiffs)>3:
            tiffs=tiffs[:3]
        else:
            while len(tiffs)<3:
                tiffs.append(np.zeros_like(tiffs[0]))
        img=np.stack(tiffs,2)
        return img
    else:
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), -1)
        channels = img.shape.__len__()
        if channels == 2:
            return img
        else:
            return cv2.cvtColor(img,cv2.COLOR_BGR2RGB)



def stack_gray_to_rgb(gray):
    '''
    为适用于一些特殊的应用场景（如watershed的第一个参数需要三通道图），我们需要把灰度图转为三通道图（虽然也是灰的）
    可以用numpy的stack在通到2进行一个简单的叠加
    :param gray:  ndim=2的灰度图
    :return:  ndim=3的rgb图
    '''
    rgb = np.stack((gray, gray, gray), axis=2)
    return rgb.astype('uint8')


def img_norm(img):
    """
    图像归一化
    :param img:
    :return:
    """
    img = (img - np.min(img)) / float(np.max(img) - np.min(img))
    img *= 255.
    img = img.astype(np.uint8)
    return img

