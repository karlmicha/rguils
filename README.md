RGUILS: **R**obust **GUI** Automation **L**ibrary for **S**ikuli

  1. _ro-gels_ = [roʊgəls]
  1. _ra-gils_ = [rɑ:gɪls]

RGUILS is a python library for robust GUI automation with [Sikuli](http://sikuli.org/). It provides an object-oriented API to model GUI elements, such as sets of buttons, checkboxes, radio buttons, windows and dialogue hierarchies for GUI automation and testing, all in a robust way.

RGUILS enables you to write object-oriented APIs to automate any sequence of actions in complex graphical user interfaces robustly with relatively little code, rather than just automate fixed UI interaction sequences.

# How it works #

Say you have an application with three buttons Back, Next, Cancel that you want to automate.

## 1. Create a Sikuli project ##

Create a Sikuli project with constants for the images of all your buttons in different states:

![project buttons](wiki/images/project_buttons.jpg)

## 2. Configure the import

Tell RGUILS where to find your Sikuli project. Put the following line in `sikuliimport\settings.py`:
```python
SIKULI_PROJECT_DIRS = ['C:\\Documents and Settings\\username\\Sikuli\\buttons.sikuli']
```

## 3. Use the RGUILS API

Now you can use your button images to automate the buttons of your application in a robust way. RGUILS automatically groups your button images by button type, detects which buttons exist on the screen and whether they are enabled or disabled, and lets you click on them:
```python
from seagull.images import IMG_BUTTONS, IMG_BUTTONS_DISABLED
from seagull.buttons import Buttons

# define buttons
buttons = Buttons(IMG_BUTTONS, IMG_BUTTONS_DISABLED)

# locate buttons on the screen
buttons.find_buttons()

buttons.waitUntilButtonIsEnabled('next', 15)
buttons.click('next')
```

# Learn more

To learn how to use RGUILS, read the SampleInstaller tutorial. To start using RGUILS, please visit the GettingStarted page. To learn more about Sikuli, read this SikuliOverview. For a more in-depth discussion of GUI automation issues, read this page about [robust GUI automation](https://github.com/karlmicha/rguils/wiki/RobustGUIAutomation).
