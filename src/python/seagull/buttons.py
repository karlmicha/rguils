"""seagull/buttons.py
   A class to model a set of buttons in a window or region.
   Author: Karl-Michael Schneider
   Created: 6/2/10
"""

import logging
from sikuli.Sikuli import SCREEN
from sikuli.Region import Region
from seagull.util import bestMatches, bestMatch, NO_MODIFIER, Wait

_LOGGER = logging.getLogger(__name__)

class Buttons:
    """Models a set of buttons in a window or region.
       A button set is created by providing one or more images for each button.
       The class locates all the buttons that exist in the region. You can
       check which buttons exist, whether they are enabled or disabled, and
       click on them.
    """

    def __init__(self, buttons, disabled_buttons = None, region = SCREEN,
            name = None):
        """Creates a new instance.
           Buttons is a dictionary object where each key is a button name and
           the value is a list of images of the specified button.
           Disabled_buttons is a dictionary object with the same format and the
           same keys, or a subset of the keys. Images in disabled_buttons
           represent disabled buttons.
           Names in disabled_buttons that do not exist in buttons are ignored.
           If region is not specified, the entire screen is used.
           Each button can exist only once in the region. If the same button is
           found twice, whether enabled or disabled, Exception is raised.
           The name is only used in log messages.
        """
        self._buttons = buttons
        self._disabled_buttons = disabled_buttons
        self._region = region
        self._name = name
        self._button_matches = None
        if name is not None:
            self._debugprefix = '[%s] ' % name
        else:
            self._debugprefix = ""

        # _button_images contains all images
        # _button_names[i] is the name of the button in _button_images[i]
        # _button_disabled[i] is True if _button_images[i] is a disabled button
        # _button_image_index[i] is the index of _button_images[i] in
        # _buttons[name] or _disabled_buttons[name]
        # _button_index[name] is the index in _button_images of the first image
        # of the named button
        # _disabled_button_index[name] is the index in _button_images of the
        # first image of the disabled named button (if any)
        self._button_images = []
        self._button_names = []
        self._button_disabled = []
        self._button_image_index = []
        self._button_index = {}
        self._disabled_button_index = {}
        names = self._buttons.keys()
        names.sort()
        for name in names:
            self._button_index[name] = len(self._button_images)
            for j, image in enumerate(self._buttons[name]):
                self._button_images.append(image)
                self._button_names.append(name)
                self._button_disabled.append(False)
                self._button_image_index.append(j)
            if self._disabled_buttons is not None and \
                    name in self._disabled_buttons:
                self._disabled_button_index[name] = len(self._button_images)
                for j, image in enumerate(self._disabled_buttons[name]):
                    self._button_images.append(image)
                    self._button_names.append(name)
                    self._button_disabled.append(True)
                    self._button_image_index.append(j)
        _LOGGER.info('%sdeclared %d buttons: %s',
                self._debugprefix, len(names), ', '.join(names))

    def find_buttons(self):
        """Finds all buttons in the region.
        """
        # list of (i, match) tuples where match is a match of _button_images[i]
        matches = bestMatches(self._button_images, region = self._region,
                minOverlap = 0.5)
        _LOGGER.info('%sfound %d buttons', self._debugprefix, len(matches))

        # index matches by name
        self._button_matches = {}
        duplicate_names = []
        for i, match in matches:
            name = self._button_names[i]
            if name in self._button_matches:
                duplicate_names.append(name)
            self._button_matches[name] = (i, match)
            if self._button_disabled[i]:
                state = 'disabled'
            else:
                state = 'enabled'
            _LOGGER.info("%s is '%s' %s (image %d)",
                    str(match), name, state, self._button_image_index[i])
        if len(duplicate_names) > 0:
            raise Exception("found duplicate buttons: %s" %
                    (', '.join(duplicate_names)))

    def button_count(self):
        """Returns the number of buttons that were found in the region.
        """
        return len(self._button_matches)

    def button_names(self):
        """Returns a list of the button names that were found in the region.
           The list is in no particular order.
        """
        return self._button_matches.keys()

    def exists_button(self, name):
        """Returns True if the specified button was found in the region.
        """
        return name in self._button_matches

    def is_button_enabled(self, name):
        """Returns True if the specified button is not disabled.
           A button can only be disabled if there are images of the disabled
           button.
        """
        i, match = self._button_matches[name]
        return not self._button_disabled[i]

    def all_buttons_enabled(self):
        """Returns True if none of the buttons are disabled.
        """
        for name in self.button_names():
            if not self.is_button_enabled(name):
                return False
        return True

    def button_image_index(self, name):
        """Returns the index of the best matching button image.
        """
        i, match = self._button_matches[name]
        return self._button_image_index[i]

    def update_button(self, name):
        """Updates the specified button so that this button set reflects the
           current state of the button.
        """
        _LOGGER.debug("%sgetting current state of '%s' button",
                self._debugprefix, name)
        i, match = self._button_matches[name]
        button_region = Region(match).nearby(15)
        images = []
        images.extend(self._buttons[name])
        if self._disabled_buttons is not None and \
                name in self._disabled_buttons:
            images.extend(self._disabled_buttons[name])
        i_best, m_best = bestMatch(images, region = button_region,
                minOverlap = 0.5)
        disabled = i_best >= len(self._buttons[name])
        if disabled:
            _LOGGER.info("'%s' button (image %d) is disabled",
                    name, i_best -len(self._buttons[name]))
            s = self._disabled_button_index[name]
            self._button_matches[name] = \
                    (s + i_best - len(self._buttons[name]), m_best)
        else:
            _LOGGER.info("'%s' button (image %d) is enabled", name, i_best)
            s = self._button_index[name]
            self._button_matches[name] = (s + i_best, m_best)

    def update_buttons(self):
        """Updates all buttons.
        """
        for name in self.button_names():
            self.update_button(name)

    def waitUntilButtonIsEnabled(self, name, timeout):
        """Waits until the specified button is no longer disabled.
           Raises Exception if the button is still disabled after the specified
           timeout.
        """
        if timeout is None:
            _LOGGER.info("%swaiting for '%s' button to be enabled",
                    self._debugprefix, name)
        else:
            _LOGGER.info("%swaiting for '%s' button to be enabled, timeout set to %f seconds",
                    self._debugprefix, name, timeout)
        waiting = Wait(timeout,
                exception_message =
                "'%s' button still disabled after %f seconds" %
                (name, timeout))
        while not self.is_button_enabled(name):
            waiting.wait()
            self.update_button(name)

    def waitUntilAllButtonsEnabled(self, timeout):
        """Waits until none of the buttons is disabled.
           Raises Exception if some button is still disabled after the
           specified timeout.
        """
        if timeout is None:
            _LOGGER.info('%swaiting until all buttons are enabled',
                    self._debugprefix)
        else:
            _LOGGER.info('%swaiting until all buttons are enabled, timeout set to %f seconds',
                    self._debugprefix, timeout)
        waiting = Wait(timeout,
                exception_message =
                'some button still disabled after %f seconds' % timeout)
        while not self.all_buttons_enabled():
            waiting.wait()
            self.update_buttons()

    def click(self, name):
        """Clicks the specified button.
        """
        i, match = self._button_matches[name]
        _LOGGER.info("%sclick '%s': %s", self._debugprefix, name, str(match))
        SCREEN.click(match, NO_MODIFIER)
