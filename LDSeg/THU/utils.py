from copy import deepcopy
from pathlib import Path

from PIL import Image, ImageSequence
from skimage import morphology
from random import randint
import cv2
import pylab as plt
import numpy as np
from scipy.ndimage.filters import sobel

def get_color(type='rgb'):  # hex rgb
    color = []
    for i in range(3):
        color.append(randint(0, 255))
    if type == 'hex':
        hex = '#' + ''.join(f"{x:02x}" for x in color)
        return hex
    else:
        return color

def get_single_contour(marker):
    contours = cv2.findContours(marker, 1, cv2.CHAIN_APPROX_NONE)
    len_list = [len(c) for c in contours[1]]
    ind = len_list.index(max(len_list))
    contours = contours[1][ind]
    return contours

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

def img_show(image_to_show, axis='on', cmap=None, title_list=None,filename=None,title=None):

    def _row_col(number):
        """
        """
        row_num = 0
        col_num = 0
        for num in range(1, number + 1):
            if number % num == 0:
                temp_row_num = num
                temp_col_num = int(number / num)
                if temp_row_num > temp_col_num:
                    break
                if temp_row_num > row_num:
                    row_num = temp_row_num
                    col_num = temp_col_num

        return row_num, col_num

    try:
        assert (isinstance(image_to_show, list) or isinstance(image_to_show, np.ndarray))
    except:
        raise AssertionError('Input must be list or numpy ndarray!')

    if isinstance(image_to_show, np.ndarray):
        plt.imshow(image_to_show, cmap=cmap)
        plt.axis(axis)
    else:
        row, col = _row_col(len(image_to_show))
        if title_list:
            try:
                assert len(image_to_show) == len(title_list)
            except:
                raise AssertionError('The number of images is different from the number of titles!')
            for index, (image, title) in enumerate(zip(image_to_show, title_list)):
                plt.subplot(row, col, index + 1)
                plt.imshow(image, cmap=cmap)
                plt.axis(axis)
                plt.title(title)
        else:
            for index, image in enumerate(image_to_show):
                plt.subplot(row, col, index + 1)
                plt.imshow(image, cmap=cmap)
                plt.axis(axis)
    if filename is not None:
        plt.savefig(filename)
    if title is not None:
        plt.title(title)
    plt.show()
    return

def convert2gray(
        img: np.ndarray
):
    channels = img.shape.__len__()
    ans = img
    if channels == 3:
        ans = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return ans


def local_histogram_equalization(
        img: np.ndarray,
        clipLimit=2.0,
        gridSize=10
):
    img = deepcopy(img)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(gridSize, gridSize))
    if len(img.shape) == 3:
        for i in range(img.shape[0]):
            img[i] = clahe.apply(img[i])
    else:
        img = clahe.apply(img)
    img = img_norm(img)
    return img.astype(np.uint8)

def img_norm(
        img: np.ndarray
) :
    img = (img - np.min(img)) / float(np.max(img) - np.min(img))
    img *= 255.
    img = img.astype(np.uint8)
    return img

def remove_small_holes(
        binary: np.ndarray,
        area_threshold: int = 100,
        connectivity: int = 1,
        max_val: int = 255
):
    removed = binary.astype('bool')
    removed = morphology.remove_small_holes(removed, area_threshold=area_threshold, connectivity=connectivity).astype('uint8')
    return (removed * max_val)

def remove_small_ojects(
        binary: np.ndarray,
        min_size: int = 100,
        connectivity: int = 1,
        max_val: int = 255
):
    removed = binary.astype('bool')
    removed = morphology.remove_small_objects(removed, min_size=min_size, connectivity=connectivity).astype('uint8')
    return (removed * max_val)

def getArea(gray):
    return gray.flatten().nonzero()[0].size

def displayMarkers(
        markers:np.ndarray
):
    n=markers.max()
    h,w=markers.shape
    canvas=np.zeros((h,w,3),'uint8')
    for i in range(1,n+1):
        canvas[markers==i]=get_color()
    return canvas

def draw_outline(input,output,output_is_line=False):
    tname='.temp.jpg'
    plt.imsave(tname,input)
    # energy=cv2.cvtColor(input,cv2.COLOR_GRAY2BGR)
    energy=plt.imread(tname).copy()
    if output_is_line:
        outline=output.copy()
    else:
        outline=sobel_edge(output)
    energy[outline.astype('bool')]=(255,0,0)
    return energy

def sobel_edge(img):
    imx = np.zeros(img.shape)
    imy = np.zeros(img.shape)
    sobel(img, 0, imx)
    sobel(img, 1, imy)
    magnitude = np.sqrt(imx ** 2 + imy ** 2)
    return magnitude

def contour_centroid(contour):
    moments = cv2.moments(contour)
    # get centroid
    centroid = (int(moments['m10'] / (moments['m00'] + 0.1 * 10e-10)),
                int(moments['m01'] / (moments['m00'] + 0.1 * 10e-10)))
    return centroid
