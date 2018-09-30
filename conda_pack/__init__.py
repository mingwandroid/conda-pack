from __future__ import print_function, absolute_import
import sys
import os
sys.path.append(os.path.dirname(__file__))
__name__='conda_pack'
from .core import CondaEnv, File, CondaPackException, pack

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
from .cli import main
main()

