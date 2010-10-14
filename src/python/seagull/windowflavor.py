"""seagull/windowflavor.py
   Window properties that depend on OS, version, theme, etc.
   Author: Karl-Michael Schneider
   Date: 10/1/2010
"""

import logging
# only Windows is supported at this point
from seagull.os.windows.util import getWindowsVersion

_LOGGER = logging.getLogger(__name__)

WINDOWS_VERSION = getWindowsVersion()
_LOGGER.info('Windows version is %s' % WINDOWS_VERSION)
if WINDOWS_VERSION == 'XP':
    from seagull.os.windowsxp import *
elif WINDOWS_VERSION == 'Vista':
    from seagull.os.windowsvista import *
elif WINDOWS_VERSION == '7':
    from seagull.os.windows7 import *
else:
    raise Exception('Windows %s not implemented' % WINDOWS_VERSION)
