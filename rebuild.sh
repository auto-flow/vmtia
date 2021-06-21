#!/usr/bin/env bash
# 生成py版本的wheel
rm -rf build
rm -rf dist
rm -rf *.egg-info
python setup.py bdist_wheel
pip uninstall LDSeg -y
cd dist
pip install LDSeg*
echo "finish rebuild"