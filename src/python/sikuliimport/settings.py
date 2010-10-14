"""sikuliimport/settings.py
   Settings for Sikuli projects.
"""

from seagull.os.windows.util import getWindowsVersion

__IMAGE_DIR = '/home/kschneider/perforce-workspace-linux/DEPARTMENTS/QA/Automation/DigitalMirror/Sikuli/images'

__COMMON_PROJECTS = ['digitalmirror']

__WINDOWS_VERSION = getWindowsVersion()

if __WINDOWS_VERSION == 'XP':
    __ADD_PROJECTS = ['windowsxp', 'digitalmirrorxp']
elif __WINDOWS_VERSION == 'Vista':
    __ADD_PROJECTS = ['windowsvista', 'digitalmirrorvista']
elif __WINDOWS_VERSION == '7':
    __ADD_PROJECTS = ['windows7', 'digitalmirrorwin7']
else:
    raise Exception('unknown Windows version: %s' % __WINDOWS_VERSION)

# full paths of sikuli projects that should be imported
SIKULI_PROJECT_DIRS = []
for __project in __COMMON_PROJECTS:
    SIKULI_PROJECT_DIRS.append(__IMAGE_DIR + '/' + __project + '.sikuli')
for __project in __ADD_PROJECTS:
    SIKULI_PROJECT_DIRS.append(__IMAGE_DIR + '/' + __project + '.sikuli')
