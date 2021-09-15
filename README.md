 
 # **Hydralit** <img src="https://github.com/TangleSpace/hydralit/raw/main/docs/images/hydra.png" alt="hydra" width="50"/>
The Hydralit package is a wrapping and template project to combine multiple independant (or somewhat dependant) Streamlit applications into a multi-page application.

Currently the project implements a host application HydraApp and each child application simply needs to be a class deriving from the HydraHeadApp class and implement a single, simple method, run().

When converting existing applications, you can effectively put all the existing code inside the run() method and create a wrapper class deriving from HydraHeadApp. Then you create the parent app as an instance of HydraApp, add your child apps to it (see examples [app.py]("https://github.com/TangleSpace/hydralit-example/blob/main/app.py") and [secure_app.py]("https://github.com/TangleSpace/hydralit-example/blob/main/secure_app.py")) and with only a few lines of code everything will magically come together.

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

## Installing Hydralit
Hydralit can be installed from PyPI:

```bash
pip install hydralit
```

## Latest features
 - Support for a non-secure app in a secure app (like a signup app)
 - Full integration with the Hydralit Navbar that now supports complex nav!
 - some bug fixes where app to app redirect was inconsistant
 - Banners
 - Compression behind download button
 - Hydralit Navbar


Complex and sticky nav with no Streamlit markers is as easy as a couple of parameters in the Hydralit constructor.
 ```python
app = HydraApp(title='Secure Hydralit Data Explorer',favicon="🐙",hide_streamlit_markers=True,use_navbar=True, navbar_sticky=True)
 ```

## Now powered by [Hydralit Components](https://github.com/TangleSpace/hydralit_components).
Currently the complex collapsable menu format is not supported by Hydralit Navbar, however if you can live without it for now, you will be rewarded with an animated and responsive navbar.
<p align="center">
<img src="https://raw.githubusercontent.com/tanglespace/hydralit_components/master/resources/hydralit_navbar.gif" title="Quick Example" alt="Quick Example", width="60%" height="100%">
</p>

### Examples
You can try it out by running the two sample applications with their children that are located in the [hydralit-example repository](https://github.com/TangleSpace/hydralit-example).
```bash
hydralit_example> pip install -r requirements.txt

hydralit_example> streamlit run secure.app
```

<h1><a href="https://hydralit-secure-sample.herokuapp.com/">You can see this example running here</a></h1>
<img src="https://github.com/TangleSpace/hydralit-example/raw/main/docs/images/hydralit-secure-example.gif" alt="example" width="80%"/>

### Converting existing applications
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

#### That's it!
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
    app = HydraApp(title='Secure Hydralit Data Explorer',favicon="🐙",nav_horizontal=True,hide_streamlit_markers=True,use_navbar=True, navbar_sticky=True,navbar_theme=over_theme)
  
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

    # If the menu is cluttered, just rearrange it into sections!
    # completely optional, but if you have too many entries, you can make it nicer by using accordian menus
    complex_nav = {
        'Home': ['Home'],
        'Intro 🏆': ['Cheat Sheet',"Solar Mach"],
        'Hotstepper 🔥': ["Sequency Denoising","Sequency (Secure)"],
        'Clustering': ["Uber Pickups"],
        'NLP': ["Spacy NLP"],
    }


    #add a custom loader for app transitions
    #app.add_loader_app(apps.MyLoadingApp())

    #if the menu is looking shit, use some sections
    st.markdown("<h2 style='text-align: center;'>This example was written using the <a href = https://github.com/TangleSpace/hydralit>Hydralit</a> library. Sourecode for this example is located <a href = https://github.com/TangleSpace/hydralit-example>here</a>.</h2>",unsafe_allow_html=True)
  

    #and finally just the entire app and all the children.
    app.run(complex_nav)
```
You can try it out by running the two sample applications with their children that are located in the [hydralit-example repository](https://github.com/TangleSpace/hydralit-example).
```bash
hydralit_example> pip install -r requirements.txt

hydralit_example> streamlit run secure.app
```