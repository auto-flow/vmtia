#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Tang QiChun
# Mail: qichun.tang@xtalpi.com
# Created Time:  2019.6.1
#############################################
import os
import sys
from pathlib import Path

from setuptools import setup, find_packages
from LDSeg.main import __version__

name="LDSeg"
description = "Visualized Modeling Tool for Image Algorithms"


def get_recursion_file_list(dname):
    global recursion_file_list
    recursion_file_list.append(f'{dname}\\*')
    for item in Path(dname).iterdir():
        if item.is_dir():
            get_recursion_file_list(item)

def get_file_list(dname):
    os.chdir('LDSeg')
    global recursion_file_list
    recursion_file_list=[]
    get_recursion_file_list(dname)
    os.chdir('..')
    return recursion_file_list

# print(get_file_list('res'))
# exit(0)


setup(
    name=name,
    version=__version__,
    keywords=("pip", name),
    description=description,
    long_description=description,
    license="MIT Licence",

    author="Tang QiChun",
    author_email="qichun.tang@xtalpi.com",
    package_data={name: get_file_list('res')+[
                         'config/*',
                         'sample/*.jpg',
                         'THU/*.py',
                         '*.dll',
                         '*.lic',
                         '*.key',
                         '*.so',
                         ]},
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        "matplotlib==3.0.2",
        "Pygments==2.3.1",
        "pandas==0.23.4",
        "numpy==1.15.4",
        "scipy==1.1.0",
        "opencv_python==3.4.2.17",
        "PyWavelets==1.0.1",
        "pyperclip==1.7.0",
        "graphviz==0.10.1",
        "PyQt5>=5.0.0",
        "imageio>=2.0.0",
        "pywt==1.0.6",
        "scikit-image==0.14.1",
    ],
    entry_points={
        'console_scripts': [
            'LDSeg=LDSeg.main:main',
        ],
    },
)
