from typing import Dict
import streamlit as st
from hydralit.sessionstate import SessionState
from hydralit.loading_app import LoadingApp

class HydraApp(object):
    """
    Class to create a host application for combining multiple streamlit applications.

    """
    
    def __init__(self, title='Streamlit MultiApp', nav_container=None, nav_horizontal=True,layout='wide', favicon = "🧊",sidebar_state = 'auto', hide_streamlit_markers = False, clear_cross_app_sessions=True, session_params=None):
        """
        A class to create an Multi-app Streamlit application. This class will be the host application for multiple applications that are added after instancing.

        The secret saurce to making the different apps work together comes from the use of a global session store that is shared with any HydraHeadApp that is added to the parent HydraApp.
        The session store is created when this class is instanced, by default the store contains the following variables that are used across the child apps:
         - previous_app
         = selected_app
         - preserve_state
         - allow_access
         - current_user

        More global values can be added by passing in a Dict when instancing the class, the dict needs to provide a name and default value that will be added to the global session store.

        Parameters
        -----------
        title: str, 'Streamlit MultiApp'
            The title of the parent app, this name will be used as the application (web tab) name.
        nav_container: Streamlit.container, None
            A container in which to populate the navigation buttons for each attached HydraHeadApp. Default will be a horizontal aligned banner style over the child applications. If the Streamlit sidebar is the target container, the navigation items will appear at the top and the default state of the sidebar will be expanded.
        nav_horizontal: bool, True
            To align the navigation buttons horizonally within the navigation container, if False, the items will be aligned vertically.
        layout: str, 'wide'
            The layout format to be used for all app pages (HydraHeadApps), same as the layout variable used in `set_page_config <https://docs.streamlit.io/en/stable/api.html?highlight=set_page_config#streamlit.set_page_config>`.
        favicon: str
            An inline favicon image to be used as the application favicon.
        sidebar_state: str, 'auto'
            The starting state of the sidebase, same as variable used in `set_page_config <https://docs.streamlit.io/en/stable/api.html?highlight=set_page_config#streamlit.set_page_config>`.
        hide_streamlit_markers: bool, False
            A flag to hide the default Streamlit menu hamburger button and the footer watermark.
        clear_cross_app_sessions: bool, True
            A flag to indicate if the local session store values within individual apps should be cleared when moving to another app, if set to False, when loading sidebar controls, will be a difference between expected and selected.
        session_params: Dict
            A Dict of parameter name and default values that will be added to the global session store, these parameters will be available to all child applications and they can get/set values from the store during execution.
        
        """
        
        self._apps = {}
        self._nav_pointers = {}
        self._login_app = None
        self._home_app = None
        self._loader_app = LoadingApp()
        self._logout_label = 'Logout 🔒'

        try:
            st.set_page_config(page_title=title,page_icon=favicon,layout=layout,initial_sidebar_state=sidebar_state,)
        except Exception as e:
            print('page config has already been called.\nYou appear to be using a beta container that has already called st.set_page_config.')

        self._nav_horizontal = nav_horizontal

        if nav_container is None:
            self._nav_container = st.beta_container()
        else:
            #hack to stop the beta containers from running set_page_config before HydraApp gets a chance to.
            #if we have a beta_columns container, the instance is delayed until the run() method is called, beta components, who knew!
            if nav_container.__name__ in ['beta_container']:
                self._nav_container = nav_container()
            else:
                self._nav_container = nav_container

        self.cross_session_clear = clear_cross_app_sessions

        if hide_streamlit_markers:
            self._hide_streamlit_markings = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                """
        else:
            self._hide_streamlit_markings = None

        if clear_cross_app_sessions:
            preserve_state = 0
        else:
            preserve_state = 1

        if session_params is None:
            self.session_state = SessionState.get(previous_app=None, selected_app=None, preserve_state=preserve_state, allow_access=0)
        else:
            if isinstance(session_params,Dict):
                self.session_state = SessionState.get(previous_app=None, selected_app=None, preserve_state=preserve_state, allow_access=0,current_user=None,**session_params)


    def add_loader_app(self, loader_app):
        """
        To improve the transition between HydraHeadApps, a loader app is used to quickly clear the window during loading, you can supply a custom loader app, if your include an app that loads a long time to initalise, that is when this app will be seen by the user.
        NOTE: make sure any items displayed are removed once the target app loading is complete, or the items from this app will remain on top of the target app display.

        Parameters
        ------------
        loader_app: HydraHeadApp:`~Hydralit.HydraHeadApp`
            The loader app, this app must implement a modified run method that will receive the target app to be loaded, within the loader run method, the run() method of the target app must be called, or nothing will happen and it will stay in the loader app.
        """

        self._loader_app = loader_app


    def add_app(self, title, app, icon=None, is_login=False, is_home=False, logout_label=None):
        """
        Adds a new application to this HydraApp

        Parameters
        ----------
        title: str
            The title of the app. This is the name that will appear on the menu item for this app.
        app: :HydraHeadApp:`~Hydralit.HydraHeadApp`
            The app class representing the app to include, it must implement inherit from HydraHeadApp classmethod.
        icon: str
            The icon to use on the navigation button, this will be appended to the title to be used on the navigation control.
        is_login: bool, False
            Is this app used to login to the family of apps, this app will provide request response to gateway access to the other apps within the HydraApp.
        is_home: bool, False
            Is this the first 'page' that will be loaded, if a login app is provided, this is the page that will be kicked to upon successful login.

        """
        if icon is None:
            self._nav_pointers[title] = title
        else:
            self._nav_pointers[title] = '{} {}'.format(title, icon)

        if is_login:
            self._login_app = app

            if logout_label is not None:
                self._logout_label = logout_label
        elif is_home:
            self._home_app = title
            self._apps[title] = app
        else:
            self._apps[title] = app
            #grab the first added app as the home is nothing is provided
            if self._home_app is None:
                self._home_app = next(iter(self._apps.keys()))


        self._nav_item_count = int(self._login_app is not None) + len(self._apps.keys())
        app.assign_session(self.session_state)


    def _run_selected(self):
        try:
            if self.session_state.selected_app == None:
                self._loader_app.run(self._apps[self._home_app])
                #self._apps[self._home_app].run()
            else:
                self._loader_app.run(self._apps[self.session_state.selected_app])
                #self._apps[self.session_state.selected_app].run()
        except Exception as e:
            st.error('😭 Error triggered from app: **{}**, someone will be punished for your inconvenience, we humbly request you try again.'.format(self.session_state.selected_app))
            st.error('Details: {}'.format(e))


    def _clear_session_values(self):
        for key in st.session_state:
            del st.session_state[key]

    def _build_nav_menu(self, complex_nav=None):

        if complex_nav is None:
            number_of_sections = self._nav_item_count
        else:
            number_of_sections = int(self._login_app is not None) + len(complex_nav.keys())

        if self._nav_horizontal:
            if hasattr(self._nav_container,'beta_columns'):
                nav_slots = self._nav_container.beta_columns(number_of_sections)
            elif self._nav_container.__name__ in ['beta_columns']:
                nav_slots = self._nav_container(number_of_sections)
            else:
                nav_slots = self._nav_container
        else:
            if self._nav_container.__name__ in ['beta_columns']:
                #columns within columns currently not supported
                nav_slots = st
            else:
                nav_slots = self._nav_container

        #actually build the menu
        if complex_nav is None:
            for i, app_name in enumerate(self._apps.keys()):
                if self._nav_horizontal:
                    nav_section_root = nav_slots[i]
                else:
                    nav_section_root = nav_slots

                if nav_section_root.button(label=self._nav_pointers[app_name]):
                    self.session_state.previous_app = self.session_state.selected_app
                    self.session_state.selected_app = app_name

                    if self.cross_session_clear and self.session_state.previous_app != self.session_state.selected_app and not self.session_state.preserve_state:
                        self._clear_session_values()
        else:
            for i, nav_section_name in enumerate(complex_nav.keys()):
                
                if self._nav_horizontal:
                    nav_section_root = nav_slots[i]
                else:
                    nav_section_root = nav_slots

                if len(complex_nav[nav_section_name]) == 1:
                    nav_section = nav_section_root.beta_container()
                else:
                    nav_section = nav_section_root.beta_expander(label=nav_section_name)

                for nav_item in complex_nav[nav_section_name]:
                    if nav_section.button(label=self._nav_pointers[nav_item]):
                        self.session_state.previous_app = self.session_state.selected_app
                        self.session_state.selected_app = nav_item

                        if self.cross_session_clear and self.session_state.previous_app != self.session_state.selected_app and not self.session_state.preserve_state:
                            self._clear_session_values()      


        #Add logout button and kick to login action
        if self._login_app is not None:
            if self.session_state.current_user is not None:
                self._logout_label = '{} : {}'.format(self.session_state.current_user.capitalize(),self._logout_label)

            if self._nav_horizontal:
                if nav_slots[-1].button(label=self._logout_label):
                    self.session_state.allow_access = 0
                    st.experimental_rerun()
            else:
                if nav_slots.button(label=self._logout_label):
                    self.session_state.allow_access = 0
                    st.experimental_rerun()


    def run(self,complex_nav=None):
        """
        This method is the entry point for the HydraApp, just like a single Streamlit app, you simply setup the additional apps and then call this method to begin.

        Parameters
        ------------
        complex_nav: Dict
            A dictionary that indicates how the nav items should be structured, each key will be a section title and the value will be a list or array of the names of the apps (as registered with the add_app method). The sections with only a single item will be displayed directly, the sections with more than one will be wrapped in an exapnder for cleaner layout.

        """

        #A hack to hide the hamburger button and Streamlit footer
        if self._hide_streamlit_markings is not None:
            st.markdown(self._hide_streamlit_markings, unsafe_allow_html=True)


        if self.session_state.allow_access > 0 or self._login_app is None:
            self._build_nav_menu(complex_nav)

            self._run_selected()
        else:
            self.session_state.current_user = None
            self._login_app.run()


