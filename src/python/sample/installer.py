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

import os, os.path, logging
from time import sleep
from sikuli.Sikuli import SCREEN, openApp
from sikuli.Region import Region
from sikuli.Key import Key, KEY_ALT
from sikuliimport.projects import IMG_INSTALLER_WELCOME
from seagull.window import AnchoredWindow
from seagull.buttons import Buttons
from seagull.checkboxes import VerticalCheckboxList
from seagull.util import Wait
from seagull.images import IMG_BUTTONS, IMG_BUTTONS_DISABLED, IMG_CHECKBOXES

_LOGGER = logging.getLogger(__name__)

WELCOME_WINDOW_TIMEOUT = 30
NEXT_BUTTON_ENABLED_TIMEOUT = 20
INSTALL_TIME_MAX_SECONDS = 600

ANCHOR_IMAGE_OFFSET_X = 3
ANCHOR_IMAGE_OFFSET_Y = 30
WINDOW_WIDTH = 499
WINDOW_HEIGHT = 392
BUTTON_REGION_HEIGHT = 48
CONFIRM_WINDOW_WIDTH = 349
CONFIRM_WINDOW_HEIGHT = 143

class Installer(AnchoredWindow):
    """Class to automate an installer."""

    pages = ['Welcome', 'Configure Shortcuts', 'Select Installation Folder',
            'Ready to Install', 'Installing', 'Complete', 'Cancelled']
    welcome_page = 0
    shortcuts_page = 1
    folder_page = 2
    install_page = 3
    installing_page = 4
    complete_page = 5
    cancelled_page = 6

    # defines which buttons exist on which page
    button_page_map = {
        'next' : [welcome_page, shortcuts_page, folder_page, installing_page],
        'back' : [welcome_page, shortcuts_page, folder_page, install_page,
                installing_page, complete_page, cancelled_page],
        'install' : [install_page],
        'finish' : [complete_page, cancelled_page],
        'cancel' : [welcome_page, shortcuts_page, folder_page, install_page,
                installing_page, complete_page, cancelled_page]
    }

    def __init__(self, installer_path):
        if not os.path.exists(installer_path):
            raise Exception('No such file: %s' % installer_path)
        self.path = installer_path
        AnchoredWindow.__init__(self, IMG_INSTALLER_WELCOME,
                ANCHOR_IMAGE_OFFSET_X, ANCHOR_IMAGE_OFFSET_Y,
                WINDOW_WIDTH, WINDOW_HEIGHT,
                name = 'installer', title = 'Setup')
        self.button_region = None
        self.button_images = IMG_BUTTONS
        self.disabled_button_images = IMG_BUTTONS_DISABLED
        self.buttons = None
        self.buttons_valid = None
        self.confirm_window_open = None
        self.confirm_window_region = None
        self.confirm_button_images = { 'yes' : IMG_BUTTONS['yes'],
                                       'no' : IMG_BUTTONS['no'] }
        self.confirm_buttons = None
        self.shortcut_checkboxes = None
        self.running = False
        self.installing = None
        self.page = None

    def _ensure(self, **states):
        for attr, value in states.iteritems():
            if value is not None:
                if value:
                    if not getattr(self, attr):
                        raise Exception('installer is not %s' % attr)
                else:
                    if getattr(self, attr):
                        raise Exception('installer is %s' % attr)

    def _ensure_button(self, name):
        if self.page not in self.button_page_map[name.lower()]:
            raise Exception("no '%s' button on '%s' page" %
                    (name, self.pages[self.page]))

    def _ensure_buttons_valid(self):
        if self.buttons_valid:
            return
        self.buttons.find_buttons()
        self.buttons_valid = True

    def _ensure_button_enabled(self, name):
        self._ensure_buttons_valid()
        if not self.buttons.is_button_enabled(name.lower()):
            raise Exception(name + ' button is not enabled')

    def run(self):
        """Runs the installer."""
        self._ensure(running = False)
        _LOGGER.info('Running %s', self.path)
        openApp(self.path)
        self.running = True
        self.installing = False
        self.anchor(WELCOME_WINDOW_TIMEOUT)
        _LOGGER.info('Installer window has appeared')
        self.page = self.welcome_page
        self.button_region = Region(self.getX(),
                self.getY() + self.getH() - BUTTON_REGION_HEIGHT,
                self.getW(), BUTTON_REGION_HEIGHT)
        self.buttons = Buttons(self.button_images,
                self.disabled_button_images, region = self.button_region)
        self.buttons.find_buttons()
        self.buttons_valid = True
        self.buttons.waitUntilButtonIsEnabled('next',
                NEXT_BUTTON_ENABLED_TIMEOUT)
        self.confirm_window_open = False
        self.confirm_window_region = Region(
                self.getX() + (self.getW() - CONFIRM_WINDOW_WIDTH) / 2,
                self.getY() + (self.getH() - CONFIRM_WINDOW_HEIGHT) / 2,
                CONFIRM_WINDOW_WIDTH, CONFIRM_WINDOW_HEIGHT)
        self.confirm_buttons = Buttons(self.confirm_button_images,
                region = self.confirm_window_region)
        _LOGGER.info('Waiting for Next button to be enabled')
        self.shortcut_checkboxes = None

    def next(self):
        """Clicks the Next button.
           Raises Exception if the Next button is not enabled.
        """
        self._ensure(running = True)
        self._ensure_button('Next')
        self._ensure_button_enabled('Next')
        self.buttons.click('next')
        sleep(1)
        self.page += 1
        self.buttons_valid = False
        _LOGGER.info('now on %s page', self.pages[self.page])

    def next_key(self):
        """Presses the Next button using the keyboard.
           Raises Exception if the Next button is not enabled.
        """
        self._ensure(running = True)
        self._ensure_button('Next')
        self._ensure_button_enabled('Next')
        self.setFocus()
        SCREEN.type('n', KEY_ALT)
        sleep(1)
        self.page += 1
        self.buttons_valid = False
        _LOGGER.info('now on %s page', self.pages[self.page])

    def back(self):
        """Clicks the Back button.
           Raises Exception if the Back button is not enabled.
        """
        self._ensure(running = True)
        self._ensure_button('Back')
        self._ensure_button_enabled('Back')
        self.buttons.click('back')
        sleep(1)
        self.page -= 1
        self.buttons_valid = False
        _LOGGER.info('now on %s page', self.pages[self.page])

    def back_key(self):
        """Presses the Back button using the keyboard.
           Raises Exception if the Back button is not enabled.
        """
        self._ensure(running = True)
        self._ensure_button('Back')
        self._ensure_button_enabled('Back')
        self.setFocus()
        SCREEN.type('b', KEY_ALT)
        sleep(1)
        self.page -= 1
        self.buttons_valid = False
        _LOGGER.info('now on %s page', self.pages[self.page])

    def cancel(self):
        """Clicks the Cancel button and the Yes button.
           Raises Exception if the Cancel button is not enabled.
        """
        self._ensure(running = True)
        self._ensure_button('Cancel')
        self._ensure_button_enabled('Cancel')
        self.buttons.click('cancel')
        sleep(1)
        self.confirm_window_open = True
        self.confirm_cancel('yes')
        self.page = self.cancelled_page
        self.installing = False
        self.buttons_valid = False

    def cancel_key(self):
        """Presses the Cancel button and confirms using the keyboard.
           Raises Exception if the Cancel button is not enabled.
        """
        self._ensure(running = True)
        self._ensure_button('Cancel')
        self._ensure_button_enabled('Cancel')
        self.setFocus()
        SCREEN.type(Key.ESC)
        sleep(1)
        SCREEN.type('y')
        sleep(1)
        self.page = self.cancelled_page
        self.installing = False
        self.buttons_valid = False

    def finish(self):
        """Clicks the Finish button."""
        self._ensure(running = True)
        self._ensure_button('Finish')
        self._ensure_buttons_valid()
        _LOGGER.info('closing installer')
        self.buttons.click('finish')
        sleep(1)
        self.running = False

    def finish_key(self):
        """Presses the Finish button using the keyboard."""
        self._ensure(running = True)
        self._ensure_button('Finish')
        _LOGGER.info('closing installer')
        self.setFocus()
        SCREEN.type('f', KEY_ALT)
        sleep(1)
        self.running = False

    def install(self):
        """Clicks the install button.
           Raises Exception if the installer is not on the 'Ready to Install'
           page.
        """
        self._ensure(running = True)
        self._ensure_button('Install')
        self._ensure_buttons_valid()
        self.buttons.click('install')
        sleep(1)
        self.page = self.installing_page
        self.installing = True
        self.buttons_valid = False

    def install_key(self):
        """Presses the install button using the keyboard.
           Raises Exception if the installer is not on the 'Ready to Install'
           page.
        """
        self._ensure(running = True)
        self._ensure_button('Install')
        self.setFocus()
        SCREEN.type('i', KEY_ALT)
        sleep(1)
        self.page = self.installing_page
        self.installing = True
        self.buttons_valid = False

    def close(self):
        """Closes the installer by clicking the Close button in the window
           title bar and confirming if necessary.
        """
        AnchoredWindow.close(self)
        sleep(1)
        if not self.page in [self.complete_page, self.cancelled_page]:
            self.confirm_window_open = True
            self.confirm_cancel('yes')
            AnchoredWindow.close(self)
            sleep(1)
        self.running = False
        self.installing = False

    def confirm_cancel(self, button):
        """Clicks the specified button in the confirmation window.
           Raises Exception if the confirmation window is not open.
        """
        if not self.confirm_window_open:
            raise Exception('confirmation window is not open')
        self.confirm_buttons.find_buttons()
        self.confirm_buttons.click(button)
        sleep(1)
        self.confirm_window_open = False

    def _configure_shortcut(self, shortcut, add_shortcut):
        self._ensure(running = True)
        if self.page != self.shortcuts_page:
            raise Exception('installer is not on the Configure Shortcuts page')
        if self.shortcut_checkboxes is None:
            self.shortcut_checkboxes = VerticalCheckboxList(IMG_CHECKBOXES,
                    region = self)
            self.shortcut_checkboxes.find_elements()
            if self.shortcut_checkboxes.length() != 3:
                raise Exception('expected three checkboxes but found %d' %
                        self.shortcut_checkboxes.length())
        if bool(add_shortcut) != self.shortcut_checkboxes.is_checked(shortcut):
            if bool(add_shortcut):
                self.shortcut_checkboxes.check(shortcut)
            else:
                self.shortcut_checkboxes.uncheck(shortcut)
            sleep(1)

    def configure_desktop_shortcut(self, add_shortcut = True):
        """Checks the checkbox for the Desktop shortcut.
           If add_shortcut is False, unchecks the checkbox.
           Raises Exception if the installer is not on the Configure Shortcuts
           page.
        """
        self._configure_shortcut(0, add_shortcut)

    def configure_start_menu_shortcut(self, add_shortcut = True):
        """Checks the checkbox for the Start Menu shortcut.
           If add_shortcut is False, unchecks the checkbox.
           Raises Exception if the installer is not on the Configure Shortcuts
           page.
        """
        self._configure_shortcut(1, add_shortcut)

    def configure_quick_launch_shortcut(self, add_shortcut = True):
        """Checks the checkbox for the Quick Launch shortcut.
           If add_shortcut is False, unchecks the checkbox.
           Raises Exception if the installer is not on the Configure Shortcuts
           page.
        """
        self._configure_shortcut(2, add_shortcut)

    def is_finished(self):
        """Returns True if the installer has finished installing.
           More precisely, returns True if the Finish button exists in the
           installer window.
           Raises Exception if the installer was not installing.
        """
        self._ensure(running = True, installing = True)
        self.buttons.find_buttons()
        finished = self.buttons.exists_button('finish')
        if finished:
            self.installing = False
            self.buttons_valid = True
            self.page = self.complete_page
        return finished

    def wait_until_finished(self, timeout = INSTALL_TIME_MAX_SECONDS):
        """Waits until the installer finishes installing.
           Checks every 3 seconds if the Finish button exists.
           Raises Exception if the installer is not finished after the
           specified timeout.
        """
        self._ensure(running = True, installing = True)
        waiting = Wait(timeout, interval = 3,
                exception_message = 'installer not finished after %f seconds' %
                timeout)
        while not self.is_finished():
            waiting.wait()
        _LOGGER.info('finished')

    def is_running(self):
        """Returns True if the installer is running."""
        return self.running

    def is_installing(self):
        """Returns True if the installer is installing."""
        self._ensure(running = True)
        return self.installing

    def current_page(self):
        """Returns the current page number (0-based)."""
        self._ensure(running = True)
        return self.page

    def current_page_title(self):
        """Returns the current page title."""
        self._ensure(running = True)
        return self.pages[self.page]

    def defaultInstallation(self):
        """Runs the installer and installs the application, using default
           options.
        """
        self.run()
        self.next() # go to "Configure Shortcuts"
        self.next() # go to "Select Installation Folder"
        self.next() # go to "Ready to Install"
        self.install()
        self.wait_until_finished()
        self.finish()
