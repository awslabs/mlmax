"""Magic to allow .ipynb files to locate custom modules.

Usage: always have this file in the same directory as .ipynb files.
"""

import os
import subprocess
from pathlib import Path
from typing import Union

########################################################################################
# Additional PYTHONPATH to allow notebooks to import custom modules at a few pre-defined
# places.


def sys_path_append(o: Union[str, os.PathLike]) -> str:
    posix_path: str = o.as_posix() if isinstance(o, Path) else Path(o).as_posix()
    return 'sys.path.append("{}")'.format(posix_path)


_pythonpath = [
    "import sys, os",
    sys_path_append(os.getcwd()),
]

# Add GIT_ROOT/ and a few other subdirs
try:
    _p = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if _p.returncode == 0:
        _git_root: str = _p.stdout[:-1].decode("utf-8")  # Remove trailing '\n'
        _git_root_p: Path = Path(_git_root)
        _pythonpath += [
            sys_path_append(_git_root_p),  # GIT_ROOT
            sys_path_append(_git_root_p / "src"),  # GIT_ROOT/src
            sys_path_append(_git_root_p / "notebooks"),  # GIT_ROOT/notebooks
        ]
except:  # noqa: E722
    pass

c.InteractiveShellApp.exec_lines = _pythonpath  # type: ignore # noqa: F821
########################################################################################
