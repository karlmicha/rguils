"""seagull/dialoguewindow.py
   Classes to model hierarchies of dialogue windows.
   Author: Karl-Michael Schneider
   Date: 4/19/10
"""

import logging
from time import sleep
from sikuli.Sikuli import SCREEN
from sikuli.Key import Key
from seagull.util import clickAny
from seagull.window import Window

_LOGGER = logging.getLogger(__name__)

class DialogueWindow:
    """Base class to model dialogue windows.
       A dialogue window may have a parent window and any number of child
       windows.
       When a dialogue window is opened, it opens its parent window first.
       When a dialogue window is closed, it closes its child windows first.
       To open a dialogue window, call its open() method. When creating a
       dialogue window instance, you must provide a method that performs the
       necessary mouse click, key strokes, etc. to actually (physically) open
       the dialogue window on the screen.
       You can also provide a method to physically close the dialogue window.
       If no close method is define for a DialogueWindow instance and this
       instance is also an instance of Window, calling close() delegates to
       Window.close().
       The opening() and opened() methods are called on a dialogue window
       immediately before and after the window is opened.
       The closing() and closed() methods are called on a dialogue window
       immediately before and after the window is closed.
       The default implementations of these methods do nothing.
    """

    def __init__(self, name = None, parent_window = None,
                     open_method = None, close_method = None):
        """Creates a new instance.
           If parent_window is not None, it must be a DialogueWindow instance.
           open_method and close_method must be callables that override the
           _open() and _close() methods. Subclasses can override these methods
           directly and don't need to pass them in here.
           The parent_window is passed to _open() as the first argument.
           Any positional and keyword arguments that are passed to open() and
           close() are passed on to _open() and _close().
        """
        if parent_window is not None:
            if not isinstance(parent_window, DialogueWindow):
                raise TypeError('parent_window must be a DialogueWindow instance')
        self.name = name
        self.parent_window = parent_window
        self.child_windows = []
        if open_method is not None:
            self._open = open_method
        if close_method is not None:
            self._close = close_method
        if self.parent_window is not None:
            self.parent_window.add_child_window(self)
        self._is_open = False

    def add_child_window(self, window):
        """Add a child window to this dialogue window.
           The child window must be a DialogueWindow instance.
        """
        self.child_windows.append(window)

    def is_open(self):
        """Returns true if this dialogue window is open.
        """
        return self._is_open

    def open(self, *args, **kwds):
        """Opens this dialogue window. If this dialogue window is already open,
           calling open() does nothing. If this dialogue window has a parent
           window, opens the parent window first.
           The parent window is passed to _open() as the first argument.
           All optional arguments are passed to opening(), _open() and
           opened().
        """
        if self.is_open():
            return
        if self.parent_window is not None:
            self.parent_window.open()
        self.opening(*args, **kwds)
        if self.name is not None:
            _LOGGER.debug('open %s' % self.name)
        self._open(self.parent_window, *args, **kwds)
        self._is_open = True
        self.opened(*args, **kwds)

    def close(self, *args, **kwds):
        """Closes this dialogue window. If this dialogue window is not open,
           calling close() does nothing. If this dialogue window has child
           windows, closes them first.
           All optional arguments are passed to closing(), _close() and
           closed().
        """
        for window in self.child_windows:
            window.close()
        if not self.is_open():
            return
        self.closing(*args, **kwds)
        if self.name is not None:
            _LOGGER.debug('close %s' % self.name)
        self._close(*args, **kwds)
        self._is_open = False
        self.closed(*args, **kwds)

    def _open(self, parent_window, *args, **kwds):
        """The default method to open the actual dialogue window on the screen.
           The parent_window is passed to allow this method to use different
           opening mechanisms, depending from where it is opened.
           The optional and keyword arguments are passed from the open()
           method.
           When creating an instance you must pass a method to the constructor
           or override this method in a subclass.
        """
        raise Exception('no _open() method defined')

    def _close(self, *args, **kwds):
        """The default method to close the actual dialogue window on the
           screen.
           The optional and keyword arguments are passed from the close()
           method.
           If this instance is an instance of Window, it calls Window.close(),
           otherwise it throws an Exception.
           You can override this method by passing a method to the constructor
           or overriding it in a subclass.
        """
        if isinstance(self, Window):
            Window.close(self)
        else:
            raise Exception('no _close() method defined and this instance is not a Window instance')

    def opening(self, *args, **kwds):
        """This method is called immediately before the window represented by
           this instance is opened.
           The arguments are those from the open() method.
        """
        pass

    def opened(self, *args, **kwds):
        """This method is called immediately after the window represented by
           this instance was opened.
           The arguments are those from the open() method.
        """
        pass

    def closing(self, *args, **kwds):
        """This method is called immediately before the window represented by
           this instance is closed.
           The arguments are those from the close() method.
        """
        pass

    def closed(self, *args, **kwds):
        """This method is called immediately after the window represented by
           this instance was closed.
           The arguments are those from the close() method.
        """
        pass

class Confirm(DialogueWindow):
    """A simple confirmation dialogue.
       Its only elements are a number of buttons, e.g. OK, Cancel or Yes, No.
       Each button closes the dialogue.
       Buttons are specified as a dictionary object with a button id as the key
       and a button image or a list of button images as the value.
       To close the dialogue by clicking on one of the buttons, pass the button
       id to the close() method.
       Alternatively, buttons can be specified as a dictionary object with a
       button id as the key and a key sequence as the value. In this case the
       dialogue is closed by typing the key sequence with the given button id.
       It is also possible to specify a list of button ids to use only a subset
       of the buttons or keys.
       If no buttons and no key sequences are specified, the dialogue window
       has two buttons 'ok' (ENTER) and 'cancel' (ESC).
       If no button id is passed to close() and the dialogue window is an
       instance of Window, Window.close() is used to close the window.
    """

    def __init__(self, window_title, buttons = None, keys = None,
            button_ids = None, parent_window = None, open_method = None):
        DialogueWindow.__init__(self, window_title, parent_window, open_method)
        self.buttons = buttons
        self.keys = keys
        self.button_ids = button_ids
        if self.buttons is not None:
            ids = self.buttons.keys()
        else:
            if self.keys is None:
                self.keys = { 'ok' : Key.ENTER, 'cancel' : Key.ESC }
            ids = self.keys.keys()
        if self.button_ids is None:
            self.button_ids = ids
        else:
            for bid in self.button_ids:
                if bid not in ids:
                    raise Exception("undefined button id '%s' in dialogue window '%s'" % (bid, self.name))

    def _close(self, button_id = None):
        """Closes the actual confirmation dialogue represented by this
           instance.
        """
        if button_id is None:
            DialogueWindow._close(self, button_id)
            return
        if button_id not in self.button_ids:
            raise Exception("confirm dialogue '%s' does not contain a button with id %s" %
                    (self.name, button_id))
        if self.keys is not None:
            SCREEN.type(self.keys[button_id])
            sleep(1)
        else:
            button = self.buttons[button_id]
            if isinstance(button, list):
                clickAny(button)
            else:
                SCREEN.click(button)
            sleep(1)
