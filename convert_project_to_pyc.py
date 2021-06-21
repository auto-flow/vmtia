import os
import shutil
from pathlib import Path
from platform import platform

project = Path('./').absolute().parts[-1]
new_project = project + '_pyc'
ppath = Path(f'../{new_project}')
ppath.mkdir(exist_ok=True, parents=True)
shutil.copytree(f'./{project}', (ppath / project).as_posix())
os.system(f'python -O -m compileall -b {ppath / project}')

if 'windows' in platform().lower():
    cmd = fr'del {ppath / project}\*.py'
else:   # for Linux or MaxOS
    cmd = fr'rm {ppath / project}/*.py'

os.system(cmd)
for file in Path('./').iterdir():
    if file.is_file():
        shutil.copy(file.as_posix(), (ppath / file.name).as_posix())



