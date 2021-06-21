#!/usr/bin/env bash
# 生成pyc版本的wheel
rm -rf build
rm -rf dist
rm -rf *.egg-info
pip uninstall LDSeg -y
# 生成build文件夹
python setup.py build
# 生成pyc文件
python convert_build_to_pyc.py
# 预打包
python setup.py bdist_wheel
# 处理这个包
python process_pyc_wheel.py

cd dist
pip install LDSeg*.whl
echo "finish rebuild"