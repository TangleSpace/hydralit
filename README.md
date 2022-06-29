 
 # **Hydralit** <img src="https://github.com/TangleSpace/hydralit/raw/main/docs/images/hydra.png" alt="hydra" width="50"/>
The Hydralit package is a wrapping and template project to combine multiple independant (or somewhat dependant) Streamlit applications into a multi-page application.

Currently the project implements a host application HydraApp and each child application simply needs to be either a class deriving from the HydraHeadApp class and implementing a single, simple method, run() for maximum profit, or you can use a Flask style decorator on your functions to add them directly as seperate Streamlit pages.

When converting existing applications, you can effectively put all the existing code inside the run() method and create a wrapper class deriving from HydraHeadApp or put a decorator over the function. Then you create the parent app as an instance of HydraApp, add your child apps to it (see example [secure_app.py]("https://github.com/TangleSpace/hydralit-example/blob/main/secure_app.py")) and with only a few lines of code everything will magically come together.

<br>

## **Version 1.0.13 fixes the long standing stupidty of Streamlit constantly changing the method name of the session context manager, now works with Streamlit 1.9.x and above.**
 - Added the ability to disable to use of the app loader within the constructor.
<br>

## **Version 1.0.12 fixes an edge case when installing with Streamlit for the first time.**
<br>

## **Hydralit now fully supports all versions of Streamlit, including 1.4.0, despite the odd changes made in version 1.4.0 that completely broke Hydralit.**
<br>

## **Hydralit >=1.0.3 now requires a minimum version of Streamlit >=0.86.x to fully support the recently migrated beta containers, if using Streamlit <=0.85.x please continue to use Hydralit <=1.0.2**


<br>
<p align="center">
	<a href="https://pepy.tech/project/hydralit/" alt="PyPI downloads">
	<img src="https://pepy.tech/badge/hydralit" />
	</a>
    <a href="https://www.python.org/" alt="Python version">
        <img src="https://img.shields.io/pypi/pyversions/hydralit" /></a>
    <a href="https://pypi.org/project/hydralit/" alt="PyPI version">
        <img src="https://img.shields.io/pypi/v/hydralit" /></a>
    <a href="https://hydralit.aur-license.org/" alt="License">
        <img src="http://img.shields.io/:license-Apache-blue.svg?style=flat-square"></a>
    <a href="https://streamlit.io/" alt="Streamlit">
        <img src="http://img.shields.io/:streamlit->=0.86.0-blue.svg?style=flat-square"></a>
</p>

## Installation
Hydralit can be installed from PyPI:

```bash
pip install -U hydralit
```

<h1><a href="https://hydralit-secure-sample.herokuapp.com/">You can see what's possible using Hydralit here!</a></h1>

# Lightning Example
 ```python
#when we import hydralit, we automatically get all of Streamlit
import hydralit as hy

app = hy.HydraApp(title='Simple Multi-Page App')

@app.addapp()
def my_home():
  hy.info('Hello from app1')

@app.addapp()
def app2():
  hy.info('Hello from app 2')


#Run the whole lot, we get navbar, state management and app isolation, all with this tiny amount of work.
app.run()
 ```
 
 This tiny amount of code creates a menu and pages that render when the target function is called by selecting it from the menu.
 <p align="center">
<img src="https://github.com/TangleSpace/hydralit_components/blob/main/resources/baby_demo.gif?raw=true" title="Quick Example" alt="Quick Example", width="100%" height="100%">
</p>


## Latest features (version 1.0.11)
 - Fully supports all versions of Streamlit, including 1.4.0 (big thanks to [oggers](https://github.com/oggers) for some amazing support!).
 - Fixed the missing error handling bug, now all exceptions are raised to be handled however the user chooses instead of capturing and displaying an image. (big thanks to [rambam613](https://github.com/rambam613) for finding and fixing this bug, very nice!).
 - Can completely customise the Home and Logout menu entries, title and icon data from the add_app entry will be used for these items now as well as the existing.
<p align="center">
<img src="https://github.com/TangleSpace/hydralit_components/blob/main/resources/customised_navbar.PNG?raw=true" title="Navbar" alt="Navbar", width="100%" height="100%">
</p>

 - Cleaned up the formatting when running in sticky and hiding Streamlit headers and footers, yes, they will come back now when using the navbar.
 - Removed the background effort for all loader animations (everyone hated this).
 - Smaller, sleeker navbar, including a much nicer non-animated mode.
  <p align="center">
<img src="https://github.com/TangleSpace/hydralit_components/blob/main/resources/non-animated_navbar.PNG?raw=true" title="Navbar" alt="Navbar", width="100%" height="100%">
</p>

 - Full offline support for Font Awesome and Bootstrap icons for navbar entries, as well as all emojis.
 - Improved performance with some refactoring of the session and transition code, apps load faster now.

<br><br

## Version 1.0.10 features
 - Added Flask like decorators to convert any function into a child app (see example below)
 - Can set auto login with guest account when using a secure app
 - Support for a non-secure app in a secure app (like a signup app)
 - Full integration with the Hydralit Navbar that now supports complex nav!
 - some bug fixes where app to app redirect was inconsistant
 - Banners
 - Compression behind download button
 - Hydralit Navbar
 - Can turn off the navbar animation now! (must be using Hydralit_components >=1.0.4)

## NOTE
Due to the Streamlit execution model, the ability to use internal nav links from a child app is one-shot when using the navbar. This means that the internal link will redirect to the child, however if a script rerun request is made within the child app (changing the value of a widget for example), the nav will bounce back to the calling app. You can disable the navbar and the Streamlit core components nav menu will appear and the internal links will work as expected.


## Complex and sticky nav with no Streamlit markers is as easy as a couple of parameters in the Hydralit constructor.
 ```python
app = HydraApp(title='Secure Hydralit Data Explorer',favicon="🐙",hide_streamlit_markers=True,use_navbar=True, navbar_sticky=True)
 ```

## Now powered by [Hydralit Components](https://github.com/TangleSpace/hydralit_components).
The Hydralit Navbar is fully integrated, theme aware and animated (you can turn it off if you like), just add your child apps and go, the navbar will appear automatically.
# Navbar - Responsive, theme aware and animated.
<p align="center">
<img src="https://raw.githubusercontent.com/tanglespace/hydralit_components/master/resources/hydralit_navbar.gif" title="Quick Example" alt="Quick Example", width="60%" height="100%">
</p>

# Spinners and Loaders
Out of the box you get a nice loader/spinner when navigating between apps/pages. You can also create your own loader app and completely customise every part of how it looks and when it loads, even creating different effects depending on the target application. See the [Hydralit secure example code](https://github.com/TangleSpace/hydralit-example/blob/main/apps/myloading_app.py) to see what is possible.

<p align="center">
<img src="https://github.com/TangleSpace/hydralit_components/blob/main/resources/standard_loaders.gif?raw=true" title="HyLoaders" alt="HyLoaders", width="45%" height="45%">
<img src="https://github.com/TangleSpace/hydralit_components/blob/main/resources/pretty_loaders.gif?raw=true" title="HyLoaderspretty" alt="HyLoaders", width="45%" height="45%">
<img src="https://github.com/TangleSpace/hydralit_components/blob/main/resources/pulse_bars.gif?raw=true" title="HyLoaderspretty" alt="HyLoaders", width="100%" height="60%">


## Quick Start
If you have some functions and want them to run like seperate pages, you can quickly get going with a Flask style decorator over your functions.
 ```python
#when we import hydralit, we automatically get all of Streamlit
import hydralit as hy

app = hy.HydraApp(title='Simple Multi-Page App')

@app.addapp(is_home=True)
def my_home():
  hy.info('Hello from Home!')

@app.addapp()
def app2():
  hy.info('Hello from app 2')

@app.addapp(title='The Best', icon="🥰")
def app3():
  hy.info('Hello from app 3, A.K.A, The Best 🥰')

#Run the whole lot, we get navbar, state management and app isolation, all with this tiny amount of work.
app.run()
 ```
This tiny amount of code creates a nice custom multi-page app as below.
 <p align="center">
<img src="https://github.com/TangleSpace/hydralit_components/blob/main/resources/quick_demo.gif?raw=true" title="Quick Example" alt="Quick Example", width="100%" height="100%">
</p>


### Examples
You can try it out by running the two sample applications with their children that are located in the [hydralit-example repository](https://github.com/TangleSpace/hydralit-example).
```bash
hydralit_example> pip install -r requirements.txt

hydralit_example> streamlit run secure.app
```

<h1><a href="https://hydralit-secure-sample.herokuapp.com/">You can see this example running here</a></h1>


# Converting existing applications
This code sample comes directly from the [Streamlit example data explorer](https://docs.streamlit.io/en/stable/tutorial/create_a_data_explorer_app.html#let-s-put-it-all-together)
```python
import streamlit as st
import pandas as pd
import numpy as np

st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Number of pickups by hour')
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

# Some number in the range 0-23
hour_to_filter = st.slider('hour', 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader('Map of all pickups at %s:00' % hour_to_filter)
st.map(filtered_data)
```

Let's also use a simple application to combine with the demo above.
```python
import streamlit as st
import numpy as np
import pandas as pd
from data.create_data import create_table

def app():
    st.title('Small Application with a table and chart.')

    st.write("See `apps/simple.py` to know how to use it.")

    st.markdown("### Plot")
    df = create_table()

    st.line_chart(df)
```


You can easily convert these apps to be used within Hydralit by simply wrapping each in a class derived from HydraHeadApp within Hydralit and putting all the code in the run() method.

For the above Streamlit demo application, this means all that is needed is a slight modification, we create a file sample_app.py and add;
```python
import streamlit as st
import pandas as pd
import numpy as np

#add an import to Hydralit
from hydralit import HydraHeadApp

#create a wrapper class
class MySampleApp(HydraHeadApp):

#wrap all your code in this method and you should be done
    def run(self):
        #-------------------existing untouched code------------------------------------------
        st.title('Uber pickups in NYC')

        DATE_COLUMN = 'date/time'
        DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
                    'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

        @st.cache
        def load_data(nrows):
            data = pd.read_csv(DATA_URL, nrows=nrows)
            lowercase = lambda x: str(x).lower()
            data.rename(lowercase, axis='columns', inplace=True)
            data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
            return data

        data_load_state = st.text('Loading data...')
        data = load_data(10000)
        data_load_state.text("Done! (using st.cache)")

        if st.checkbox('Show raw data'):
            st.subheader('Raw data')
            st.write(data)

        st.subheader('Number of pickups by hour')
        hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
        st.bar_chart(hist_values)

        # Some number in the range 0-23
        hour_to_filter = st.slider('hour', 0, 23, 17)
        filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

        st.subheader('Map of all pickups at %s:00' % hour_to_filter)
        st.map(filtered_data)
        #-------------------existing untouched code------------------------------------------
```
For the other small application, again we can convert this very easily by wrapping in a class derived from HydraHeadApp from Hydralit and putting all the code in the run() method, we create a file small_app.py and add;
```python
import streamlit as st
import numpy as np
import pandas as pd
from data.create_data import create_table

#add an import to Hydralit
from hydralit import HydraHeadApp

#create a wrapper class
class MySmallApp(HydraHeadApp):

#wrap all your code in this method and you should be done
    def run(self):
        #-------------------existing untouched code------------------------------------------
        st.title('Small Application with a table and chart.')

        st.markdown("### Plot")
        df = create_table()

        st.line_chart(df)
```

These are is now ready to be used within a Hydralit application. We just need to create a simple host application that derives from the HydraApp class in Hydralit, add the children and we are done! we create a file host_app.py and add;
```python
from hydralit import HydraApp
import streamlit as st
from sample_app import MySampleApp
from small_app import MySmallApp


if __name__ == '__main__':

    #this is the host application, we add children to it and that's it!
    app = HydraApp(title='Sample Hydralit App',favicon="🐙")
  
    #add all your application classes here
    app.add_app("Small App", icon="🏠", app=MySmallApp())
    app.add_app("Sample App",icon="🔊", app=MySampleApp())

    #run the whole lot
    app.run()
```

### Or you could use the decorator method shown in the Lightning example and simply wrap your functions, both ways work, you can get access to more controls with the class method as the template class allows access to the Hydralit internal state for access and navigation information.

This super simple example is made of 3 files.
```
hydralit sample project
│   host_app.py
│   small_app.py
│   sample_app.py
```
### Run this sample
```bash
hydralit sample project> pip install hydralit

hydralit sample project> streamlit run host.app
```

### Examples
The code for a host application that is secured with a login app is shown below, the entire example is located in the [hydralit-example repository](https://github.com/TangleSpace/hydralit-example).

```python
from hydralit import HydraApp
import streamlit as st
import apps


if __name__ == '__main__':
    over_theme = {'txc_inactive': '#FFFFFF'}
    #this is the host application, we add children to it and that's it!
    app = HydraApp(
        title='Secure Hydralit Data Explorer',
        favicon="🐙",
        hide_streamlit_markers=False,
        #add a nice banner, this banner has been defined as 5 sections with spacing defined by the banner_spacing array below.
        use_banner_images=["./resources/hydra.png",None,{'header':"<h1 style='text-align:center;padding: 0px 0px;color:black;font-size:200%;'>Secure Hydralit Explorer</h1><br>"},None,"./resources/lock.png"], 
        banner_spacing=[5,30,60,30,5],
        use_navbar=True, 
        navbar_sticky=False,
        navbar_theme=over_theme
    )

    #Home button will be in the middle of the nav list now
    app.add_app("Home", icon="🏠", app=apps.HomeApp(title='Home'),is_home=True)

    #add all your application classes here
    app.add_app("Cheat Sheet", icon="📚", app=apps.CheatApp(title="Cheat Sheet"))
    app.add_app("Sequency Denoising",icon="🔊", app=apps.WalshApp(title="Sequency Denoising"))
    app.add_app("Sequency (Secure)",icon="🔊🔒", app=apps.WalshAppSecure(title="Sequency (Secure)"))
    app.add_app("Solar Mach", icon="🛰️", app=apps.SolarMach(title="Solar Mach"))
    app.add_app("Spacy NLP", icon="⌨️", app=apps.SpacyNLP(title="Spacy NLP"))
    app.add_app("Uber Pickups", icon="🚖", app=apps.UberNYC(title="Uber Pickups"))
    app.add_app("Solar Mach", icon="🛰️", app=apps.SolarMach(title="Solar Mach"))

    #we have added a sign-up app to demonstrate the ability to run an unsecure app
    #only 1 unsecure app is allowed
    app.add_app("Signup", icon="🛰️", app=apps.SignUpApp(title='Signup'), is_unsecure=True)

    #we want to have secure access for this HydraApp, so we provide a login application
    #optional logout label, can be blank for something nicer!
    app.add_app("Login", apps.LoginApp(title='Login'),is_login=True) 

    #specify a custom loading app for a custom transition between apps, this includes a nice custom spinner
    app.add_loader_app(apps.MyLoadingApp(delay=5))
    #app.add_loader_app(apps.QuickLoaderApp())

    #we can inject a method to be called everytime a user logs out
    @app.logout_callback
    def mylogout_cb():
        print('I was called from Hydralit at logout!')

    #we can inject a method to be called everytime a user logs in
    @app.login_callback
    def mylogin_cb():
        print('I was called from Hydralit at login!')

    #if we want to auto login a guest but still have a secure app, we can assign a guest account and go straight in
    app.enable_guest_access()

    #--------------------------------------------------------------------------------------------------------------------
    #if the menu is looking shit, use some sections
    #check user access level to determine what should be shown on the menu
    user_access_level, username = app.check_access()

    # If the menu is cluttered, just rearrange it into sections!
    # completely optional, but if you have too many entries, you can make it nicer by using accordian menus
    if user_access_level > 1:
        complex_nav = {
            'Home': ['Home'],
            'Intro 🏆': ['Cheat Sheet',"Solar Mach"],
            'Hotstepper 🔥': ["Sequency Denoising","Sequency (Secure)"],
            'Clustering': ["Uber Pickups"],
            'NLP': ["Spacy NLP"],
        }
    elif user_access_level == 1:
        complex_nav = {
            'Home': ['Home'],
            'Intro 🏆': ['Cheat Sheet',"Solar Mach"],
            'Hotstepper 🔥': ["Sequency Denoising"],
            'Clustering': ["Uber Pickups"],
            'NLP': ["Spacy NLP"],
        }
    else:
        complex_nav = {
            'Home': ['Home'],
        }

  
    #and finally just the entire app and all the children.
    app.run(complex_nav)

    #(DEBUG) print user movements and current login details used by Hydralit
    #---------------------------------------------------------------------
    user_access_level, username = app.check_access()
    prev_app, curr_app = app.get_nav_transition()
    print(prev_app,'- >', curr_app)
    print(int(user_access_level),'- >', username)
    #---------------------------------------------------------------------
```

You can try it out by running the two sample applications with their children that are located in the [hydralit-example repository](https://github.com/TangleSpace/hydralit-example).
```bash
hydralit_example> pip install -r requirements.txt

hydralit_example> streamlit run secure.app
```