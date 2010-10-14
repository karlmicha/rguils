"""sikuliimport/projects.py
   Import images from Sikuli projects with absolute pathnames.
   The Sikuli projects are defined in sikulisettings.py.
"""

import os.path, re, logging

_SIKULI_IMAGE_FILENAME_PATTERN = re.compile(r'^\d{10,15}\.png$')

logging.basicConfig()
_LOGGER = logging.getLogger(__name__)

def make_abs_sikuli_image_path(value, projectdir):
    """Returns a value that is equal to the specified value except that all
       Sikuli image filenames are replaced with their absolute pathnames in
       projectdir.
       Recurses into list, dictionary, tuple, set and frozenset values.
    """
    if isinstance(value, basestring):
        if _SIKULI_IMAGE_FILENAME_PATTERN.match(value):
            return os.path.join(projectdir, value)
        else:
            return value
    elif isinstance(value, list):
        return [make_abs_sikuli_image_path(element, projectdir)
                for element in value]
    elif isinstance(value, dict):
        return dict([(el_key, make_abs_sikuli_image_path(el_value, projectdir))
                    for el_key, el_value in value.iteritems()])
    elif isinstance(value, tuple):
        return tuple([make_abs_sikuli_image_path(element, projectdir)
                    for element in value])
    elif isinstance(value, set):
        return set([make_abs_sikuli_image_path(element, projectdir)
                    for element in value])
    elif isinstance(value, frozenset):
        return frozenset([make_abs_sikuli_image_path(element, projectdir)
                    for element in value])
    else:
        return value

def import_sikuli_project(projectdir):
    """Imports symbols from the specified Sikuli project directory.
    """
    if not projectdir.endswith('.sikuli'):
        raise ImportError('Sikuli directory must end with .sikuli')
    modulename = os.path.basename(projectdir[0:-7])
    modulefilename = os.path.join(projectdir, modulename + '.py')
    symbols = dict()
    try:
        execfile(modulefilename, symbols)
    except IOError, error:
        raise ImportError('cannot import images from %s: %s' %
                (modulefilename, error.args[1]))
    glob = globals()
    for name, value in symbols.iteritems():
        if name.startswith('_'):
            continue
        if name in glob:
            _LOGGER.warn('symbol %s="%s" redefined as "%s"',
                    name, glob[name], value)
            continue
        glob[name] = make_abs_sikuli_image_path(value, projectdir)

__IMPORTED_PROJECTS = []

try:
    import sikuliimport.settings as settings
except ImportError:
    try:
        import sikuliimport.defaultsettings as settings
    except ImportError:
        raise ImportError('neither sikuliimport/settings.py nor sikuliimport/defaultsettings.py was found, cannot import images from Sikuli')

try:
    SIKULI_DIRS = settings.SIKULI_PROJECT_DIRS
except AttributeError:
    raise ImportError('no SIKULI_PROJECT_DIRS defined in %s, cannot import images from Sikuli' %
            settings.__name__)

if not isinstance(SIKULI_DIRS, list):
    raise TypeError('SIKULI_PROJECT_DIRS must be a list')

for sikulidir in SIKULI_DIRS:
    if not isinstance(sikulidir, basestring):
        raise TypeError('elements in SIKULI_PROJECT_DIRS must be string type (value was %s)' %
                str(sikulidir))
    if sikulidir in __IMPORTED_PROJECTS:
        _LOGGER.warn('images from %s already imported', sikulidir)
        continue
    import_sikuli_project(sikulidir)
