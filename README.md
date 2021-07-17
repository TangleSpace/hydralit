 
 ## Hydralit <img src="./docs/images/hydra.png" alt="drawing" width="50"/>
The Hydralit package is a wrapping and template project to combine multiple independant (or somewhat dependant) Streamlit applications into a multi-page application.

Currently the project implements a host application HydraApp and each child application simply needs to be a class deriving from the HydraHeadApp class and implement a single, simple method, run().

When converting existing applications, you can effectively put all the existing code inside the run() method and create a wrapper class deriving from HydraHeadApp. Then you create the parent app as an instance of HydraApp, add your child apps to it (see examples [app.py]("https://github.com/TangleSpace/hydralit-example/blob/main/app.py") and [secure_app.py]("https://github.com/TangleSpace/hydralit-example/blob/main/secure_app.py")) and with only a few lines of code everything will magically come together.


## Installing Hydralit
Hydralit can be installed from PyPI:

```bash
pip install hydralit
```

### Examples
You can try it out by running the two sample applications with their children that are located in the [hydralit-example repository](https://github.com/TangleSpace/hydralit-example).
```bash
hydralit_example> pip install -r requirements.txt

hydralit_example> streamlit run secure.app
```

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
    #------------all valid container references, do not initilise or page config will not be applied (this is from beta containers, beta, who knew!).
    #my_container = st.sidebar
    # my_container = st.sidebar.beta_container
    # my_container = st.sidebar.beta_columns
    #my_container = st
    # my_container = st.beta_container
    # my_container = st.beta_columns
    my_container = None

    #this is the host application, we add children to it and that's it!
    app = HydraApp(title='Secure Hydralit Data Explorer',favicon="🐙",nav_container=my_container,nav_horizontal=True,hide_streamlit_markers=True)
  
    #add all your application classes here
    app.add_app("Cheat Sheet", icon="📚", app=apps.CheatApp())
    app.add_app("Sequency Denoising",icon="🔊", app=apps.WalshApp(title='Walsh Data'))
    app.add_app("Sequency (Secure)",icon="🔊🔒", app=apps.WalshAppSecure(title='Walsh Secure'))
    app.add_app("Solar Mach", icon="🛰️", app=apps.SolarMach(title='Solar-MACH'))

    #Home button will be in the middle of the nav list now
    app.add_app("Home", icon="🏠", app=apps.HomeApp(title='Home'),is_home=True) 

    app.add_app("Spacy NLP", icon="⌨️", app=apps.SpacyNLP())
    app.add_app("Uber Pickups", icon="🚖", app=apps.UberNYC())

    #we want to have secure access for this HydraApp, so we provide a login application
    #optional logout label, can be blank for something nicer!

    #app.add_app("Login", apps.LoginApp(title='Login'),is_login=True,logout_label='Piss Off 🖕')
    app.add_app("Login", apps.LoginApp(title='Login'),is_login=True) 

    # If the menu is cluttered, just rearrange it into sections!
    # completely optional, but if you have too many entries, you can make it nicer by using accordian menus
    complex_nav = {
        'Home': ['Home'],
        'Intro 🏆': ['Cheat Sheet',"Solar Mach"],
        'Hotstepper 🔥': ["Sequency Denoising","Sequency (Secure)"],
        'Models 🧩': ["Spacy NLP","Uber Pickups"],
    }
    
    #add a custom loader for app transitions
    #app.add_loader_app(apps.MyLoadingApp())

    #st.write('**This is completely outside of all HydraApp and HydraHeadApps, we can do whatever we want!** 🤪')

    #run with default menu layout
    #app.run()

    #if the menu is looking shit, use some sections
    app.run(complex_nav)
```
You can try it out by running the two sample applications with their children that are located in the [hydralit-example repository](https://github.com/TangleSpace/hydralit-example).
```bash
hydralit_example> pip install -r requirements.txt

hydralit_example> streamlit run secure.app
```