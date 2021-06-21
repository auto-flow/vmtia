#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

project=Path('./').absolute().parts[-1]

# bdpath=Path(f'build/lib/{project}')
#
# for file in  bdpath.iterdir():
#     if file.is_file() and file.suffix=='.py':
#         os.system(f'python -m py_compile {file}')
#         file.unlink()
#         dname=file.parent
#         stem=file.stem
#         fstem=file.as_posix().replace('.py','')
#         cmd=f'mv {dname}/__pycache__/{stem}* {fstem}.pyc'
#         print(cmd)
#         os.system(cmd)

os.system(f'python3 -O -m compileall -b build/lib/{project}')




