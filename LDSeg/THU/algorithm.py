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
global gID


def recursion(crop, lineWidth=2, min_matchShapes=.1, min_area=20, minRatio=.1):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    hull = morphology.convex_hull_image(crop > 0).astype('uint8')
    hull_area = getArea(hull)
    subtract = hull.copy()
    subtract[crop > 0] = 0
    ans = np.zeros_like(crop)
    # subtract=cv2.erode(subtract,kernel)
    subtract = cv2.morphologyEx(subtract, cv2.MORPH_OPEN, kernel, iterations=1)
    ret, sub_markers = cv2.connectedComponents(subtract)
    label_ratio = []
    for sub_label in range(1, sub_markers.max() + 1):
        sub_loc = sub_markers == sub_label
        sub_marker = sub_loc.astype('uint8')
        sub_area = getArea(sub_marker)
        ratio = (sub_area / hull_area)
        label_ratio.append((sub_label, ratio))
    if len(label_ratio) < 2:
        return (crop > 0).astype('uint8')
    label_ratio.sort(key=lambda x: x[1])
    label_ratio = label_ratio[::-1]
    if label_ratio[1][1] < minRatio:
        return (crop > 0).astype('uint8')

    pt = []
    divisionZero = False
    for i in range(2):
        sub_label = label_ratio[i][0]
        contour = get_single_contour((sub_markers == sub_label).astype('uint8'))
        M = cv2.moments(contour)
        if not M['m00']:
            divisionZero = True
            break
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        pt.append((cx, cy))
    if divisionZero:
        return (crop > 0).astype('uint8')
    devided = crop.copy()
    cv2.line(devided, pt[0], pt[1], 0, lineWidth)
    ans[devided > 0] = 1
    final = np.zeros_like(crop)
    ret, ans_markers = cv2.connectedComponents(ans)
    for label in range(1, ans_markers.max() + 1):
        marker = (ans_markers == label).astype('uint8')
        marker = cv2.morphologyEx(marker, cv2.MORPH_OPEN, kernel, iterations=1)
        contours = get_single_contour(marker)
        area = cv2.contourArea(contours)
        ret = cv2.matchShapes(match_contours, contours, 1, 0.)
        if not (ret < min_matchShapes or area < min_area):
            res = recursion(marker, lineWidth, min_matchShapes, min_area, minRatio)
            # img_show([res,marker])
            final[res > 0] = 1
        else:
            final[marker > 0] = 1
    # img_show([crop, hull, subtract, devided],
    #          title_list=['origin', 'convex_hull', 'subtract', 'output'],
    #          )
    return final


def convexHullProcess(
        no_circle: np.ndarray,
        minArea: int = 20,
        lineWidth: int = 2,
        minRatio: float = .1,
):
    # no_circle = cv2.imread('../m3.jpg', 0)
    n = no_circle.max()
    ans = np.zeros_like(no_circle, 'uint8')
    for sub_label in range(1, n + 1):
        loc = (no_circle == sub_label)
        if not loc.any():
            continue
        marker = loc.astype('uint8')
        contours = get_single_contour(marker)
        area = cv2.contourArea(contours)
        if area < minArea:
            continue
        x, y, w, h = cv2.boundingRect(contours)
        crop = marker[y: y + h, x: x + w]
        # crop = cv2.morphologyEx(crop, cv2.MORPH_OPEN, kernel, iterations=1)
        # crop = cv2.GaussianBlur(crop, (3, 3), 0)
        final = recursion(crop, lineWidth, min_area=minArea, minRatio=minRatio)
        ans[y: y + h, x: x + w] = final

    ret, ans_markers = cv2.connectedComponents(ans)
    return ans_markers


def concatenateMarkers(
        markers1: np.ndarray,
        markers2: np.ndarray
):
    _markers1 = markers1.copy()
    _markers2 = markers2.copy()
    _markers1[markers2 > 0] = 0
    _markers2[_markers2 > 0] += markers1.max()
    _markers1 += _markers2
    return _markers1


def segmentNoCircle(
        markers: np.ndarray,
        min_matchShapes: float = .1,
        min_area: int = 20
):
    n = markers.max()
    is_circle = np.zeros_like(markers, 'int32')
    no_circle = is_circle.copy()
    ix1, ix2 = 1, 1
    for i in range(1, n + 1):
        loc = (markers == i)
        if not loc.any():
            continue
        marker = loc.astype('uint8')
        contours = get_single_contour(marker)
        area = cv2.contourArea(contours)
        ret = cv2.matchShapes(match_contours, contours, 1, 0.)
        if ret < min_matchShapes or area < min_area:
            is_circle[loc] = ix1
            ix1 += 1
        else:
            no_circle[loc] = ix2
            ix2 += 1
    return is_circle, no_circle


def recursionOpenProcess(no_circle,
                         origin,
                         rethreshold=True,
                         isadaptive=True,
                         erode_size=3,
                         dilate_size=2,
                         max_iterations=3,
                         min_matchShapes=.1,
                         min_area=20,
                         cellMean=0):
    ans = np.zeros_like(no_circle, 'int32')
    canvas = np.zeros(list(no_circle.shape), 'uint8')
    datalist = []
    global gID
    gID = 1
    for label in range(1, no_circle.max() + 1):
        loc = (no_circle == label)
        marker = loc.astype('uint8')
        contours = get_single_contour(marker)
        marked_image = origin.copy()
        marked_image[~marker] = 0
        x, y, w, h = cv2.boundingRect(contours)
        cut_image = marked_image[y: y + h, x: x + w]
        if rethreshold:
            if isadaptive:
                mk = cv2.adaptiveThreshold(cut_image, 1, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 29, 1)
            else:
                _, mk = cv2.threshold(cut_image, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            mk = marker[y: y + h, x: x + w]
        dt = cv2.distanceTransform(mk, cv2.DIST_L2, 3)
        process_ans = recursion_devide(dt, 0, erode_size, dilate_size, max_iterations,
                                       min_matchShapes, min_area)
        ans[y: y + h, x: x + w] = process_ans
    markers = np.zeros_like(ans)
    index = 1
    for i in range(1, ans.max() + 1):
        loc = ans == i
        if not loc.any():
            continue
        if origin[loc].mean() < cellMean:
            continue
        # 删除小的干扰项
        if getArea(loc) < 30:
            continue
        # 后处理
        cur = loc.astype('uint8')
        contour = get_single_contour(cur)
        score = get_match_score(contour)
        if (score > .1):
            x, y, w, h = cv2.boundingRect(contour)
            roi = cur[y:y + h, x:x + w]
            roi = remove_small_holes(roi)
            proc = afterprocess(roi)  # 注意调整最大值
            for j in range(1, proc.max() + 1):
                sub = (proc == j)
                markers[y:y + h, x:x + w][sub] = index + j - 1
                # 椭圆轮廓
                contour = get_single_contour(sub.astype('uint8'))
                ellipse = cv2.fitEllipse(contour)
                center, axes, angle = ellipse
                center = center[0] + x, center[1] + y
                ellipse = center, axes, angle
                cv2.ellipse(canvas, ellipse, (255, 255, 0), 2)
                datalist.append([center[0], center[1], axes[0], axes[1], angle])
            index += proc.max()
        else:
            markers[loc] = index
            index += 1
            # 椭圆轮廓
            ellipse = cv2.fitEllipse(contour)
            center, axes, angle = ellipse
            datalist.append([center[0], center[1], axes[0], axes[1], angle])
            cv2.ellipse(canvas, ellipse, (255, 255, 0), 2)
    values = np.array(datalist)
    table=pd.DataFrame(values, columns=['centerX', 'centerY', 'axisA', 'axisB', 'rotateAngle'])
    # print(table.shape)
    return markers, canvas, table


def get_match_score(contour):
    ret = cv2.matchShapes(match_contours, contour, 1, 0.)
    return ret


def afterprocess(marker, layer=0):
    dt = cv2.distanceTransform(marker, cv2.DIST_L2, 3)
    dt = ((dt - dt.min()) / (dt.max() - dt.min())) * 255
    dt = dt.astype('uint8')
    sure_fg = (dt > 128).astype('uint8') * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cv2.morphologyEx(sure_fg, cv2.MORPH_OPEN, kernel, iterations=2)
    unknown = cv2.subtract(marker, sure_fg)
    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1  # 用label进行控制
    markers[unknown == 255] = 0
    markers = cv2.watershed(cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR), markers)  # 分水岭的地方就编程-1
    markers[markers == -1] = 1
    markers -= 1
    # print(set(markers.flat))
    ans = markers.copy()
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
    # img_show([marker,dt,sure_fg,ans])

    return ans


def recursion_devide(img, cnt, erode_size=3, dilate_size=2, max_iterations=3, min_matchShapes=.2, min_area=20):
    global gID
    img = img.astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erode_size, erode_size))
    img = cv2.morphologyEx(img, cv2.MORPH_ERODE, kernel)
    ans = np.zeros_like(img, 'int32')
    _, cur_mark = cv2.connectedComponents(img)
    cur_mark = cur_mark.astype('int32')
    for i in range(1, cur_mark.max() + 1):
        loc = (cur_mark == i)
        label = loc.astype('uint8')
        if not label.any():
            continue
        contours = cv2.findContours(label, 1, cv2.CHAIN_APPROX_NONE)
        contours = contours[1][0]
        ret = cv2.matchShapes(match_contours, contours, 1, 0.)
        area = cv2.contourArea(contours)
        if ret > min_matchShapes and area > min_area and cnt < max_iterations:
            # 确认是多个细胞
            res = recursion_devide(label, cnt + 1, erode_size, dilate_size)
            res_labels = list(set(res.flat))
            if 0 in res_labels:
                res_labels.remove(0)
            if -1 in res_labels:
                res_labels.remove(-1)
            for res_label in res_labels:
                ans = ans.copy()
                ans[(res == res_label).copy()] = gID
                gID += 1
        else:
            ans[loc] = gID
            gID += 1
    ans = dilate_marks(ans, dilate_size)
    return ans


def dilate_marks(marks, x):
    if not marks.any():
        return marks
    labels = list(set(marks.flat))
    ans = np.zeros_like(marks, 'int32')
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (x, x))

    for label in labels:
        loc = (marks == label).astype('uint8')
        dilate = cv2.morphologyEx(loc, cv2.MORPH_DILATE, kernel)
        ans[dilate.astype('bool')] = label
    return ans


def calc_table(markers):
    _markers = np.zeros_like(markers, 'int32')
    columns = ['Area', 'Length', 'centroidX', 'centroidY']
    df = pd.DataFrame(columns=columns)
    index = 1
    for label in range(1, markers.max() + 1):
        loc = markers == label
        if not loc.any():
            continue
        _markers[loc] = index
        marker = loc.astype('uint8')
        contour = get_single_contour(marker)
        area = cv2.contourArea(contour)
        length = cv2.arcLength(contour, True)
        # x, y, w, h = cv2.boundingRect(contour)
        # roi = marker[y: y + h, x: x + w]
        # plt.imshow(roi)
        # plt.show()
        x, y = contour_centroid(contour)
        df = df.append(pd.DataFrame([[area, length, x, y]], columns=columns, index=[index]))
        index += 1

    return _markers, df
