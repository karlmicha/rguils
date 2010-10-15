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

import os, os.path, subprocess, tempfile
from java.awt import Toolkit
from java.awt.datatransfer import DataFlavor
from sikuli.Sikuli import openApp, Env
from sikuli.Key import Key, KEY_CTRL, KEY_SHIFT
from seagull.util import typeKeys

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

def getUsername():
    """Returns the name of the current user.
    """
    return os.getlogin()

def getMSOfficeVersion():
    """Returns the Microsoft Office version as an integer between 9 and 12.
       Raises Exception if the version cannot be determined.
    """
    for version in [9, 10, 11, 12]:
        if os.path.exists(os.path.join(MSOFFICE_ROOT_PATH,
                'OFFICE%d' % version)):
            return version
    if os.path.exists(os.path.join(MSOFFICE_ROOT_PATH, 'Office')):
        return 9
    raise Exception('cannot determine MS Office version')

def getTempDir():
    """Returns the directory to create temporary files in.
    """
    return tempfile.gettempdir()

def makeTempFile(suffix = "", close = False):
    """Creates a temporary file.
       Returns an open filehandle and the filename. The file is opened for
       writing.
       To create a file name tmpname.bat, you must use suffix = '.bat'.
       If suffix is empty or not specified, the filename has no suffix.
       If close is True, closes the file.
       This is not secure, may create race conditions, but right now there is
       no better alternative.
    """
    tmpfilename = tempfile.mktemp(suffix = suffix)
    tmpfile = open(tmpfilename, 'w')
    if close:
        tmpfile.close()
    return tmpfile, tmpfilename

def saveInTempFile(contents, suffix = ""):
    """Writes the specified contents to a temporary file and returns the
       filename.
    """
    tmpfile, tmpfilename = makeTempFile(suffix)
    tmpfile.write(contents)
    tmpfile.close()
    return tmpfilename

def getInternetExplorerPath():
    """Get pathnames of common Windows applications.
    """
    return INTERNET_EXPLORER_PATH

def getWindowsExplorerPath():
    """Returns the path of the Windows Explorer executable."""
    return WINDOWS_EXPLORER_PATH

def getMSOfficePath():
    """Returns the folder path of MS Office."""
    officeversion = getMSOfficeVersion()
    if officeversion == 9:
        officedir = 'Office'
    else:
        officedir = 'OFFICE%d' % officeversion
    return os.path.join(MSOFFICE_ROOT_PATH, officedir)

def getOutlookPath():
    """Returns the path of the Outlook executable."""
    return os.path.join(getMSOfficePath(), 'OUTLOOK.EXE')

def getNotepadPath():
    """Returns the path of the Notepad executable."""
    return NOTEPAD_PATH

def getControlPanelPath():
    """Returns the path of the control panel executable."""
    return CONTROL_PANEL_PATH

def startCommand(command, *arguments, **kwds):
    """Runs the specified command with the specified arguments in a new process
       using the Windows start command.
       Optional arguments: startargs
       If startargs is specified, it must be a list of arguments that are
       passed to the start command. Type start /? in a Windows command prompt
       to see a list of valid arguments.
       Returns a subprocess.Popen instance.
    """
    cmdlist = ['cmd', '/c', 'start']
    if 'startargs' in kwds:
        cmdlist.extend(kwds['startargs'])
    cmdlist.append(command)
    cmdlist.extend(arguments)
    return subprocess.Popen(cmdlist)

def runApplication(executablepath, *args, **kwds):
    """Runs an application with the specified arguments.
       If the application is run without arguments, uses openApp to launch it.
       Otherwise, uses the Windows start command.
    """
    if len(filter(lambda x:x is not None, args)) == 0:
        openApp(executablepath)
    else:
        startCommand(executablepath, *args, **kwds)

def openInternetExplorer(url = None):
    """Opens Internet Explorer.
       If url is not None, it is opened in Internet Explorer.
    """
    runApplication(getInternetExplorerPath(), url)

def openWindowsExplorer(folder = None, select = None):
    """Opens Windows Explorer with a new single-pane window.
       If folder is not None, it will be opened in the window. Otherwise, the
       default folder will be opened (usually C:\).
       If select is not None, it should be a folder or filename in the opened
       folder, and it will be selected.
    """
    args = ['/n']
    if folder is not None:
        args.extend([',/root,', folder])
    if select is not None:
        args.extend([',/select,', select])
    runApplication(getWindowsExplorerPath(), *args)

def openOutlook():
    """Opens Outlook."""
    openApp(getOutlookPath())

def openNotepad(filename = None):
    """Opens Notepad."""
    runApplication(getNotepadPath(), filename)

def keyRightClick(region = None):
    """Right clicks using the keyboard.
       If region is not None, clicks on the region first.
    """
    typeKeys(Key.F10, modifiers = KEY_SHIFT, region = region)

def keyCopy():
    """Types Control-C.
    """
    typeKeys('c', modifiers = KEY_CTRL)

def keyCut():
    """Types Control-X.
    """
    typeKeys('x', modifiers = KEY_CTRL)

def keyPaste():
    """Types Control-V.
    """
    typeKeys('v', modifiers = KEY_CTRL)

def getClipboardText():
    """Returns the clipboard contents. Returns None if the clipboard does not
       contain text.
    """
    contents = Toolkit.getDefaultToolkit().getSystemClipboard().getContents(
            None)
    if contents.isDataFlavorSupported(DataFlavor.stringFlavor):
        return str(contents.getTransferData(DataFlavor.stringFlavor))
    return None
