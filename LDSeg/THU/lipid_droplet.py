# !/usr/bin/env python
# encoding: utf-8

import os
import sys

import cv2
import numpy as np
import copy
import numpy.ma  as ma
from utils import *
from algorithm import *


def recursionOpenMethod(
        img: np.ndarray,
        isBlur: bool=True,
        rethreshold: bool=True,
        isadaptive: bool=True,
        clipLimit: float=6.,
        gridSize: int=20,
        thresholdValue: int=6,
        minMatchArea: int=20,
        minMatchShape: float=.2,
        minObjectArea: int=20,
        erode_size: int=3,
        dilate_size: int=3,
        max_iterations: int=10,
) -> dict:
    '''
    对于非圆形的连通块，采用距离变换获取中心区域，再递归地进行形态学开运算
    :param img: 脂肪滴图像
    :param isUseEnhancement: 是否使用局部直方图增强
    :param isBlur: 是否使用平滑
    :param rethreshold: 是否对非圆脂滴图像重新使用阈值分割
    :param isadaptive: 是否对非圆脂滴图像阈值分割使用自适应阈值
    :param clipLimit: 局部直方图增强参数，越大图像对比度越大，分割出的脂滴越多
    :param gridSize: 局部直方图增强参数
    :param thresholdValue: 采用大律法进行分割时，采用的阈值大小
    :param minMatchArea: 非圆形的连通块的最小面积
    :param minMatchShape: 非圆形的连通块的最小匹配程度
    :param erode_size: 进行递归地形态学开运算时，每一步的腐蚀操作的算子大小
    :param dilate_size: 进行递归地形态学开运算时，每一步的膨胀操作的算子大小
    :param max_iterations: 递归运算的最大深度
    :param minObjectArea: 删除小于minObjectArea的连通块。如果不想进行删除连通小块的操作，可以把这个值设置为0
    :return: enhancement=增强后的图像;
             preliminarySegment=预分割后的效果图;
             no_circle=非圆连通块;
             no_circle_processed=处理后的非圆连通块;
             markers=最终的连通块效果图,在状态栏中显示的最大值`max`就是分割得到的脂肪滴数目;
             colorful_markers=着色的连通块;
             outline_markers=绘制轮廓的效果图;
             outline_ellipses=用椭圆拟合各个脂肪滴轮廓;
             lipid_count=当前方法与参数下，分割得到的脂肪滴数目;
             dataTable=分割得到的各个脂肪滴的属性表
    '''
    gray = convert2gray(img)
    origin = copy.deepcopy(gray)
    if isBlur:
        blured = cv2.GaussianBlur(gray, (5, 5), 0)
    else:
        blured = copy.deepcopy(gray)
    blured = local_histogram_equalization(blured,clipLimit,gridSize)
    threshold = cv2.threshold(blured, thresholdValue, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    blured2 = cv2.GaussianBlur(threshold, (3, 3), 0)
    threshold2 = cv2.threshold(blured2, thresholdValue, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    removed = remove_small_ojects(threshold2, min_size=minObjectArea)
    preliminary_segment = remove_small_holes(removed)
    _, markers = cv2.connectedComponents(preliminary_segment)
    is_circle, no_circle = segmentNoCircle(markers, minMatchShape, minMatchArea)
    mean = blured[preliminary_segment].mean()
    processed,ellipses,table = recursionOpenProcess(no_circle,
                                     gray,
                                     rethreshold,
                                     isadaptive,
                                     erode_size,
                                     dilate_size,
                                     max_iterations,
                                     minMatchShape,
                                     minMatchArea,
                                     mean
                                     )

    concat = concatenateMarkers(is_circle, processed)
    # _,concat=cv2.connectedComponents(removed)
    binary = (concat > 0).astype('uint8')
    outline_markers = draw_outline(origin, binary)
    outline_ellipses = draw_outline(origin, ellipses,True)
    colorful_markers = displayMarkers(concat)
    ret = {
        'enhancement': blured,
        'presegment': preliminary_segment,
        'no_circle': no_circle,
        'no_circle_processed': processed,
        'markers': concat,
        'colorful_markers': colorful_markers,
        'outline_markers': outline_markers,
        'outline_ellipses':outline_ellipses, 
        'lipid_count': int(concat.max()),
        'dataTable':table
    }
    return ret


if __name__ == '__main__':
    path = 'test.tif'
    img = load_img(path)
    ans = recursionOpenMethod(img)
    img_show([ans['colorful_markers'],ans['outline_ellipses']])
