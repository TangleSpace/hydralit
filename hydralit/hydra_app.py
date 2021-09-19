from typing import Dict
import streamlit as st
from hydralit.sessionstate import SessionState
from hydralit.loading_app import LoadingApp
from hydralit_components import nav_bar

class HydraApp(object):
    """
    Class to create a host application for combining multiple streamlit applications.
    """
    
    def __init__(self, title='Streamlit MultiApp', nav_container=None, nav_horizontal=True,layout='wide', favicon = "🧊",use_navbar=True,navbar_theme=None,navbar_sticky=True,sidebar_state = 'auto', hide_streamlit_markers = False,use_banner_images=None,banner_spacing=None, clear_cross_app_sessions=True, session_params=None):
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
        use_navbar: bool, False
            Use the Hydralit Navbar component or internal Streamlit components to create the nav menu. Currently Hydralit Navbar doesn't support dropdown menus.
        navbar_theme: Dict, None
            Override the Hydralit Navbar theme, you can overrider only the part you wish or the entire theme by only providing details of the changes.
             - txc_inactive: Inactive Menu Item Text color
             - menu_background: Menu Background Color
             - txc_active: Active Menu Item Text Color
             - option_active: Active Menu Item Color            
            example, navbar_theme = {'txc_inactive': '#FFFFFF','menu_background':'red','txc_active':'yellow','option_active':'blue'}
        navbar_sticky: bool, True
            Set navbar to be sticky and fixed to the top of the window.
        sidebar_state: str, 'auto'
            The starting state of the sidebase, same as variable used in `set_page_config <https://docs.streamlit.io/en/stable/api.html?highlight=set_page_config#streamlit.set_page_config>`.
        hide_streamlit_markers: bool, False
            A flag to hide the default Streamlit menu hamburger button and the footer watermark.
        use_banner_images: str or Array, None
            A path to the image file to use as a banner above the menu or an array of paths to use multiple images spaced using the rations from the banner_spacing parameter.
        banner_spacing: Array, None
            An array to specify the alignment of the banner images, this is the same as the array spec used by Streamlit Columns, if you want centered with 20% padding either side -> banner_spacing =[20,60,20]
        clear_cross_app_sessions: bool, True
            A flag to indicate if the local session store values within individual apps should be cleared when moving to another app, if set to False, when loading sidebar controls, will be a difference between expected and selected.
        session_params: Dict
            A Dict of parameter name and default values that will be added to the global session store, these parameters will be available to all child applications and they can get/set values from the store during execution.
        
        """
        
        self._apps = {}
        self._nav_pointers = {}
        self._navbar_pointers = {}
        self._login_app = None
        self._unsecure_app = None
        self._home_app = None
        self._navbar_sticky = navbar_sticky
        self._use_navbar = use_navbar
        self._navbar_theme = navbar_theme
        self._banners = use_banner_images
        self._banner_spacing = banner_spacing
        self._loader_app = LoadingApp()
        self._logout_label = None
        self._logout_callback = None
        self._login_callback = None
        self._session_attrs = {}
        self._guest_name = 'guest'
        self._no_access_level = 0

        self._user_session_params = session_params

        try:
            st.set_page_config(page_title=title,page_icon=favicon,layout=layout,initial_sidebar_state=sidebar_state,)
        except Exception as e:
            print('page config has already been called.\nYou appear to be using a container that has already called st.set_page_config.')

        self._nav_horizontal = nav_horizontal

        if self._banners is not None:
            self._banner_container = st.container()

        if nav_container is None:
            self._nav_container = st.container()
        else:
            #hack to stop the beta containers from running set_page_config before HydraApp gets a chance to.
            #if we have a beta_columns container, the instance is delayed until the run() method is called, beta components, who knew!
            if nav_container.__name__ in ['container']:
                self._nav_container = nav_container()
            else:
                self._nav_container = nav_container

        self.cross_session_clear = clear_cross_app_sessions

        if hide_streamlit_markers:
            self._hide_streamlit_markings = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
            """
        else:
            self._hide_streamlit_markings = None

        if clear_cross_app_sessions:
            preserve_state = 0
        else:
            preserve_state = 1

        if self._user_session_params is None:
            self.session_state = SessionState.get(previous_app=None, selected_app=None,other_nav_app=None, preserve_state=preserve_state, allow_access=self._no_access_level,logged_in=False)
            self._session_attrs = {'previous_app':None, 'selected_app':None,'other_nav_app':None, 'preserve_state':preserve_state, 'allow_access':self._no_access_level,'logged_in':False}
        else:
            if isinstance(self._user_session_params,Dict):
                self.session_state = SessionState.get(previous_app=None, selected_app=None,other_nav_app=None, preserve_state=preserve_state, allow_access=self._no_access_level,logged_in=False,current_user=None,**(self._user_session_params))
                self._session_attrs = {'previous_app':None, 'selected_app':None,'other_nav_app':None, 'preserve_state':preserve_state, 'allow_access':self._no_access_level,'logged_in':False,**(self._user_session_params)}


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


    def add_app(self, title, app, icon=None, is_login=False, is_home=False, logout_label=None, is_unsecure=False):
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
        is_unsecure: bool, False
            An app that can be run other than the login if using security, this is typically a sign-up app that can be run and then kick back to the login.
        """
        if self._use_navbar:
            self._navbar_pointers[title] = [title,icon]
        
        if icon is None:
            self._nav_pointers[title] = title
        else:
            self._nav_pointers[title] = '{} {}'.format(icon,title)

        if is_unsecure:
            self._unsecure_app = app

        if is_login:
            self._login_app = app

            if logout_label is not None:
                self._logout_label = logout_label
            else:
                self._logout_label = 'Logout 🔒'
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
                self.session_state.other_nav_app = None
                self.session_state.previous_app = None
                self.session_state.selected_app = self._home_app
                self._loader_app.run(self._apps[self._home_app])
            else:
                if self.session_state.other_nav_app == None:
                    self._loader_app.run(self._apps[self.session_state.selected_app])
                else:
                    self.session_state.previous_app = self.session_state.selected_app
                    self.session_state.selected_app = self.session_state.other_nav_app
                    self.session_state.other_nav_app = None
                    self._loader_app.run(self._apps[self.session_state.selected_app])

        except Exception as e:
            st.error('😭 Error triggered from app: **{}**'.format(self.session_state.selected_app))
            st.error('Details: {}'.format(e))


    def _clear_session_values(self):
        for key in st.session_state:
            del st.session_state[key]

    def set_guest(self,guest_name):
        """
        Set the name to be used for guest access.

        Parameters
        -----------
        guest_name: str
            The value to use when allowing guest logins.
        """

        if guest_name is not None:
            self._guest_name = guest_name


    def set_noaccess_level(self,no_access_level:int):
        """
        Set the access level integer value to be used to indicate no access, default is zero.

        Parameters
        -----------
        no_access_level: int
            The value to use to block access, all other values will have some level of access
        """

        if no_access_level is not None:
            self._no_access_level = int(no_access_level)


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
        username = None

        if hasattr(self.session_state,'current_user'):
            username = str(self.session_state.current_user)

        return int(self.session_state.allow_access), username


    def get_nav_transition(self):
        """
        Check the previous and current app names the user has navigated between

        Returns
        ---------
        tuple: previous_app, current_app

        """

        return str(self.session_state.previous_app),str(self.session_state.selected_app)


    def get_user_session_params(self):
        """
        Return a dictionary of the keys and current values of the user defined session parameters.

        Returns
        ---------
        dict

        """
        user_session_params = {}

        if self._user_session_params is not None:
            for k in self._user_session_params.keys():
                if hasattr(self.session_state,k):
                    user_session_params[k] = getattr(self.session_state,k)

        return user_session_params


    def _do_logout(self):
        self.session_state.allow_access = self._no_access_level
        self._logged_in = False
        if callable(self._logout_callback):
            self._logout_callback()
                                
        st.experimental_rerun()


    def _build_nav_menu(self, complex_nav=None):

        if complex_nav is None:
            number_of_sections = self._nav_item_count
        else:
            number_of_sections = int(self._login_app is not None) + len(complex_nav.keys())

        if self._nav_horizontal:
            if hasattr(self._nav_container,'columns'):
                nav_slots = self._nav_container.columns(number_of_sections)
            elif self._nav_container.__name__ in ['columns']:
                nav_slots = self._nav_container(number_of_sections)
            else:
                nav_slots = self._nav_container
        else:
            if self._nav_container.__name__ in ['columns']:
                #columns within columns currently not supported
                nav_slots = st
            else:
                nav_slots = self._nav_container

        #actually build the menu
        if complex_nav is None:
            if self._use_navbar:
                menu_data = [{'label':self._navbar_pointers[app_name][0],'id':app_name, 'icon': self._navbar_pointers[app_name][1]} for app_name in self._apps.keys() if (app_name != self._home_app and app_name != self._logout_label)]

                #Add logout button and kick to login action
                if self._login_app is not None:
                    if self.session_state.current_user is not None:
                        self._logout_label = '{} : {}'.format(self.session_state.current_user.capitalize(),self._logout_label)

                    with self._nav_container:
                        self.session_state.previous_app = self.session_state.selected_app
                        nav_selected = nav_bar(menu_definition=menu_data,key="mainHydralitMenu",home_name=self._home_app,override_theme=self._navbar_theme,login_name=self._logout_label,sticky_nav=self._navbar_sticky)

                        if self.session_state.other_nav_app == None or not hasattr(self.session_state,'other_nav_app'):
                            self.session_state.selected_app = nav_selected

                        if self.cross_session_clear and self.session_state.previous_app != self.session_state.selected_app and not self.session_state.preserve_state:
                            self._clear_session_values()

                    # user clicked logout
                    if self.session_state.selected_app == self._logout_label:
                        self._do_logout()
                else:
                    self.session_state.previous_app = self.session_state.selected_app
                    if self.cross_session_clear and self.session_state.previous_app != self.session_state.selected_app and not self.session_state.preserve_state:
                        self._clear_session_values()

                    with self._nav_container:
                        nav_selected = nav_bar(menu_definition=menu_data,key="mainHydralitMenucont",home_name=self._home_app,override_theme=self._navbar_theme,login_name=self._logout_label,sticky_nav=self._navbar_sticky)

                        if self.session_state.other_nav_app == None or not hasattr(self.session_state,'other_nav_app'):                           
                            self.session_state.selected_app = nav_selected

                        if self.cross_session_clear and self.session_state.previous_app != self.session_state.selected_app and not self.session_state.preserve_state:
                            self._clear_session_values()
            else:
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

                #Add logout button and kick to login action
                if self._login_app is not None:
                    if self.session_state.current_user is not None:
                        self._logout_label = '{} : {}'.format(self.session_state.current_user.capitalize(),self._logout_label)

                    if self._nav_horizontal:
                        if nav_slots[-1].button(label=self._logout_label):
                            self._do_logout()
                    else:
                        if nav_slots.button(label=self._logout_label):
                            self._do_logout()
        else:
            if self._use_navbar:
                menu_data = []
                for i, nav_section_name in enumerate(complex_nav.keys()):
                    menu_item = None
                    if len(complex_nav[nav_section_name]) == 1:
                        if (complex_nav[nav_section_name][0] != self._home_app and complex_nav[nav_section_name][0] != self._logout_label):
                            menu_item = {'label':self._navbar_pointers[complex_nav[nav_section_name][0]][0],'id':complex_nav[nav_section_name][0], 'icon': self._navbar_pointers[complex_nav[nav_section_name][0]][1]}
                    else:
                        submenu_items = []
                        for nav_item in complex_nav[nav_section_name]:
                            if (nav_item != self._home_app and nav_item != self._logout_label):
                                menu_item = {'label':self._navbar_pointers[nav_item][0],'id':nav_item, 'icon': self._navbar_pointers[nav_item][1]}
                                submenu_items.append(menu_item)

                        if len(submenu_items) > 0:
                            menu_item = {'label': nav_section_name,'id':nav_section_name, 'submenu':submenu_items}

                    if menu_item is not None:
                        menu_data.append(menu_item)

                #Add logout button and kick to login action
                if self._login_app is not None:
                    if self.session_state.current_user is not None:
                        self._logout_label = '{} : {}'.format(self.session_state.current_user.capitalize(),self._logout_label)

                    with self._nav_container:
                        self.session_state.previous_app = self.session_state.selected_app
                        nav_selected = nav_bar(menu_definition=menu_data,key="mainHydralitMenuComplex",home_name=self._home_app,override_theme=self._navbar_theme,login_name=self._logout_label,sticky_nav=self._navbar_sticky)
                        if self.session_state.other_nav_app == None or not hasattr(self.session_state,'other_nav_app'):
                            self.session_state.selected_app = nav_selected
                            
                        if self.cross_session_clear and self.session_state.previous_app != self.session_state.selected_app and not self.session_state.preserve_state:
                            self._clear_session_values()

                    # user clicked logout
                    if self.session_state.selected_app == self._logout_label:
                        self._do_logout()
                else:
                    self.session_state.previous_app = self.session_state.selected_app
                    if self.cross_session_clear and self.session_state.previous_app != self.session_state.selected_app and not self.session_state.preserve_state:
                        self._clear_session_values()

                    with self._nav_container:
                        nav_selected = nav_bar(menu_definition=menu_data,key="mainHydralitMenuComplexcont",home_name=self._home_app,override_theme=self._navbar_theme,login_name=self._logout_label,sticky_nav=self._navbar_sticky)
                        if self.session_state.other_nav_app == None or not hasattr(self.session_state,'other_nav_app'):
                            self.session_state.selected_app = nav_selected
                        else:
                            self._run_selected()
                            
                        if self.cross_session_clear and self.session_state.previous_app != self.session_state.selected_app and not self.session_state.preserve_state:
                            self._clear_session_values()
            else:
                if 'Home' not in complex_nav and not self._home_app is None:
                    complex_nav = {'Home': ['Home'], **complex_nav}

                for i, nav_section_name in enumerate(complex_nav.keys()):
                    
                    if self._nav_horizontal:
                        nav_section_root = nav_slots[i]
                    else:
                        nav_section_root = nav_slots

                    if len(complex_nav[nav_section_name]) == 1:
                        nav_section = nav_section_root.container()
                    else:
                        nav_section = nav_section_root.expander(label=nav_section_name,expanded=False)

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
                            self._do_logout()
                    else:
                        if nav_slots.button(label=self._logout_label):
                            self._do_logout()


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

        if self._banners is not None:
            if isinstance(self._banners,str):
                self._banners = [self._banners]

            if self._banner_spacing is not None and len(self._banner_spacing) == len(self._banners):
                    cols= self._banner_container.columns(self._banner_spacing)
                    for idx, im in enumerate(self._banners):
                        if im is not None:
                            if isinstance(im,Dict):
                                cols[idx].markdown(next(iter(im.values())),unsafe_allow_html=True)
                            else:
                                cols[idx].image(im)
            else:
                if self._banner_spacing is not None and len(self._banner_spacing) != len(self._banners):
                    print('WARNING: Banner spacing spec is a different length to the number of banners supplied, using even spacing for each banner.')

                cols= self._banner_container.columns([1]*len(self._banners))
                for idx, im in enumerate(self._banners):
                    if im is not None:
                        if isinstance(im,Dict):
                            cols[idx].markdown(next(iter(im.values())),unsafe_allow_html=True)
                        else:
                            cols[idx].image(im)


        if self.session_state.allow_access > self._no_access_level or self._login_app is None:
            if callable(self._login_callback):
                if not self.session_state.logged_in:
                    self.session_state.logged_in = True
                    self._login_callback()

            self._build_nav_menu(complex_nav)
            self._run_selected()
        elif self.session_state.allow_access < self._no_access_level:
            self.session_state.current_user = self._guest_name
            self._unsecure_app.run()
        else:
            self.session_state.logged_in = False
            self.session_state.current_user = None
            self._login_app.run()


    def logout_callback(self,func):
        def my_wrap(*args, **kwargs):
            return func(*args, **kwargs)

        self._logout_callback = my_wrap
        return my_wrap


    def login_callback(self,func):
        def my_wrap(*args, **kwargs):
            return func(*args, **kwargs)

        self._login_callback = my_wrap
        return my_wrap

