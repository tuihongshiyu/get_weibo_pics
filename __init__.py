
import sys

if sys.version_info[0] == 3:

    from .__main__ import *

    #from .common import *
    #from .version import *
    #from .cli_wrapper import *
    #from .extractor import *
else:
    # Don't import anything.
    pass
