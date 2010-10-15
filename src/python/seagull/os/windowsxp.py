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

from sikuli.Region import Region
from sikuli.Sikuli import SCREEN

"""Window theme
"""
WINDOW_TITLEBAR_HEIGHT = 30
WINDOW_TITLEBAR_MINIMIZE_BUTTON_OFFSET = -62
WINDOW_TITLEBAR_MAXIMIZE_BUTTON_OFFSET = -39
WINDOW_TITLEBAR_CLOSE_BUTTON_OFFSET = -16

"""Windows task bar
"""
WINDOWS_TASKBAR_REGION = Region(0, SCREEN.getH() - 31, SCREEN.getW(), 31)

"""Paths
"""
INTERNET_EXPLORER_PATH = r'C:\Program Files\Internet Explorer\IEXPLORE.EXE'
MSOFFICE_ROOT_PATH = r'C:\Program Files\Microsoft Office'
WINDOWS_EXPLORER_PATH = r'C:\WINDOWS\explorer.exe'
CONTROL_PANEL_PATH = r'C:\WINDOWS\system32\control.exe'
NOTEPAD_PATH = r'C:\WINDOWS\system32\notepad.exe'
