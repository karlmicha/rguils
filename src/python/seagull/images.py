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

import sikuliimport.projects

IMG_BUTTONS = {}
IMG_BUTTONS_DISABLED = {}
IMG_CHECKBOXES = { 'checked' : [], 'unchecked' : [] }
IMG_RADIOBUTTONS = { 'checked' : [], 'unchecked' : [] }

for symbol in dir(sikuliimport.projects):
    if symbol.startswith('IMG_'):
        value = eval('sikuliimport.projects.%s' % symbol)
        if symbol.startswith('IMG_BUTTON_'):
            buttonname = symbol.split('_')[2].lower()
            try:
                IMG_BUTTONS[buttonname].append(value)
            except KeyError:
                IMG_BUTTONS[buttonname] = [value]
        elif symbol.startswith('IMG_DISABLED_BUTTON_'):
            buttonname = symbol.split('_')[3].lower()
            try:
                IMG_BUTTONS_DISABLED[buttonname].append(value)
            except KeyError:
                IMG_BUTTONS_DISABLED[buttonname] = [value]
        elif symbol.startswith('IMG_CHECKED_BOX'):
            IMG_CHECKBOXES['checked'].append(value)
        elif symbol.startswith('IMG_UNCHECKED_BOX'):
            IMG_CHECKBOXES['unchecked'].append(value)
        elif symbol.startswith('IMG_CHECKED_RADIOBUTTON'):
            IMG_RADIOBUTTONS['checked'].append(value)
        elif symbol.startswith('IMG_UNCHECKED_RADIOBUTTON'):
            IMG_RADIOBUTTONS['unchecked'].append(value)
