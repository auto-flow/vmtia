# -*- coding: UTF-8 -*-

'''
函数解析库
用于解析某一文件中所有函数的函数名、参数列表（参数名，参数类型，默认值）、返回值
'''

import re
import sys
import warnings
from pathlib import Path
import textwrap
from platform import platform

import numpy as np
from importlib import reload


def chop_long_comment(comment, sep=80):
    pattern_str = '\s*?<.*?>.*</.*?>\s*?'
    pattern = re.compile(pattern_str)
    if pattern.match(comment):
        return comment
    return '\n'.join(textwrap.wrap(comment, sep))


def parse_raw_parameters(raw_parameters):
    # 0:()  ; 1:[]   ; 2:{}
    bracket = np.zeros((3,))
    left = '([{'
    right = ')]}'
    pre_list = []
    cur_word = ''
    for c in raw_parameters:
        if c in left:
            index = left.find(c)
            bracket[index] += 1
        elif c in right:
            index = right.find(c)
            bracket[index] -= 1
        else:
            # 只要有一个非零，说明还在括号匹配阶段
            if bracket.any():
                cur_word += c

            # 正常阶段，词可以被逗号分割
            else:
                # 出现了分隔符
                if c == ',':
                    pre_list.append(cur_word)
                    cur_word = ''
                else:
                    cur_word += c

    # 最后扫尾
    pre_list.append(cur_word)
    ans_list = []
    # 对于list中的子表进行后处理 (变量名与对应的格式)
    for i, item in enumerate(pre_list):
        tmp = item.split(':')
        # 得到变量名
        param_name = tmp[0].strip()
        if len(tmp) <= 1:
            param_type = None
            param_default = None
        else:
            # 得到默认值
            tmp = tmp[1].split('=')
            if len(tmp) > 1:
                param_default = tmp[1].strip()
            else:
                param_default = None
            if tmp[0].find(',') >= 0:
                param_type = tmp[0].split(',')
            else:
                param_type = tmp[0].strip()
        if param_name is None or not param_name:
            continue
        # 参数名 参数类型 参数默认值 参数注释(后期补上)
        ans_list.append([param_name, param_type, param_default, None])
    return ans_list


def parse_function(txt, module_path=None):
    pattern_str = r"def\s+(?P<function_name>[a-zA-Z_][a-zA-Z0-9_]*)" \
                  r"\s*\((?P<parameters>.*?)\)\s*(?P<return_type>->.*?){0,1}\s*:" \
                  r"(?P<comment>\s*?'''.*?'''){0,1}"
    pattern = re.compile(pattern_str)
    iters = pattern.finditer(txt)
    ret = []
    for iter in iters:
        item = {}
        function_name = iter.group('function_name')
        raw_parameters = iter.group('parameters')
        parameters = parse_raw_parameters(raw_parameters)
        raw_return_type = iter.group('return_type')
        if raw_return_type is not None:
            return_type = raw_return_type.replace('->', '').strip()
        else:
            return_type = None
        item['function_name'] = function_name
        item['parameters'] = parameters
        item['return_type'] = return_type
        item['return_comment'] = None
        item['function_comment'] = None
        if module_path is not None and return_type == 'dict':
            parse_comment_ans = parse_comment(function_name, module_path)
            if parse_comment_ans is not None:
                param_comment, return_comment, function_comment = parse_comment_ans
                item['function_comment'] = function_comment
                for param in parameters:
                    param_name = param[0]
                    comment = param_comment.get(param_name, None)
                    param[3] = comment
                if return_comment is not None and return_comment:
                    try:
                        ans_return_comment = {}
                        raw_phase_comments = return_comment.split(';')
                        raw_phase_comments = list(filter(lambda x: (not x.isspace()) and x, raw_phase_comments))
                        for raw_phase_comment in raw_phase_comments:
                            try:
                                phase, phase_comment = raw_phase_comment.split('=')
                                ans_return_comment[phase.strip()] = phase_comment.strip()
                            except Exception as e:
                                warnings.warn(str(e))
                        item['return_comment'] = ans_return_comment
                    except Exception as e:
                        warnings.warn(str(e))
        ret.append(item)
    return ret


def parse_comment(function_name, module_path):
    if 'darwen' in platform().lower():
        return None, None, None
    path = Path(module_path)
    fname = path.name
    dname = str(path.parent)
    if dname not in sys.path:
        sys.path.append(dname)
    module = fname.split('.')[0]
    cmd = f'''
import {module}
reload({module})
ans=({module}.{function_name}).__doc__
'''
    try:
        exec(cmd, globals(), locals())
    except Exception as e:
        warnings.warn(str(e))
        return None
    raw_comment = locals()['ans']
    if raw_comment is None:
        return None
    comments = raw_comment.split('\n')
    comments = list(filter(lambda x: (False if x.strip() == '' else True), comments))
    comments = list(x.strip() for x in comments)
    function_pattern_str = r':\s*?param\s+?' \
                           r'(?P<param_name>[a-zA-Z_][a-zA-Z0-9_]*)\s*:' \
                           r'(?P<comment>.*)'
    return_pattern_str = r':\s*?return\s*?:(?P<comment>.*)'
    function_pattern = re.compile(function_pattern_str)
    return_pattern = re.compile(return_pattern_str)
    param_comment = {}
    return_comment = None
    function_comment = ''
    pre_param_name = None
    is_in_return_comment = False
    for comment in comments:
        # 函数注释
        if function_pattern.match(comment) is not None:
            match = function_pattern.findall(comment)
            match = match[0]
            param_name, cur_param_comment = match
            param_comment[param_name] = chop_long_comment(cur_param_comment)
            pre_param_name = param_name
        # 返回值注释
        elif return_pattern.match(comment) is not None:
            match = return_pattern.findall(comment)
            return_comment = (match[0]).strip()
            is_in_return_comment = True
        # 参数注释  + 其他
        else:
            if pre_param_name is None:
                function_comment += chop_long_comment(comment) + '<br>\n'
            elif is_in_return_comment:
                return_comment += comment.strip()
            else:
                param_comment[pre_param_name] += '\n' + chop_long_comment(comment)
    return param_comment, return_comment, function_comment


if __name__ == '__main__':
    path = '/home/tqc/Desktop/image-process-tool/image-process-tool_THU/imageUtils/enhancement.py'
    with open(path) as f:
        txt = f.read().replace('\n', ' ')
    ret = parse_function(txt, path)
    ret2 = parse_comment()
