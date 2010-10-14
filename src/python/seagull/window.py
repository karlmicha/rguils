"""seagull/window.py
   A class to model a window with a title bar that can be minimized, maximized
   and closed.
   Author: Karl-Michael Schneider
   Date: 4/8/2010
"""

import logging
from sikuli.Sikuli import Location, SCREEN, closeApp
from sikuli.Region import Region
from seagull.util import AnchoredRegion
import seagull.windowflavor as windowflavor

_LOGGER = logging.getLogger(__name__)

class Window:
    """A window has a title bar that contains buttons to minimize, maximize and
       close the window in the upper right.
       A window can get focus by clicking on its title bar.
    """

    def __init__(self, region, title):
        """Creates a new window that covers the specified region. The region
           includes the title bar.
        """
        self.region = region
        self.title = title
        self.titlebar_region = Region(region.getX(), region.getY(),
                region.getW(), windowflavor.WINDOW_TITLEBAR_HEIGHT)
        self.minimize_button = self.getButtonLocation(
                windowflavor.WINDOW_TITLEBAR_MINIMIZE_BUTTON_OFFSET)
        self.maximize_button = self.getButtonLocation(
                windowflavor.WINDOW_TITLEBAR_MAXIMIZE_BUTTON_OFFSET)
        self.close_button = self.getButtonLocation(
                windowflavor.WINDOW_TITLEBAR_CLOSE_BUTTON_OFFSET)

    def getButtonLocation(self, button_offset):
        """Returns a Location instance at the specified horizontal offset in
           the title bar, vertically centered in the title bar.
        """
        if button_offset > 0:
            button_x = self.titlebar_region.getX() + button_offset
        else:
            button_x = self.titlebar_region.getX() \
                    + self.titlebar_region.getW() + button_offset
        return Location(button_x, self.titlebar_region.getY()
                + windowflavor.WINDOW_TITLEBAR_HEIGHT / 2)

    def setFocus(self):
        """Clicks on the center of this window's title bar."""
        _LOGGER.debug('setFocus: %s', self.title)
        SCREEN.click(self.titlebar_region)

    def minimize(self):
        """Clicks on the minimize button in this window's title bar."""
        _LOGGER.debug('minimize window: %s', self.title)
        SCREEN.click(self.minimize_button)

    def maximize(self):
        """Clicks on the maximize button in this window's title bar."""
        _LOGGER.debug('maximize window: %s', self.title)
        SCREEN.click(self.maximize_button)

    def close(self):
        """Clicks on the close button in this window's title bar."""
        _LOGGER.debug('close window: %s', self.title)
        SCREEN.click(self.close_button)

    def kill(self):
        """Attempts to kill the process that owns this window, using the window
           title.
        """
        _LOGGER.debug('kill window: %s', self.title)
        closeApp(self.title)

class AnchoredWindow(Window, AnchoredRegion):
    """An anchored window is a window whose region is an anchored region.
    """

    def __init__(self, anchorimage, offsetx = 0, offsety = 0, width = 0,
            height = 0, parentregion = SCREEN, name = 'anchored region',
            title = 'untitled'):
        """Creates a new instance.
           offsetx, offsety, width, height define the location and size of this
           region relative to the anchor image. See AnchoredRegion for details.
           name is the name of the region and is only used for debugging.
           title is the window title and is only used for debugging.
           The window is not initialized, it will be initialized when it is
           anchored.
        """
        AnchoredRegion.__init__(self, anchorimage, offsetx = offsetx,
                offsety = offsety, width = width, height = height,
                parentregion = parentregion, name = name)
        self.title = title

    def anchor(self, timeout = 0):
        """Searches the anchor image to determine the location of this window
           on the screen.
        """
        AnchoredRegion.anchor(self, timeout)
        # initialize this window to cover the anchored region
        Window.__init__(self, self, self.title)
