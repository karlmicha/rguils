"""seagull/checkboxes.py
   A class to model rows and/or columns of checkboxes, radio buttons and
   similar elements.
   Author: Karl-Michael Schneider
   Date: 5/25/10
"""

import operator, logging
from sikuli.Sikuli import SCREEN, FindFailed
from sikuli.Region import Region
from seagull.util import bestMatch, click, extendRegion, getUniqueRegions, \
        REGION_SORT_HORIZONTAL, sameRegion, setTimeout, sortRegions, Wait

_LOGGER = logging.getLogger(__name__)

class Checkable:
    """Models a row or column of identical elements that can be checked or
       unchecked, such as checkboxes and radio buttons. A checkbox or radio
       button list is defined by providing one or more images of checked
       elements and one or more images of unchecked elements. The class locates
       all occurrences of the element in the specified region and determines
       its status (checked or unchecked).
    """

    def __init__(self, images, region = SCREEN, orientation = 0,
            radio = False, auto_verify = False, timeout = 3):
        """Creates a new list of checkboxes or radio buttons.
           Images must be a dictionary with two keys, 'checked' and
           'unchecked'. The value for 'checked' must be a list of images of
           checked elements. The value for 'unchecked' must be a list of images
           of unchecked elements.
           Images are searched for in region. If region is None, the
           entire screen is used.
           Orientation is a sort order for regions.
           If radio is True, at most one element can be checked.
           If auto_verify is True, any method that clicks on an element will
           wait until the element's actual state on the screen has changed as
           expected. For example, if a method clicks on an element to check it,
           it will wait until the element is actually checked. If the element
           is still not changed after the timeout, the method will raise an
           Exception.
           Images are not actually searched when the list is created.
           You must call find_elements() to search the elements in the region.
        """
        self.images = images
        self.region = region
        self.orientation = orientation
        self.radio = radio
        self.auto_verify = auto_verify
        self.timeout = timeout
        if self.radio:
            self.element_type = 'radio button'
            self.element_types = 'radio buttons'
        else:
            self.element_type = 'checkbox'
            self.element_types = 'checkboxes'
        self.element_regions = None
        self.checked_scores = None
        self.unchecked_scores = None

    def find_elements(self, timeout = 0):
        """Finds the elements of this list in the region.
           Each image is searched for no more than timeout seconds.
           If timeout is None, the default wait time of the region is used.
           Raises FindFailed if no elements can be found.
        """
        # Creates three lists:
        # element_regions[i] is the region of a match of an image in the
        # region.
        # checked_scores[i] is the highest score of a match for an image of a
        # checked element.
        # unchecked_scores[i] is the highest score of a match for an image of
        # an unchecked element.
        # element_regions[i] is ordered according to orientation.
        #
        # The approach is as follows:
        # 1. for each image, find all matches.
        # 2. for each match, find an existing element region that is similar
        # to the region of the match. If no similar region exists, create a new
        # element region.
        # 3. update the score for the element region with the match score.
        # scores are indexed by region coordinates.
        # 4. when all matches have been found, sort the element regions.
        # 5. create new lists of scores where scores are indexed by region
        # number.
        self.element_regions = []
        checked_region_scores = {}
        unchecked_region_scores = {}
        if timeout is not None:
            t = setTimeout(self.region, timeout)
        for state in ['checked', 'unchecked']:
            for image in self.images[state]:
                try:
                    matches = self.region.findAll(image)
                    if matches is not None:
                        for match in getUniqueRegions(matches):
                            self._add_match(match, state, self.element_regions,
                                    checked_region_scores,
                                    unchecked_region_scores)
                except FindFailed:
                    pass
        if timeout is not None:
            setTimeout(self.region, t)
        if len(self.element_regions) == 0:
            raise FindFailed('no %s were found' % self.element_types)
        sortRegions(self.element_regions, self.orientation)
        self.checked_scores = [checked_region_scores[self._region_id(region)]
                for region in self.element_regions]
        self.unchecked_scores = [
                unchecked_region_scores[self._region_id(region)]
                for region in self.element_regions]
        _LOGGER.info('found %d %s, %s checked', self.length(),
                self.element_types, str(self.checked_elements()))
        if self.radio:
            if len(self.checked_elements()) > 1:
                raise Exception('found %d checked elements, violates radio=True parameter')

    def _add_match(self, match, state, regions, checked_region_scores,
            unchecked_region_scores):
        """Find the region in regions that is similar to the match. Update the
           score for that region. If there is no similar region, create a new
           region from the match.
        """
        match_region = None
        for region in regions:
            if sameRegion(region, match, 0.5):
                match_region = region
                break
        if match_region is None:
            match_region = Region(match)
            regions.append(match_region)
        region_id = self._region_id(match_region)
        if region_id not in checked_region_scores:
            checked_region_scores[region_id] = 0
        if region_id not in unchecked_region_scores:
            unchecked_region_scores[region_id] = 0
        if state == 'checked':
            if match.getScore() > checked_region_scores[region_id]:
                checked_region_scores[region_id] = match.getScore()
        else:
            if match.getScore() > unchecked_region_scores[region_id]:
                unchecked_region_scores[region_id] = match.getScore()

    def _region_id(self, region):
        """Returns the region's position as a string, to be used as a
           dictionary key.
        """
        return '%d,%d' % (region.getX(), region.getY())

    def length(self):
        """Returns the number of elements.
        """
        return len(self.element_regions)

    def regions(self):
        """Returns the regions of the elements as a list.
        """
        return self.element_regions

    def checked(self):
        """Returns a list of booleans indicating whether each element is
           checked or not.
        """
        return map(lambda s:operator.gt(s[0], s[1]),
                zip(self.checked_scores, self.unchecked_scores))

    def is_checked(self, element_index):
        """Returns True if the specified element is checked, else False.
           Element indexes are 0-based.
        """
        return self.checked_scores[element_index] > \
                self.unchecked_scores[element_index]

    def checked_elements(self):
        """Returns the indexes of all checked elements as a list.
           If no elements are checked, the list is empty.
        """
        return [index for index, checked in enumerate(self.checked())
                if checked]

    def checked_element(self):
        """Returns the index of the checked element, or None if no element is
           checked.
           Raise Exception if this list was not created with radio=True.
        """
        if not self.radio:
            raise Exception('method checked_element can only be called on radio lists')
        checked = self.checked_elements()
        if len(checked) > 0:
            return checked[0]
        else:
            return None

    def _toggle_state(self, element_index):
        self.checked_scores[element_index], \
                self.unchecked_scores[element_index] \
        = self.unchecked_scores[element_index], \
                self.checked_scores[element_index]
        if self.is_checked(element_index):
            _LOGGER.info('%s %d changed from unchecked to checked',
                    self.element_type, element_index)
        else:
            _LOGGER.info('%s %d changed from checked to unchecked',
                    self.element_type, element_index)

    def check(self, element_index, modifiers = 0):
        """Checks the specified element.
           If the element is already checked, does nothing.
           Returns True if the element was not previously checked, else false.
           Element indexes are 0-based.
        """
        if self.is_checked(element_index):
            return False
        if self.radio:
            old_index = self.checked_element()
        click(self.element_regions[element_index], modifiers = modifiers,
                region = self.region)
        if self.auto_verify:
            # updates the state
            self.wait(element_index, True)
        else:
            self._toggle_state(element_index)
        if self.radio:
            if old_index is not None:
                # old_index != element_index because element_index was not
                # checked
                self._toggle_state(old_index)
        return True

    def check_all(self, element_indexes = None, modifiers = 0):
        """Checks the specified elements.
           If the optional argument is omitted, checks all elements.
           Returns the number of elements that have changed from unchecked to
           checked.
           If this list was created with radio=True, raises Exception.
           Element indexes are 0-based.
        """
        if self.radio:
            raise Exception('cannot check multiple radio buttons')
        if element_indexes is None:
            element_indexes = range(self.length())
        changed = 0
        for index in element_indexes:
            if self.check(index, modifiers = modifiers):
                changed += 1
        return changed

    def uncheck(self, element_index, modifiers = 0):
        """Unchecks the specified element.
           If the element is not currently checked, does nothing.
           Returns True if the element was previously checked, else False.
           If this list was created with radio=True, raises Exception.
           Element indexes are 0-based.
        """
        if self.radio:
            raise Exception('cannot uncheck a radio button')
        if not self.is_checked(element_index):
            return False
        self.toggle(element_index, modifiers = modifiers)
        return True

    def uncheck_all(self, element_indexes = None, modifiers = 0):
        """Unchecks the specified elements.
           If the optional argument is omitted, unchecks all elements.
           Returns the number of elements that have changed from checked to
           unchecked.
           If this list was created with radio=True, raises Exception.
           Element indexes are 0-based.
        """
        if self.radio:
            raise Exception('cannot uncheck radio buttons')
        if element_indexes is None:
            element_indexes = range(self.length())
        changed = 0
        for index in element_indexes:
            if self.uncheck(index, modifiers = modifiers):
                changed += 1
        return changed

    def toggle(self, element_index, modifiers = 0):
        """Checks the specified element if it is unchecked, and unchecks it if
           it is checked.
           Returns True if the element is checked as a result of this call,
           else False.
           Raises Exception if this list was created with radio=True.
           Element indexes are 0-based.
        """
        if self.radio:
            raise Exception('cannot toggle a radio button')
        click(self.element_regions[element_index], modifiers = modifiers,
                region = self.region)
        if self.auto_verify:
            # updates the state
            self.wait(element_index, not self.is_checked(element_index))
        else:
            self._toggle_state(element_index)
        return self.is_checked(element_index)

    def set(self, element_indexes, modifiers = 0):
        """Checks the specified elements and unchecks all other elements.
           Returns the number of elements that were changed.
           If this list was created with radio=True, raises Exception.
           Element indexes are 0-based.
        """
        if self.radio:
            raise Exception('cannot check multiple radio buttons')
        changed = 0
        for index, checked in enumerate(self.checked()):
            if (checked and (index not in element_indexes)) or (
                    (not checked) and (index in element_indexes)):
                self.toggle(index, modifiers = modifiers)
                changed += 1
        return changed

    def update_element(self, element_index):
        """Updates the specified element with its true state.
        """
        region = Region(self.element_regions[element_index])
        # add some space since images may have slightly different size
        marginx = int(region.getW() * 0.2)
        marginy = int(region.getH() * 0.2)
        extendRegion(region, left = marginx, right = marginx, top = marginy,
                bottom = marginy)
        best_checked_score = 0
        best_unchecked_score = 0
        try:
            best_checked = bestMatch(self.images['checked'], region = region,
                    minOverlap = 0.5)
            if best_checked is not None:
                best_checked_score = best_checked[1].getScore()
        except FindFailed:
            pass
        try:
            best_unchecked = bestMatch(self.images['unchecked'],
                    region = region, minOverlap = 0.5)
            if best_unchecked is not None:
                best_unchecked_score = best_unchecked[1].getScore()
        except FindFailed:
            pass
        if best_checked_score == best_unchecked_score:
            if best_checked_score == 0:
                raise Exception('no %s found in region %d' %
                        (self.element_types, element_index))
            raise Exception('score tie: cannot decide whether %s %d is checked or unchecked (score=%f)' %
                    (self.element_type, element_index, best_checked_score))
        state = best_checked_score > best_unchecked_score
        if state != self.is_checked(element_index):
            self._toggle_state(element_index)

    def wait(self, element_index, checked, timeout = None):
        """Waits until the specified element is in the specified state.
           If the element is not in the specified state after the timeout,
           raises Exception.
           If no timeout is specified, uses the default timeout of this list.
        """
        if timeout is None:
            timeout = self.timeout
        if checked:
            oldstate = 'unchecked'
            newstate = 'checked'
        else:
            oldstate = 'checked'
            newstate = 'unchecked'
        if timeout is None:
            _LOGGER.info('waiting for %s %d to become %s',
                    self.element_type, element_index, newstate)
        else:
            _LOGGER.info('waiting for %s %d to become %s, timeout set to %f seconds',
                    self.element_type, element_index, newstate, timeout)
        self.update_element(element_index)
        message = '%s %d still %s after %f seconds' % (
                self.element_type, element_index, oldstate, timeout)
        waiting = Wait(timeout, exception_message = message)
        while bool(self.is_checked(element_index)) != bool(checked):
            waiting.wait()
            self.update_element(element_index)

    def set_element_state(self, element_index, checked):
        """Sets the stored state of the specified element in this list, without
           clicking on the element. This can be used to update the stored state
           of an element if its (real) state was changed by an external event.
           Note that it is possible to set the state of a radio button to
           unchecked.
           If a radio button is set to checked, all other radio buttons in this
           list are set to unchecked.
        """
        if self.radio and checked:
            checked_index = self.checked_element()
            if checked_index is not None and checked_index != element_index:
                self._toggle_state(checked_index)
        if bool(self.is_checked(element_index)) != bool(checked):
            self._toggle_state(element_index)

class Checkboxes(Checkable):
    """A row or column of checkboxes."""

    def __init__(self, images, region = SCREEN, orientation = 0,
            auto_verify = False, timeout = 3):
        """Creates a new row or column of checkboxes."""
        Checkable.__init__(self, images = images, region = region,
                orientation = orientation, radio = False,
                auto_verify = auto_verify, timeout = timeout)

class RadioButtons(Checkable):
    """A row or column of radio buttons."""

    def __init__(self, images, region = SCREEN, orientation = 0,
            auto_verify = False, timeout = 3):
        """Creates a new row or column of radio buttons."""
        Checkable.__init__(self, images = images, region = region,
                orientation = orientation, radio = True,
                auto_verify = auto_verify, timeout = timeout)

class VerticalCheckboxList(Checkboxes):
    """A vertical column of checkboxes."""

    def __init__(self, images, region = SCREEN, auto_verify = False,
            timeout = 3):
        """Creates a new column of checkboxes."""
        Checkboxes.__init__(self, images = images, region = region,
                orientation = 0, auto_verify = auto_verify, timeout = timeout)

class HorizontalCheckboxList(Checkboxes):
    """A horizontal row of checkboxes."""

    def __init__(self, images, region = SCREEN, auto_verify = False,
            timeout = 3):
        """Creates a new row of checkboxes."""
        Checkboxes.__init__(self, images = images, region = region,
                orientation = REGION_SORT_HORIZONTAL,
                auto_verify = auto_verify, timeout = timeout)

class VerticalRadioButtonList(RadioButtons):
    """A vertical column of radio buttons."""

    def __init__(self, images, region = SCREEN, auto_verify = False,
            timeout = 3):
        """Creates a new column of radio buttons."""
        RadioButtons.__init__(self, images = images, region = region,
                orientation = 0, auto_verify = auto_verify, timeout = timeout)

class HorizontalRadioButtonList(RadioButtons):
    """A horizontal row of radio buttons."""

    def __init__(self, images, region = SCREEN, auto_verify = False,
            timeout = 3):
        """Creates a new row of radio buttons."""
        RadioButtons.__init__(self, images = images, region = region,
                orientation = REGION_SORT_HORIZONTAL,
                auto_verify = auto_verify, timeout = timeout)
