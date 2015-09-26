RGUILS: <b>R</b>obust <b>GUI</b> Automation <b>L</b>ibrary for <b>S</b>ikuli

  1. _ro-gels_ = [roʊgəls]
  1. _ra-gils_ = [rɑ:gɪls]

RGUILS is a python library for robust GUI automation with [Sikuli](http://sikuli.org/). It provides an object-oriented API to model GUI elements, such as sets of buttons, checkboxes, radio buttons, windows and dialogue hierarchies for GUI automation and testing, all in a robust way.

RGUILS enables you to write object-oriented APIs to automate any sequence of actions in complex graphical user interfaces robustly with relatively little code, rather than just automate fixed UI interaction sequences.

# How it works #

Say you have an application with three buttons Back, Next, Cancel that you want to automate.

## 1. Create a Sikuli project ##

Create a Sikuli project with constants for the images of all your buttons in different states:

<img src='http://rguils.googlecode.com/svn/wiki/images/project_buttons.jpg' border='1'>

<h2>2. Configure the import</h2>

Tell RGUILS where to find your Sikuli project. Put the following line in <code>sikuliimport\settings.py</code>:<br>
<br>
<pre><code>SIKULI_PROJECT_DIRS = ['C:\\Documents and Settings\\username\\Sikuli\\buttons.sikuli']<br>
</code></pre>

<h2>3. Use the RGUILS API</h2>

Now you can use your button images to automate the buttons of your application in a robust way. RGUILS automatically groups your button images by button type, detects which buttons exist on the screen and whether they are enabled or disabled, and lets you click on them:<br>
<br>
<pre><code>from seagull.images import IMG_BUTTONS, IMG_BUTTONS_DISABLED<br>
from seagull.buttons import Buttons<br>
<br>
# define buttons<br>
buttons = Buttons(IMG_BUTTONS, IMG_BUTTONS_DISABLED)<br>
<br>
# locate buttons on the screen<br>
buttons.find_buttons()<br>
<br>
buttons.waitUntilButtonIsEnabled('next', 15)<br>
buttons.click('next')<br>
</code></pre>

<h1>Learn more</h1>

To learn how to use RGUILS, read the SampleInstaller tutorial. To start using RGUILS, please visit the GettingStarted page. To learn more about Sikuli, read this SikuliOverview. For a more in-depth discussion of GUI automation issues, read this page about <a href='RobustGUIAutomation.md'>RobustGUIAutomation</a>.