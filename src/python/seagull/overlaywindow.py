"""seagull/overlaywindow.py
   Classes to create overlay windows on the screen to display regions.
   Author: Karl-Michael Schneider
   Date: 6/10/2010
"""

from time import sleep
from javax.swing import JWindow
from java.awt import Color
from java.awt.image import RescaleOp
from java.awt.event import MouseListener
from sikuli.Sikuli import getScreen

class OverlayWindow(JWindow, MouseListener):
    """Class to show a region on the screen.
       This is an abstract class. Subclasses must define the methods
       prepareShowRegion() and paint(graphics).
    """

    def __init__(self, screen = None):
        """Creates a new overlay window on the specified screen, or on the
           current screen if screen is None.
        """
        if screen is not None:
            self.screen = screen
        else:
            self.screen = getScreen()
        self.region = None
        self.setVisible(False)
        self.setAlwaysOnTop(True)
        self.addMouseListener(self)

    def showRegion(self, region, duration = None):
        """Shows the specified region on the screen for the specified duration
           in seconds. If duration is not specified or is None, does not remove
           the overlay after it is displayed.
        """
        self.region = region
        self.prepareShowRegion()
        self.setVisible(True)
        self.toFront()
        if duration is not None:
            sleep(duration)
            self.close()

    def close(self):
        """Removes this overlay window from the screen.
        """
        self.dispose()

    def prepareShowRegion(self):
        """Makes the necessary preparations for drawing the overlay window,
           such as setting its position and dimensions, capturing the screen,
           color-scaling of images, etc.
        """
        raise Exception('a subclass must override this method')

    def mousePressed(self, event):
        """specified in java.awt.event.MouseListener"""
        pass

    def mouseReleased(self, event):
        """specified in java.awt.event.MouseListener"""
        pass

    def mouseEntered(self, event):
        """specified in java.awt.event.MouseListener"""
        pass

    def mouseExited(self, event):
        """specified in java.awt.event.MouseListener"""
        pass

    def mouseClicked(self, event):
        """specified in java.awt.event.MouseListener"""
        self.close()

class OutlineOverlayWindow(OverlayWindow):
    """An overlay window that shows a region by drawing its outline as a red
       rectangle, and also draws a horizontal and vertical line through its
       center.
    """

    def __init__(self, screen = None):
        OverlayWindow.__init__(self, screen)
        self.__region_image = None

    def prepareShowRegion(self):
        """Specified in OverlayWindow."""
        x = self.region.getX()
        y = self.region.getY()
        w = self.region.getW()
        h = self.region.getH()
        self.__region_image = self.screen.capture(x, y, w, h).getImage()
        self.setLocation(x, y)
        self.setSize(w, h)

    # @Override
    def paint(self, graphics):
        """Paints the window.
           Specified in java.awt.Container.
        """
        graphics.drawImage(self.__region_image, 0, 0, self)
        w, h = self.region.getW(), self.region.getH()
        if w < 1 or h < 1:
            return
        graphics.setColor(Color.red)
        graphics.drawRect(0, 0, w - 1, h - 1)
        graphics.drawLine(int(w/2), 0, int(w/2), h - 1)
        graphics.drawLine(0, int(h/2), w - 1, int(h/2))

class DimOverlayWindow(OverlayWindow):
    """An overlay window that shows a region by dimming the screen around the
       region and drawing a cross in its center.
    """

    def __init__(self, screen = None):
        OverlayWindow.__init__(self, screen)
        self.__screen_image = None
        self.__darker_screen_image = None

    def prepareShowRegion(self):
        """Specified in OverlayWindow."""
        self.__screen_image = self.screen.capture().getImage()
        scale_factor = 0.6
        op = RescaleOp(scale_factor, 0, None)
        self.__darker_screen_image = op.filter(self.__screen_image, None)
        self.setLocation(self.screen.getX(), self.screen.getY())
        self.setSize(self.screen.getW(), self.screen.getH())

    # @Override
    def paint(self, graphics):
        """Paints the window.
           Specified in java.awt.Container.
        """
        graphics.drawImage(self.__darker_screen_image, 0, 0, self)
        x = self.region.getX()
        y = self.region.getY()
        w = self.region.getW()
        h = self.region.getH()
        if w < 1 or h < 1:
            return
        graphics.setClip(x, y, w, h)
        graphics.drawImage(self.__screen_image, 0, 0, self)
        crossdim = min(40, w, h)
        crossx = x + int((w - crossdim) / 2)
        crossy = y + int((h - crossdim) / 2)
        graphics.setColor(Color.red)
        graphics.drawLine(x + int(w/2), crossy,
                x + int(w/2), crossy + crossdim - 1)
        graphics.drawLine(crossx, y + int(h/2),
                crossx + crossdim - 1, y + int(h/2))
