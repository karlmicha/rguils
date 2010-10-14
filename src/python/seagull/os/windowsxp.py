"""seagull/os/windowsxp.py
   Windows XP settings
   Author: Karl-Michael Schneider
   Date: 6/1/2010
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
