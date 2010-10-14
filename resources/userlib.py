"""userlib.py
   Adds a user-defined directory and all *.sikuli subdirectories to the python
   module path, so that user-defined modules and Sikuli projects can be
   imported into python scripts run with Sikuli Script.
   Copy this file into the Sikuli installation directory, e.g. on Windows:
   C:\Program Files\Sikuli\userlib.py
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
