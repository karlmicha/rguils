"""
Copyright (c) 2010 Karl-Michael Schneider

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from sikuli.Sikuli import Env

# only Windows is supported at this point

def getWindowsVersion():
    """Returns the Windows version.
       The return values is 'XP', 'Vista' or '7'.
    """
    rawversion = Env.getOSVersion()
    if rawversion[0] == '7':
        return '7'
    elif rawversion[0] == '6':
        return 'Vista'
    elif rawversion[0] == '5':
        return 'XP'
    else:
        raise Exception('unknown OS version: %s' % rawversion)

WINDOWS_VERSION = getWindowsVersion()
if WINDOWS_VERSION == 'XP':
    from seagull.os.windowsxp import *
elif WINDOWS_VERSION == 'Vista':
    from seagull.os.windowsvista import *
elif WINDOWS_VERSION == '7':
    from seagull.os.windows7 import *
else:
    raise Exception('Windows %s not implemented' % WINDOWS_VERSION)
