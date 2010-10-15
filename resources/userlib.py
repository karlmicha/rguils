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

import sys, os, os.path

# Directory where user-defined python modules and Sikuli projects are located
# the default is C:\Documents and Settings\username\Sikuli on Windows XP and
# ~/Sikuli on Linux.
# If necessary, change this to the location of your Sikuli projects and python
# modules
USERLIBDIR = os.path.join(os.path.expanduser('~'), 'Sikuli')

def addlibdir(dirname):
    """Adds the specified directory to the python module path, unless it is
       already included in the path.
    """
    if dirname not in sys.path:
        sys.path.append(dirname)

def adduserlibs():
    """Adds the directory defined in USERLIBDIR and all subdirectories with the
       extension .sikuli to the python module path.
    """
    addlibdir(USERLIBDIR)
    for moduledir in os.listdir(USERLIBDIR):
        if moduledir.endswith('.sikuli'):
            addlibdir(os.path.join(USERLIBDIR, moduledir))

def getmodulepath(modulename):
    """Returns the full path of a Sikuli project module.
       To load a module in a Sikuli script, use
       execfile(getmodulepath(modulename)).
    """
    return USERLIBDIR + '\\' + modulename + '.sikuli\\' + modulename + '.py'

adduserlibs()
