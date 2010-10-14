"""seagull/util.py
   Utility functions and classes for Seagull (a cleaner Sikuli API).
   Author: Karl-Michael Schneider
   Date: 4/8/2010
"""

import logging
from time import sleep
from sikuli.Sikuli import SCREEN, FindFailed
from sikuli.Region import Region
from seagull.overlaywindow import OutlineOverlayWindow

logging.basicConfig()
_LOGGER = logging.getLogger(__name__)
_debug_region = None
_show_regions = False
_overlaywindow = None

# click(arg, [modifiers]) requires modifiers if it is called on an instance of
# edu.mit.csail.uid.Region. To make code more readable, use NO_MODIFIER.
NO_MODIFIER = 0

def setTimeout(region, timeout):
    """Sets the auto wait timeout (in seconds) in the specified region and
       returns the previous value.
    """
    oldtimeout = region.getAutoWaitTimeout()
    region.setAutoWaitTimeout(timeout)
    return oldtimeout

def setException(region, flag):
    """Sets whether an exception is thrown when find fails in the specified
       region, returns the previous value.
    """
    oldflag = region.getThrowException()
    region.setThrowException(flag)
    return oldflag

def setDebug(flag):
    """If flag is True, turns debug mode on.
       If flag is False, turns debug mode off.
       In debug mode, the log level is set to DEBUG instead of INFO.
    """
    if flag:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info('debug turned on')
    else:
        logging.getLogger().setLevel(logging.INFO)

def getDebug():
    """Returns True if debug messages are logged.
    """
    return logging.getLogger().isEnabledFor(logging.DEBUG)

def setDebugRegion(region):
    """Sets the region for future debugging.
       If region is not None, results are only printed if find was invoked on
       the specified region.
    """
    global _debug_region
    _debug_region = region

def getDebugRegion():
    """Returns the current debug region.
    """
    return _debug_region

def setShowRegions(flag):
    """If flag is True, shows the outline and center of matches and other
       regions found by methods in this module. If flag is False, matches are
       not shown.
    """
    global _show_regions
    _show_regions = flag

def getShowRegions():
    """Returns True if regions are shown, else False.
    """
    return _show_regions

def showRegion(region, duration = 2):
    """Shows the outline and center of the specified region on the current
       screen for the specified duration.
    """
    global _overlaywindow
    if _overlaywindow is None:
        _overlaywindow = OutlineOverlayWindow()
    _overlaywindow.showRegion(region, duration)

def _debug(methodname, iarg, arg, region, match):
    if _debug_region is not None and region != _debug_region:
        return
    _LOGGER.debug('%s: find(%d=%s, region=%s) = %s',
            methodname, iarg, str(arg), str(region), str(match))

class TimeoutExceeded(Exception):
    """Raised by the Wait class when the timeout is exceeded while waiting."""

    def __init__(self, message):
        Exception.__init__(self, message)

class Wait:
    """Simple class to sleep in intervals until a timeout is reached. A
       TimeoutExceeded exception is raised when the timeout is reached.
    """

    def __init__(self, timeout, interval = 1,
            exception_message = 'maximum waiting time exceeded'):
        """Creates a new instance with the specified timeout, interval and
           exception message. If the timeout is None, waits forever.
        """
        # catch bugs where exception message is passed without parameter name
        if not (isinstance(interval, int) or isinstance(interval, float)):
            raise Exception('interval must be a number')
        self.timeout = timeout
        self.interval = interval
        self.exception_message = exception_message
        self.waited = 0

    def wait(self):
        """Sleeps for the number of seconds specified in this instance's
           interval, but no longer than until the timeout is reached.
           Raises TimeoutExceeded if the timeout has been reached before
           sleeping.
        """
        if self.timeout is not None:
            if self.waited >= self.timeout:
                raise TimeoutExceeded(self.exception_message)
            sec = min(self.interval, self.timeout - self.waited)
        else:
            sec = self.interval
        sleep(sec)
        self.waited += sec

    def setExceptionMessage(self, message):
        """Sets the exception message. Can be used to change the exception
           message while waiting.
        """
        self.exception_message = message

def find(arg, region = SCREEN, timeout = None, exception = None):
    """Behaves like region.find(arg) except that if timeout and exception are
       not None, the auto wait time and exception of the region are set to the
       specified values before the find method is called, and restored when the
       find method returns.
    """
    if timeout is not None:
        t = setTimeout(region, timeout)
    if exception is not None:
        e = setException(region, exception)
    try:
        match = region.find(arg)
    finally:
        if timeout is not None:
            setTimeout(region, t)
        if exception is not None:
            setException(region, e)
    return match

def click(arg, modifiers = NO_MODIFIER, region = SCREEN,
        timeout = None, exception = None):
    """Behaves like region.click(arg) except that if timeout and exception are
       not None, the auto wait time and exception of the region are set to the
       specified values before the click method is called, and restored when
       the click method returns.
    """
    if timeout is not None:
        t = setTimeout(region, timeout)
    if exception is not None:
        e = setException(region, exception)
    try:
        value = region.click(arg, modifiers)
    finally:
        if timeout is not None:
            setTimeout(region, t)
        if exception is not None:
            setException(region, e)
    return value

def findAny(args, region = SCREEN, timeout = None, exception = None):
    """Searches the specified region for the elements in args until it finds
       one.
       If none of the elements exists in the region, waits for one second and
       then searches again.
       If an element is found, returns its index in args (0-based) and the
       match.
       Elements are searched in the order they appear in args.
       If no element is found within the specified time (in seconds), returns
       None if exception is False, and raises FindFailed if exception is True.
       If no region is specified, searches the entire screen.
       If the optional timeout is not specified or is None, uses the current
       timeout of the region.
       If the exception argument is not specified or is None, uses the current
       exception setting of the region.
    """
    if not isinstance(args, list):
        raise ValueError('list argument expected')
    if timeout is None:
        timeout = region.getAutoWaitTimeout()
    if exception is None:
        exception = region.getThrowException()
    argi = None
    match = None
    waiting = Wait(timeout)
    while True:
        for i, arg in enumerate(args):
            match = find(arg, region = region, timeout = 0, exception = False)
            _debug('findAny', i, arg, region, match)
            if match is not None:
                if _show_regions:
                    showRegion(match)
                argi = i
                break
        if match is not None:
            break
        try:
            waiting.wait()
        except TimeoutExceeded:
            break
    if match is not None:
        return argi, match
    elif exception:
        raise FindFailed('none of the elements was found after %f seconds' %
                timeout)
    else:
        return None

def clickAny(args, region = SCREEN, timeout = None, exception = None):
    """Searches the specified region for the elements in args until it finds
       one.
       Clicks on the first element that is found.
       Returns the value returned by the click method.
       If no element is found within the specified time, returns 0 if exception
       is False, and raises FindFailed if exception is True.
       If no region is specified, searches the entire screen.
       If the optional timeout is not specified or is None, uses the current
       timeout of the region.
       If the exception argument is not specified or is None, uses the current
       exception setting of the region.
    """
    results = findAny(args, region = region, timeout = timeout,
            exception = exception)
    if results is None:
        return 0
    click(results[1], region = region)
    return 1

def existsAny(args, region = SCREEN, timeout = None):
    """Returns the index of the first element in args that is found in the
       specified region within the specified timeout (in seconds), or None if
       none is found.
       If no region is specified, searches the entire screen.
       If the optional timeout is not specified or is None, uses the current
       timeout of the region.
       The index is 0-based.
    """
    try:
        results = findAny(args, region = region, timeout = timeout)
        if results is None:
            return None
        return results[0]
    except FindFailed:
        return None

def waitAny(args, region = SCREEN, timeout = None):
    """Waits until any of the args is found in the specified region.
       Raises FindFailed if none of the args is found within the specified
       timeout (in seconds).
       If no region is specified, searches the entire screen.
       If the optional timeout is not specified or is None, uses the current
       timeout of the region.
    """
    e = setException(region, True)
    try:
        findAny(args, region = region, timeout = timeout)
    finally:
        setException(region, e)

def waitWhileFound(arg, region = SCREEN, timeout = None, interval = 1):
    """Waits while the specified argument is found in the region.
       A search is performed every interval seconds (default is 1 second).
       Raises Exception if the argument is still found after the timeout.
       If no region is specified, searches the entire screen.
       If the optional timeout is not specified or is None, uses the current
       timeout of the region.
    """
    if timeout is None:
        timeout = region.getAutoWaitTimeout()
    waiting = Wait(timeout, interval = interval,
            exception_message = 'argument still found after %f seconds' %
            timeout)
    while find(arg, region = region, timeout = 0,
            exception = False) is not None:
        waiting.wait()

def getAllMatches(args, region = SCREEN, timeout = None):
    """Searches the specified region for all elements in args and returns a
       list of the matches.
       Images that do not exist in the region are searched again repeatedly
       with one second between each round, until the timeout is reached.
       If an image is not found within the specified time, None is returned for
       that image.
       If no region is specified, searches the entire screen.
       If timeout is not specified, uses the current timeout of the region.
    """
    if not isinstance(args, list):
        raise ValueError('list argument expected')
    if timeout is None:
        timeout = region.getAutoWaitTimeout()
    matches = [None] * len(args)
    notfound = [(i, arg) for i, arg in enumerate(args)]
    waiting = Wait(timeout)
    while len(notfound) > 0:
        j = 0 # index in notfound
        while j < len(notfound):
            i, arg = notfound[j]
            match = find(arg, region = region, timeout = 0, exception = False)
            _debug('getAllMatches', i, arg, region, match)
            if match is not None:
                if _show_regions:
                    showRegion(match)
                matches[i] = match
                del notfound[j]
            else:
                j += 1
        if len(notfound) > 0:
            try:
                waiting.wait()
            except TimeoutExceeded:
                break
    return matches

def getAllScores(args, **kwds):
    """Searches the specified region for all elements in args and returns a
       list of the match scores.
       If an image is not found within the specified time, the score is set to
       0.
    """
    scores = []
    for match in getAllMatches(args, **kwds):
        if match is not None:
            scores.append(match.getScore())
        else:
            scores.append(0)
    return scores

def clickOffset(image, offsetx = 0, offsety = 0, region = SCREEN,
        timeout = None, exception = None):
    """Clicks with an offset relative to an image or a Match object.
       Returns 1 if the click was performed, else 0.
       Raises FindFailed if the image was not found within the specified time
       and exception is True.
       If region is not specified, searches the entire screen.
       If timeout is not specified or is None, uses the current timeout of the
       region.
       If exception is not specified or is None, uses the current exception
       setting of the region.
    """
    if hasattr(image, 'getX'):
        target = image
    else:
        target = find(image, region = region, timeout = timeout,
                exception = exception)
        if target is None:
            return 0
    newtarget = Region(target.getX() + offsetx, target.getY() + offsety,
            target.getW(), target.getH())
    if _show_regions:
        showRegion(newtarget)
    return region.click(newtarget, NO_MODIFIER)

def typeKeys(keys, modifiers = NO_MODIFIER, repeat = 1, region = None):
    """Types a sequence of keys.
       If repeat is greater than 1, types the same sequence repeatedly.
       If region is not None, clicks on the region first.
    """
    if repeat < 1:
        return
    # click on the region only once
    SCREEN.type(region, keys, modifiers)
    for i in range(repeat - 1):
        SCREEN.type(keys, modifiers)

def extendRegion(region, top = 0, right = 0, bottom = 0, left = 0):
    """Extends the given region in all four directions by the specified values.
    """
    region.setRect(region.getX() - left, region.getY() - top,
                        region.getW() + left + right,
                        region.getH() + top + bottom)

def getUniqueRegions(regions):
    """Returns the specified regions but removes duplicates.
       Does not change the order of the regions.
       A region is a duplicate of another one if they have the same coordinates
       and size.
       The argument can be a list or an iterable.
    """
    rect = set()
    unique_regions = []
    for region in regions:
        r = (region.getX(), region.getY(), region.getW(), region.getH())
        if r in rect:
            continue
        unique_regions.append(region)
        rect.add(r)
    return unique_regions

def _first(a, b):
    """Returns a if a is not 0, else b.
    """
    if a != 0:
        return a
    else:
        return b

"""Constants to specify how regions are sorted.
   Any subset of these constants specifies a sort order.
   The bitwise OR of the elements in such a subset is the index in the list
   of region comparison functions.
"""
REGION_SORT_HORIZONTAL = 4
REGION_SORT_HDESC = 2
REGION_SORT_VDESC = 1

"""A list of comparison functions for regions (suitable for sort).
   Assume that A, B, C, D are regions with relative position as follows:

      A   B

      C   D

   Given a sort order specification, the sort order is as follows:

      HORIZONTAL   HDESC     VDESC     sort order
      False        False     False     A, B, C, D
      False        False     True      C, D, A, B
      False        True      False     B, A, D, C
      False        True      True      D, C, B, A
      True         False     False     A, C, B, D
      True         False     True      C, A, D, B
      True         True      False     B, D, A, C
      True         True      True      D, B, C, A
"""
REGION_COMPARATORS = [
    lambda a,b: _first(cmp(a.getY(), b.getY()), cmp(a.getX(), b.getX())),
    lambda a,b: _first(-cmp(a.getY(), b.getY()), cmp(a.getX(), b.getX())),
    lambda a,b: _first(cmp(a.getY(), b.getY()), -cmp(a.getX(), b.getX())),
    lambda a,b: _first(-cmp(a.getY(), b.getY()), -cmp(a.getX(), b.getX())),
    lambda a,b: _first(cmp(a.getX(), b.getX()), cmp(a.getY(), b.getY())),
    lambda a,b: _first(cmp(a.getX(), b.getX()), -cmp(a.getY(), b.getY())),
    lambda a,b: _first(-cmp(a.getX(), b.getX()), cmp(a.getY(), b.getY())),
    lambda a,b: _first(-cmp(a.getX(), b.getX()), -cmp(a.getY(), b.getY()))
]

def sortRegions(matches, sortorder = 0):
    """Sorts the specified regions in place by their x and y coordinates.
       The argument must be a list.
       The default sort order is rows from top to bottom, and within rows from
       left to right.
    """
    matches.sort(REGION_COMPARATORS[sortorder])

def getOverlap(region1, region2):
    """Returns the overlap of two regions as a fraction of the first region.
    """
    overlap_w = min(region1.getX() + region1.getW(),
            region2.getX() + region2.getW()) \
                    - max(region1.getX(), region2.getX())
    if overlap_w <= 0:
        return 0
    overlap_h = min(region1.getY() + region1.getH(),
            region2.getY() + region2.getH()) \
                    - max(region1.getY(), region2.getY())
    if overlap_h <= 0:
        return 0
    return float(overlap_w * overlap_h) / (region1.getW() * region1.getH())

def sameRegion(region1, region2, minOverlap = 0.9):
    """Returns True if the two regions are almost the same.
       More precisely, returns True if the overlap of the two regions is no
       less than the specified fraction of each region.
       The default minimum fraction is 0.9.
    """
    return getOverlap(region1, region2) >= minOverlap and \
            getOverlap(region2, region1) >= minOverlap

def bestMatch(images, region = SCREEN, minOverlap = 0.9):
    """Finds each image in the specified region and returns the index of the
       image with the highest match score, and the match.
       All matches must have approximately the same region.
       If exceptions are enabled and none of the images are found, throws
       FindFailed.
       If exceptions are not enabled and none of the images are found, returns
       None.
       If the list of images is empty, returns None.
       Raises Exception if not all matches have the same region.
       If region is not specified, searches in the entire screen.
    """
    if len(images) == 0:
        return None
    matches = getAllMatches(images, **{ 'region' : region, 'timeout' : 0 })
    if matches[0] is not None:
        best_match = 0
        best_score = matches[0].getScore()
    else:
        best_match = None
        best_score = 0
    for m in range(1, len(matches)):
        match = matches[m]
        if match is None:
            continue
        score = match.getScore()
        if best_match is None:
            best_match = m
            best_score = score
        else:
            if not sameRegion(matches[best_match], match, minOverlap):
                raise Exception('images %d, %d found in different regions' %
                        (best_match, m))
            if score > best_score:
                best_match = m
                best_score = score
    if best_match is None:
        if region.getThrowException():
            raise FindFailed('none of the images was found')
        else:
            return None
    return best_match, matches[best_match]

def bestMatches(images, region = SCREEN, minOverlap = 0.9):
    """Finds each image in the specified region and returns a list of tuples
       (i, match) where i is an index in images, match is the match of
       images[i], any match of a different image with the same region as a
       match in the returned list has a lower score, and all matches in the
       returned list have different regions. In other words, if multiple images
       are found and their matches have the same region, only the best match is
       returned. If two images are found in different regions, they are treated
       separately. For each image only the best match is used.
       If exceptions are enabled and none of the images are found, throws
       FindFailed.
       If exceptions are not enabled and none of the images are found, returns
       None.
       If the list of images is empty, returns None.
       If region is not specified, searches in the entire screen.
    """
    if len(images) == 0:
        return None
    matches = getAllMatches(images, **{ 'region' : region, 'timeout' : 0 })
    best_match_regions = []
    for i_match, match in enumerate(matches):
        if match is None:
            continue
        # find match with same region in best_match_regions
        # if this match has a higher score, replace the match in
        # best_match_regions
        # if no match with the same region is found, add this match
        i_best = None
        for i, bm in enumerate(best_match_regions):
            if sameRegion(bm[1], match, minOverlap):
                i_best = i
                break
        if i_best is not None:
            if match.getScore() > best_match_regions[i_best][1].getScore():
                best_match_regions[i_best] = (i_match, match)
        else:
            best_match_regions.append((i_match, match))
    if len(best_match_regions) == 0:
        if region.getThrowException():
            raise FindFailed('none of the images was found')
        else:
            return None
    return best_match_regions

class AnchoredRegion(Region):
    """An anchored region is a region of a specified size that is anchored to
       an image. The image has a fixed position relative to the region's
       top-left corner. An anchored region is identified by finding the
       anchoring image on the screen and then calculating the region's position
       relative to the position of the image.
       An anchored region can have a parent region, in which case the anchor
       image is only searched for in the parent region.
       An anchored region has a find count. Everytime an anchored region is
       identified, its find count is incremented. When a region with a parent
       region that is also an anchored region is identified and the parent
       region has a lower find count than the region's find count, the parent
       region is identified first. This way a region is correctly identified if
       its parent region has moved since the last time it was identified.
    """

    def __init__(self, anchorimage, offsetx = 0, offsety = 0, width = 0,
            height = 0, parentregion = SCREEN, name = 'anchored region'):
        """Creates a new anchored region that will be identified by the
           specified image. The anchor() method must be called to actually
           identify the region and calculate its position. The image's top-left
           corner will be positioned offsetx pixels from the left edge and
           offsety pixels from the top edge of the region. Width and height are
           the region's dimensions.
           If the parent region is specified, the anchor image will only be
           searched in that region, otherwise in the entire screen. Note that
           for finding the anchor image, the parent region's position and
           dimension at the time the anchor() method is called are relevant,
           not those at the time this instance is created.
           If width and height are 0, offsetx and offsety must also be 0, and
           the region is set to the match region of the anchor image.
           If name is provided, it is printed in debug statements.
        """
        if width == 0 or height == 0:
            if offsetx != 0 or offsety != 0 or width != 0 or height != 0:
                raise Exception('if width or height are 0, all offsets and dimensions must be 0')
        Region.__init__(self, 0, 0, width, height)
        self.anchorimage = anchorimage
        self.offsetx = offsetx
        self.offsety = offsety
        if parentregion is not None:
            self.parentregion = parentregion
        else:
            self.parentregion = SCREEN
        self.name = name
        self.anchormatch = None
        self.findcount = 0

    def anchor(self, timeout = 0):
        """Identifies this region by searching for its anchor image and
           calculates its position.
           If the parent region of this anchored region is also an anchored
           region that has not been identified, or has a lower find count, the
           parent region is identified first.
           Raises FindFailed if the anchor image is not found within the
           specified time.
        """
        self.findcount += 1
        if isinstance(self.parentregion, AnchoredRegion):
            if self.parentregion.findcount < self.findcount:
                self.parentregion.anchor(timeout)
        self.anchormatch = find(self.anchorimage, region = self.parentregion,
                timeout = timeout, exception = True)
        _LOGGER.debug('%s anchor=%s count=%d',
                self.name, str(self.anchormatch), self.findcount)
        if _show_regions:
            showRegion(self.anchormatch)
        self.setX(self.anchormatch.getX() - self.offsetx)
        self.setY(self.anchormatch.getY() - self.offsety)
        if self.getW() == 0 or self.getH() == 0:
            self.setW(self.anchormatch.getW())
            self.setH(self.anchormatch.getH())
        if _show_regions:
            showRegion(self)

    def is_displayed(self):
        """Returns True if the anchor image is displayed in the parent region
           of this region (which may be the entire screen).
        """
        return self.parentregion.exists(self.anchorimage, 0) is not None

    def wait_until_displayed(self, timeout, is_displayed = True):
        """Waits no longer than the specified timeout (in seconds) until the
           anchor image is displayed in the parent region of this region.
           Raises Exception if the anchor image is not displayed within the
           timeout.
           If the optional argument is_displayed is False, waits until the
           anchor image is no longer displayed, and raises Exception if the
           anchor image is still displayed after the specified time.
        """
        if is_displayed:
            e = setException(self.parentregion, True)
            try:
                self.parentregion.wait(self.anchorimage, timeout)
            except FindFailed:
                raise Exception("anchor image of region '%s' not found after %f seconds" % (self.name, timeout))
            finally:
                setException(self.parentregion, e)
        else:
            if not self.parentregion.waitVanish(self.anchorimage, timeout):
                raise Exception("anchor image of region '%s' still displayed after %f seconds" % (self.name, timeout))
