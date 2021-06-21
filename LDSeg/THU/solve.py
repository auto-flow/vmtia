import os
import sys

import cv2
import numpy as np
import numpy.ma as ma
from utils import *
import pandas as pd
import pylab as plt

circle_img = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50))
circle_img = np.pad(circle_img, 2, 'constant')
match_contours = get_single_contour(circle_img)

def get_match_score(contour):
    ret = cv2.matchShapes(match_contours, contour, 1, 0.)
    return ret


def afterprocess(marker, layer=0):

    dt = cv2.distanceTransform(marker, cv2.DIST_L2, 3)
    dt=((dt-dt.min())/(dt.max()-dt.min()))*255
    dt=dt.astype('uint8')
    sure_fg=(dt>128).astype('uint8')*255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cv2.morphologyEx(sure_fg, cv2.MORPH_OPEN, kernel, iterations=2)
    unknown = cv2.subtract(marker, sure_fg)
    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1  # 用label进行控制
    markers[unknown == 255] = 0
    markers = cv2.watershed(cv2.cvtColor(marker,cv2.COLOR_GRAY2BGR), markers)  # 分水岭的地方就编程-1
    markers[markers==-1]=1
    markers-=1
    print(set(markers.flat))
    ans=markers.copy()
    # 引入递归  注意溢出
    # ans=np.zeros_like(markers,dtype='uint8')
    # index=1
    # for i in range(1,markers.max()+1):
    #     cur=(markers==i).astype('uint8')
    #     score=get_match_score(cur)
    #     if score>=.5 and layer<2:
    #         proc=process(cur,layer+1)  # 注意调整最大值
    #         for j in range(1,proc.max()+1):
    #             print(j)
    #             sub = (proc == j)
    #             ans[sub]=index+j-1
    #         # ans[proc>0]+=(proc+index-1)
    #         index+=proc.max()
    #     else:
    #         ans+=cur*index
    #         index+=1
    # debug
    img_show([marker,dt,sure_fg,ans])

    return ans



marker=np.load('a5.npy')
contours = get_single_contour(marker)
x, y, w, h = cv2.boundingRect(contours)
marker=marker[y:y+h,x:x+w]
marker=remove_small_holes(marker)
ret =get_match_score(contours)
print('origin match-score: ',ret)
afterprocess(marker)