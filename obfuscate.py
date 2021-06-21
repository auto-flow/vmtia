import os
import shutil
from pathlib import Path
project=Path('./').absolute().parts[-1]

ppath=Path(f'../{project}_dist')
if ppath.exists():
    shutil.rmtree(ppath.as_posix())
    ppath.mkdir(parents=True,exist_ok=True)

cmd=f'pyarmor obfuscate {project}/__init__.py -O ../{project}_dist/{project} --no-cross-protection'

wanted=['config','res']
wanted+=['THU','sample']

for dname in Path(project).iterdir():
    if dname.is_dir() and dname.name in wanted:
        shutil.copytree(dname.as_posix(), (ppath /project/ dname.name).as_posix())

os.system(cmd)

os.system(cmd)
for file in Path('./').iterdir():
    if file.is_file():
        shutil.copy(file.as_posix(), (ppath / file.name).as_posix())



