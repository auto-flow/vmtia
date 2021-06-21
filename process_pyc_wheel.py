import os
from pathlib import Path
project=Path('./').absolute().parts[-1]

exec(f'from {project}.main import __version__')

os.chdir('dist')
os.system('unzip *.whl')
os.system('rm *.whl')

for path in Path('./').iterdir():
    if path.as_posix().endswith('dist-info'):
        path=path/'RECORD'
        lines = Path(path).read_text().split('\n')
        new_lines = []
        for line in lines:
            if line.split(',')[0].endswith('py'):
                continue
            new_lines.append(line)
        txt = '\n'.join(new_lines)
        Path(path).write_text(txt)
    else:
        for subpath in path.iterdir():
            if subpath.is_file() and subpath.suffix=='.py':
                subpath.unlink()

whl=f'{project}-{__version__}-py3.6-none-any.whl'   #LDSeg-0.0.1-py3-none-any.whl
cmd=f"zip -qr {whl} ./*"
print(cmd)
os.system(cmd)
