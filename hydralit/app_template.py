from abc import ABC, abstractmethod 
from bokeh.models.widgets import Div
import validators
import json
import uuid
import re
import base64
import pickle
import streamlit as st
import pandas as pd


class HydraHeadApp(ABC):
    """
    This is a template class that streamlit applications can inherit from that automatically structures them for use in a Hydralit application.

    A number of convenience methods are also included within the template.
    
    """

    #Must implement this method as the entry point for the application.
    @abstractmethod
    def run(self):
        pass


    def assign_session(self,session_state):
        """
        This method is called when the app is added to a Hydralit application to gain access to the global session state.

        Parameters
        ------------
        session_state:
            The session state as created by the parent application.

        """

        self.session_state = session_state

    def set_access(self,allow_access=0,access_user=''):
        """
        Set the access permission and the assigned username for that access during the current session.

        Parameters
        -----------
        allow_access: int, 0
            Value indicating if access has been granted, can be used to create levels of permission.
        access_user: str, None
            The username the access has been granted to for this session.

        """

        #Set the global access flag
        self.session_state.allow_access = allow_access

        #Also, who are we letting in..
        self.session_state.current_user = access_user


    def check_access(self):
        """
        Check the access permission and the assigned user for the running session.

        Returns
        ---------
        tuple: access_level, username

        """

        return int(self.session_state.allow_access), str(self.session_state.current_user)


    def do_redirect(self,redirect_target_app=None):
        """
        Used to redirect to another app within the parent application. If the redirect_target is a valid url, a new window will open and the browser will set focus on the new window while leaving this app in it's current state.

        Parameters
        ------------
        redirect_target_app: str, None
            The name of the target app or a valid url, this must be the registered name when the app was added to the parent. If no target is provided, it will redirect to the HydraApp home app. If the redirect_target is a valid url, a new window will open and the browser will set focus on the new window while leaving this app in it's current state.

        """

        if redirect_target_app is not None and validators.url(redirect_target_app):
            js = "window.open('{}')".format(redirect_target_app)
            html = '<img src onerror="{}">'.format(js)
            div = Div(text=html)
            st.bokeh_chart(div)
        else:        
            self.session_state.selected_app = redirect_target_app
            st.experimental_rerun()


    def download_button(self,object_to_download, download_filename, button_text, parent_container=None,pickle_it=False, css_formatting=None, **kwargs):
        """
        A convenience method to include a dataframe download button within this application.

        Parameters
        ------------
        object_to_download: Pickle, DataFrame
            This is the data object that will be available to download as either a csv if the object is a Pandas DataFrame or as a JSON text file if is a pickle file.
        download_filename: str
            The default name of the download file.
        button_text: str
            The text to display on the download button
        parent_container: Streamlit.container
            The parent container in which to create the button.
        pickle_it: bool, False
            Flag to indicate if the download data should be pickled.
        css_formatting: Dict, None
            A css formatting string to be applied to the download button. The format dict must have a value of the css string and a key value of the css selection tag value, e.g. mybutton
        kwargs:
            Keyword arguments to be passed to either the json.dump or Pandas.to_csv method used for the data export.

        """

        if pickle_it:
            try:
                object_to_download = pickle.dumps(object_to_download)
            except pickle.PicklingError as e:
                st.write(e)
                return None

        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(**kwargs)

        else:
            object_to_download = json.dumps(object_to_download,**kwargs)

        try:
            b64 = base64.b64encode(object_to_download.encode()).decode()

        except AttributeError as e:
            b64 = base64.b64encode(object_to_download).decode()

        button_uuid = str(uuid.uuid4()).replace('-', '')
        button_id = re.sub('\d+', '', button_uuid)

        if css_formatting is None:
            css_styling = f""" 
                <style>
                    #{button_id} {{
                        display: inline-flex;
                        -webkit-box-align: center;
                        align-items: center;
                        -webkit-box-pack: center;
                        justify-content: center;
                        font-weight: 400;
                        padding: 0.25rem 0.75rem;
                        border-radius: 0.25rem;
                        margin: 0px;
                        line-height: 1.6;
                        color: inherit;
                        width: auto;
                        background-color: rgb(19, 23, 32);
                        border: 1px solid rgba(250, 250, 250, 0.2);
                    }} 
                    #{button_id}:hover {{
                        border-color: rgb(246, 51, 102);
                        color: rgb(246, 51, 102);
                    }}
                    #{button_id}:active {{
                        color: rgb(255, 255, 255);
                        border-color: rgb(246, 51, 102);
                        background-color: rgb(246, 51, 102);
                    }}
                </style> """
        else:
            tag_name = next(iter(css_formatting.keys()))
            css_styling = next(iter(css_formatting.values()))
            css_styling = css_styling.replace(tag_name,button_id)


        dl_link = css_styling+f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

        if parent_container is None:
            st.markdown(dl_link, unsafe_allow_html=True)
        else:
            parent_container.markdown(dl_link, unsafe_allow_html=True)
        
        return dl_link
