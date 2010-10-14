"""seagull/images.py
   Create dictionaries with button, checkbox and radio button images from
   Sikuli projects.
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
