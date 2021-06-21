# -*- coding: UTF-8 -*-

'''
命令调度模块
将主界面中的一些逻辑部分拆分到这里
'''
import json
import warnings
from importlib import reload
from pathlib import Path
from . import globalvar
import numpy as np
import os
from .parse_function import parse_function
import cv2
import pylab as plt
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from random import randint
from .utils import *


# ---------------通过cmd代码文件进行计算，获取图像函数计算值-------------------------------------------


def get_imgdata_input(data):
    '''
    获取`imgdata`某一项的`input`键值
    :param data: `imgdata`某一项
    :return: `imgdata`某一项的`input`键值
    '''
    if data['input'] is None:
        data['input'] = load_img(data['path'])
        data['ndim'] = data['input'].ndim
    return data['input']


def get_imgdata_value(item: dict, module_name='input', method_name='input', phase_name='input', imgdata=None):
    '''
    获取`imgdata`中某一项键值key对应的值
    本函数使用了缓存技巧，如果键存在并且不是None，直接返回。如果不是，需要根据cmd.py进行重新计算
    :param item: `imgdata`列表中的一项，字典类型
    :param phase_name: 键值
    :return: 键值对应的数据
    '''
    # 键不存在或者是None，需要根据cmd.py进行计算
    if phase_name == 'input':
        return get_imgdata_input(item)
    # 建立一条字典路径
    create_dict_path(item, [module_name, method_name, phase_name])
    method_dict = item[module_name][method_name]
    phase_dict = method_dict[phase_name]
    if (isinstance(phase_dict, dict) and not phase_dict) or phase_dict is None:
        if phase_name == 'input':
            ans = load_img(item['path'])
        else:
            if Path(f'cmd/{module_name}/{method_name}.py').exists():
                inputObj = get_imgdata_input(item)
                out = image_process_from_cmd(module_name, method_name, inputObj, imgdata)
                if out is None or not out:
                    # raise Exception
                    return load_img(item['path'])
                # 取出out中所有的phase放入
                for k, v in out.items():
                    method_dict[k] = v
                if phase_name in out:
                    ans = out[phase_name]
                else:
                    ans = inputObj
            else:
                # 不存在cmd.py，直接加载图片
                # raise Exception
                ans = load_img(item['path'])
        method_dict[phase_name] = ans

    else:
        ans = method_dict[phase_name]
    return ans


def image_process_from_cmd(module, method, inputObj, imgdata):
    '''
    执行cmd/目录中的代码文件，注意`exec`隐式依赖`input`,`imgdata`,隐式输出`output`
    :param module:
    :param method:
    :param inputObj: `exec`隐式依赖`input`。通过判断inputObj是否为列表(视频输入)，来进行对应的转换
    :param imgdata: `exec`隐式依赖`imgdata`（多输入类型）
    :return: 运算结果
    '''
    '''如果cmd.py已经生成，通过cmd.py调用功能函数并获得输出'''
    try:
        with open(f'cmd/{module}/{method}.py', 'r') as f:
            cmd = f.read()
            # 图片类型输入
            if isinstance(inputObj, np.ndarray):
                input = inputObj
                exec(cmd, globals(), locals())
                out = locals()['output']
            # 视频类型输入
            elif isinstance(inputObj, list):
                input = inputObj[0]
                exec(cmd, globals(), locals())
                out = locals()['output']
                for k in out.keys():
                    out[k] = [out[k]]
                for i in range(1, len(inputObj)):
                    input = inputObj[i]
                    exec(cmd, globals(), locals())
                    tmpout = locals()['output']
                    for k in out.keys():
                        out[k].append(tmpout[k])
            else:
                warn(f'invalid input type {type(inputObj)}')
                out = None
            return out
    except Exception as e:
        # 捕获运行时异常并用对话框的形式输出
        info = '图片运算错误\n' + str(e)
        warn(info, True)
        return None


# ---------------写出cmd代码文件，到cmd/目录中-------------------------------------------


def writeout_cmd_from_paramdict(function_name, param_dict, module_name):
    '''根据函数名和参数字典，构建调用功能函数的命令cmd，并保存到cmd.py'''
    path = Path(f'./cmd/{module_name}')
    path.mkdir(parents=True, exist_ok=True)
    cmd_path = path / f'{function_name}.py'
    cmd = generate_cmd(function_name, param_dict, module_name)
    with open(str(cmd_path), 'w+') as f:
        f.write(cmd)


def generate_cmd(function_name, param_dict, module_name)->str:
    '''根据函数名和参数字典，构建调用功能函数的命令cmd'''
    kv_list = []
    for k, v in param_dict.items():
        if k == 'multiImg':
            if len(v) == 1:
                for i, (name, value) in enumerate(v):
                    kv_list.append(f'{name}=input')
            else:
                for i, (name, value) in enumerate(v):
                    try:
                        kv_list.append(f'{name}=imgdata[{value}]["input"]')
                    except Exception:
                        raise Exception('')
                        # raise Exception('globalvar.set_value("imgdata",self.imgdata) 未执行')
        else:
            kv_list.append(f'{k}={v}')
    kv_list_str = ','.join(kv_list)
    module_path = Path(get_config('modulePath')) / module_name
    dirname, filename = os.path.split(str(module_path))
    module_name = filename.split('.')[0]
    importList = get_config('importList')
    cmd = '\n'.join(importList)
    cmd += f'''
module_path="{dirname}"
if module_path not in sys.path: 
    sys.path.append(module_path)
import {module_name}
from importlib import reload
reload({module_name})
output = {module_name}.{function_name}({kv_list_str})
'''
    return cmd


# ---------------其他-------------------------------------------


def create_dict_path(obj: dict, path: list):
    '''
    根据一个路径列表，来构造深层次的字典
    example:
    >>>create_dict_path({},['module','method','phase'])
    >>>{'module':{'method':{'phase':{}}}}
    '''
    for i, item in enumerate(path):
        if item not in obj or obj[item] is None:
            obj[item] = {}
        if isinstance(obj, dict):
            obj = obj[item]
        else:
            break


def get_function_dict(module=None):
    '''获取功能模块中功能函数的属性字典'''
    module_path = get_module_path(module)
    with open(module_path, encoding='utf8') as f:
        txt = f.read().replace('\n', ' ')
    ret = parse_function(txt, module_path)
    ans = {}
    for item in ret:
        if item['return_type'] == 'dict':
            ans[item['function_name']] = item
    return ans


def get_module_path(module=None):
    '''获取功能模块对应的文件（在config.json中配置）'''
    path = Path(get_config('modulePath'))
    if not module:
        includeList = get_config('includeList')
        path = path / includeList[0]
    else:
        path = path / module
    return str(path)


def generate_simple_cmd(module_name, method_name, param_dict, new_phase, pre_phase=None):
    # delete `.py`
    module_name = module_name.split('.')[0]
    kv_list = []
    for k, v in param_dict.items():
        if k == 'multiImg':
            for i, (name, value) in enumerate(v):
                if pre_phase is not None:
                    kv_list.append(f'{name}={pre_phase[i]}')
                else:
                    kv_list.append(f'{name}')
        else:
            kv_list.append(f'{k}={v}')
    return f"{new_phase} = {module_name}.{method_name}({','.join(kv_list)})['{new_phase}']"


def get_imgParam_list(multiImg):
    ans = []
    for param, _ in multiImg:
        ans.append(param)
    return ans


def get_img_attr(obj):
    if obj is None:
        return {}
    if isinstance(obj, np.ndarray):
        ndim = obj.ndim
        if ndim == 2:
            min = int(obj.min())
            max = int(obj.max())
            mean = round(float(obj.mean()), 2)
        else:
            min = (obj.min(axis=(0, 1))).tolist()
            max = (obj.max(axis=(0, 1))).tolist()
            mean = [round(x, 2) for x in obj.mean(axis=(0, 1))]
        obj_attr = {
            'dtype': str(obj.dtype),
            'ndim': ndim,
            'min': min,
            'max': max,
            'mean': mean,
            'shape': obj.shape,
        }
    elif isinstance(obj, list):
        obj_attr = {
            'ndim': obj[0].ndim,
            'frames': len(obj),
            'shape': obj[0].shape
        }
    else:
        warnings.warn(f'invalid type {type(obj)}')
        obj_attr = {}

    return obj_attr
