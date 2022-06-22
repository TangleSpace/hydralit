from typing import Dict
import streamlit as st
from datetime import datetime, timedelta, timezone
from hydralit.sessionstate import SessionState
from hydralit.loading_app import LoadingApp
import hydralit_components as hc
from hydralit.wrapper_class import Templateapp

class HydraApp(object):
    """
    Class to create a host application for combining multiple streamlit applications.
    """
    
    def __init__(self, 
        title='Hydralit Apps', 
        nav_container=None, 
        nav_horizontal=True,
        layout='wide', 
        favicon = "🧊",
        use_navbar=True,
        navbar_theme=None,
        navbar_sticky=True,
        navbar_mode='pinned',
        use_loader=True,
        use_cookie_cache=True,
        sidebar_state = 'auto',
        navbar_animation=True,
        allow_url_nav=False,
        hide_streamlit_markers = False,
        use_banner_images=None,
        banner_spacing=None, 
        clear_cross_app_sessions=True, 
        session_params=None):
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
        allow_url_nav: bool False
            Enable navigation using url parameters, this allows for bookmarking and using internal links for navigation
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
        use_loader: bool, True
            Set if to use the app loader with auto transition spinners or load directly.
        navbar_animation: bool, False
            Set navbar is menu transitions should be animated.
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
        self._home_label = None
        self._home_id = 'Home'
        self._complex_nav = None
        self._navbar_mode = navbar_mode
        self._navbar_active_index = 0
        self._allow_url_nav = allow_url_nav
        self._navbar_animation = navbar_animation
        self._navbar_sticky = navbar_sticky
        self._nav_item_count = 0
        self._use_navbar = use_navbar
        self._navbar_theme = navbar_theme
        self._banners = use_banner_images
        self._banner_spacing = banner_spacing
        self._hide_streamlit_markers = hide_streamlit_markers
        self._loader_app = LoadingApp()
        self._user_loader = use_loader
        self._use_cookie_cache = use_cookie_cache
        self._cookie_manager = None
        self._logout_label = None
        self._logout_id = 'Logout'
        self._logout_callback = None
        self._login_callback = None
        self._session_attrs = {}
        self._call_queue = []
        self._other_nav = None
        self._guest_name = 'guest'
        self._guest_access = 1
        self._hydralit_url_hash='hYDRALIT|-HaShing==seCr8t'
        self._no_access_level = 0

        self._user_session_params = session_params

        try:
            st.set_page_config(page_title=title,page_icon=favicon,layout=layout,initial_sidebar_state=sidebar_state,)
        except:
            pass

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

        
        if clear_cross_app_sessions:
            preserve_state = 0
        else:
            preserve_state = 1

        if self._user_session_params is None:
            self.session_state = SessionState.get(previous_app=None, selected_app=None,other_nav_app=None, preserve_state=preserve_state, allow_access=self._no_access_level,logged_in=False,access_hash=None)
            self._session_attrs = {'previous_app':None, 'selected_app':None,'other_nav_app':None, 'preserve_state':preserve_state, 'allow_access':self._no_access_level,'logged_in':False,'access_hash':None}
        else:
            if isinstance(self._user_session_params,Dict):
                self.session_state = SessionState.get(previous_app=None, selected_app=None,other_nav_app=None, preserve_state=preserve_state, allow_access=self._no_access_level,logged_in=False,current_user=None,access_hash=None,**(self._user_session_params))
                self._session_attrs = {'previous_app':None, 'selected_app':None,'other_nav_app':None, 'preserve_state':preserve_state, 'allow_access':self._no_access_level,'logged_in':False,'access_hash':None,**(self._user_session_params)}


    # def _encode_hyauth(self):
    #     user_access_level, username = self.check_access()
    #     payload = {"exp": datetime.now(timezone.utc) + timedelta(days=1), "userid": username,"user_level":user_access_level}
    #     return jwt.encode(payload, self._hydralit_url_hash, algorithm="HS256")

    # def _decode_hyauth(self,token):
    #     return jwt.decode(token, self._hydralit_url_hash, algorithms=["HS256"])


    def add_loader_app(self, loader_app):
        """
        To improve the transition between HydraHeadApps, a loader app is used to quickly clear the window during loading, you can supply a custom loader app, if your include an app that loads a long time to initalise, that is when this app will be seen by the user.
        NOTE: make sure any items displayed are removed once the target app loading is complete, or the items from this app will remain on top of the target app display.
        Parameters
        ------------
        loader_app: HydraHeadApp:`~Hydralit.HydraHeadApp`
            The loader app, this app must implement a modified run method that will receive the target app to be loaded, within the loader run method, the run() method of the target app must be called, or nothing will happen and it will stay in the loader app.
        """

        if loader_app:
            self._loader_app = loader_app
            self._user_loader = True
        else:
            self._loader_app = None
            self._user_loader = False


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

        # don't add special apps to list
        if self._use_navbar and not is_login and not is_home:
            self._navbar_pointers[title] = [title,icon]
        
        # if icon is None and not is_login and not is_home:
        #     self._nav_pointers[title] = title
        # else:
        #     self._nav_pointers[title] = '{} {}'.format(icon,title)

        if is_unsecure:
            self._unsecure_app = app

        if is_login:
            self._login_app = app
            self._logout_label = [title,icon]

        elif is_home:
            self._home_app = app
            self._home_label = [title,icon]
        else:
            self._apps[title] = app


        self._nav_item_count = int(self._login_app is not None) + len(self._apps.keys())
        app.assign_session(self.session_state, self)


    def _run_selected(self):
        try:
            if self.session_state.selected_app is None:
                self.session_state.other_nav_app = None
                self.session_state.previous_app = None
                self.session_state.selected_app = self._home_id

                #can disable loader
                if self._user_loader:
                    self._loader_app.run(self._home_app)
                else:
                    self._home_app.run()
                
                #st.experimental_set_query_params(selected=self._home_app)
            else:
                
                if self.session_state.other_nav_app is not None:
                    self.session_state.previous_app = self.session_state.selected_app
                    self.session_state.selected_app = self.session_state.other_nav_app
                    self.session_state.other_nav_app = None

                    if self.session_state.selected_app == self._home_id:
                        if self._user_loader:
                            self._loader_app.run(self._home_app)
                        else:
                            self._home_app.run()
                    else:
                        if self._user_loader:
                            self._loader_app.run(self._apps[self.session_state.selected_app])
                        else:
                            self._apps[self.session_state.selected_app].run()
                else:
                    if self.session_state.selected_app == self._home_id:
                        if self._user_loader:
                            self._loader_app.run(self._home_app)
                        else:
                            self._home_app.run()
                    else:
                        if self._user_loader:
                            self._loader_app.run(self._apps[self.session_state.selected_app])
                        else:
                            self._apps[self.session_state.selected_app].run()
                #st.experimental_set_query_params(selected=self.session_state.selected_app)

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


    def set_access(self,allow_access=0,access_user='', cache_access=False):
        """
        Set the access permission and the assigned username for that access during the current session.
        Parameters
        -----------
        allow_access: int, 0
            Value indicating if access has been granted, can be used to create levels of permission.
        access_user: str, None
            The username the access has been granted to for this session.
        cache_access: bool, False
            Save these access details to a browser cookie so the user will auto login when they visit next time.
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
        #self._delete_cookie_cache()
        if callable(self._logout_callback):
            self._logout_callback()
                                
        st.experimental_rerun()


    def _run_navbar(self, menu_data):

        if hasattr(hc,'__version__'):
            
            if hc.__version__ >= 104:
                login_nav = None
                home_nav = None
                
                if self._login_app:
                    login_nav = {'id': self._logout_id, 'label': self._logout_label[0], 'icon': self._logout_label[1], 'ttip': 'Logout'}
                
                if self._home_app:
                    home_nav = {'id': self._home_id, 'label': self._home_label[0], 'icon': self._home_label[1], 'ttip': 'Home'}
                     
                self.session_state.selected_app = hc.nav_bar(menu_definition=menu_data,key="mainHydralitMenuComplex",home_name=home_nav,override_theme=self._navbar_theme,login_name=login_nav,use_animation=self._navbar_animation,hide_streamlit_markers=self._hide_streamlit_markers)
        else:
            self.session_state.selected_app = hc.nav_bar(menu_definition=menu_data,key="mainHydralitMenuComplex",home_name=self._home_app,override_theme=self._navbar_theme,login_name=self._logout_label)

        # if nav_selected is not None:
        #     if nav_selected != self.session_state.previous_app and self.session_state.selected_app != nav_selected:
        # self.session_state.selected_app = nav_selected

        if self.cross_session_clear and self.session_state.preserve_state:
            self._clear_session_values()


    def _build_nav_menu(self):

        if self._complex_nav is None:
            number_of_sections = self._nav_item_count
        else:
            number_of_sections = int(self._login_app is not None) + len(self._complex_nav.keys())

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
        if self._complex_nav is None:
            if self._use_navbar:
                menu_data = [{'label':self._navbar_pointers[app_name][0],'id':app_name, 'icon': self._navbar_pointers[app_name][1]} for app_name in self._apps.keys()]

                #Add logout button and kick to login action
                if self._login_app is not None:
                    #if self.session_state.current_user is not None:
                    #    self._logout_label = '{} : {}'.format(self.session_state.current_user.capitalize(),self._logout_label)

                    with self._nav_container:
                        self._run_navbar(menu_data)

                    # user clicked logout
                    if self.session_state.selected_app == self._logout_label:
                        self._do_logout()
                else:
                    with self._nav_container:
                        self._run_navbar(menu_data)
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
                    #if self.session_state.current_user is not None:
                    #    self._logout_label = '{} : {}'.format(self.session_state.current_user.capitalize(),self._logout_label)

                    if self._nav_horizontal:
                        if nav_slots[-1].button(label=self._logout_label):
                            self._do_logout()
                    else:
                        if nav_slots.button(label=self._logout_label):
                            self._do_logout()
        else:
            if self._use_navbar:
                menu_data = []
                for i, nav_section_name in enumerate(self._complex_nav.keys()):
                    menu_item = None
                    if nav_section_name not in [self._home_id,self._logout_id]:
                        if len(self._complex_nav[nav_section_name]) == 1:
                            #if (self._complex_nav[nav_section_name][0] != self._home_app and self._complex_nav[nav_section_name][0] != self._logout_label):
                            menu_item = {'label':self._navbar_pointers[self._complex_nav[nav_section_name][0]][0],'id':self._complex_nav[nav_section_name][0], 'icon': self._navbar_pointers[self._complex_nav[nav_section_name][0]][1]}
                        else:
                            submenu_items = []
                            for nav_item in self._complex_nav[nav_section_name]:
                                #if (nav_item != self._home_app and nav_item != self._logout_label):
                                menu_item = {'label':self._navbar_pointers[nav_item][0],'id':nav_item, 'icon': self._navbar_pointers[nav_item][1]}
                                submenu_items.append(menu_item)

                            if len(submenu_items) > 0:
                                menu_item = {'label': nav_section_name,'id':nav_section_name, 'submenu':submenu_items}

                        if menu_item is not None:
                            menu_data.append(menu_item)

                #Add logout button and kick to login action
                if self._login_app is not None:
                    #if self.session_state.current_user is not None:
                    #    self._logout_label = '{} : {}'.format(self.session_state.current_user.capitalize(),self._logout_label)

                    with self._nav_container:
                        self._run_navbar(menu_data)

                    # user clicked logout
                    if self.session_state.selected_app == self._logout_id:
                        self._do_logout()
                else:
                    #self.session_state.previous_app = self.session_state.selected_app
                    with self._nav_container:
                        self._run_navbar(menu_data)

            else:

                for i, nav_section_name in enumerate(self._complex_nav.keys()):
                    if nav_section_name not in [self._home_id,self._logout_id]:
                        if self._nav_horizontal:
                            nav_section_root = nav_slots[i]
                        else:
                            nav_section_root = nav_slots

                        if len(self._complex_nav[nav_section_name]) == 1:
                            nav_section = nav_section_root.container()
                        else:
                            nav_section = nav_section_root.expander(label=nav_section_name,expanded=False)

                        for nav_item in self._complex_nav[nav_section_name]:
                            if nav_section.button(label=self._nav_pointers[nav_item]):
                                self.session_state.previous_app = self.session_state.selected_app
                                self.session_state.selected_app = nav_item
                    
                if self.cross_session_clear and self.session_state.previous_app != self.session_state.selected_app and not self.session_state.preserve_state:
                    self._clear_session_values()   

                #Add logout button and kick to login action
                if self._login_app is not None:
                    #if self.session_state.current_user is not None:
                    #    self._logout_label = '{} : {}'.format(self.session_state.current_user.capitalize(),self._logout_label)

                    if self._nav_horizontal:
                        if nav_slots[-1].button(label=self._logout_label[0]):
                            self._do_logout()
                    else:
                        if nav_slots.button(label=self._logout_label[0]):
                            self._do_logout()


    def _do_url_params(self):
        if self._allow_url_nav:

            query_params = st.experimental_get_query_params()
            if 'selected' in query_params:
                if (query_params['selected'])[0] != 'None' and (query_params['selected'])[0] != self.session_state.selected_app: # and (query_params['selected'])[0] != self.session_state.previous_app:
                    self.session_state.other_nav_app = (query_params['selected'])[0]


    def enable_guest_access(self, guest_access_level=1, guest_username='guest'):
        """
        This method will auto login a guest user when the app is secured with a login app, this will allow fora guest user to by-pass the login app and gain access to the other apps that the assigned access level will allow.

        ------------
        guest_access_level: int, 1
            Set the access level to assign to an auto logged in guest user.
        guest_username: str, guest
            Set the username to assign to an auto logged in guest user.
        """

        user_access_level, username = self.check_access()
        if user_access_level == 0 and username is None:
            self.set_access(guest_access_level, guest_username)


    # def get_cookie_manager(self):
    #     if self._use_cookie_cache and self._cookie_manager is not None:
    #         return self._cookie_manager
    #     else:
    #         return None

    # def _delete_cookie_cache(self):
    #     if self._use_cookie_cache and self._cookie_manager is not None:
    #         username_cache = self._cookie_manager.get('hyusername')
    #         accesslevel_cache = self._cookie_manager.get('hyaccesslevel')

    #         if username_cache is not None:
    #             self._cookie_manager.delete('hyusername')

    #         if accesslevel_cache is not None:
    #             self._cookie_manager.delete('hyaccesslevel')


    # def _write_cookie_cache(self,hyaccesslevel,hyusername):
    #     if self._use_cookie_cache and self._cookie_manager is not None:
    #         if hyaccesslevel is not None and hyusername is not None:
    #             self._cookie_manager.set('hyusername',hyusername)
    #             self._cookie_manager.set('hyaccesslevel',hyaccesslevel)


    # def _read_cookie_cache(self):
    #     if self._use_cookie_cache and self._cookie_manager is not None:
    #         username_cache = self._cookie_manager.get('hyusername')
    #         accesslevel_cache = self._cookie_manager.get('hyaccesslevel')

    #         if username_cache is not None and accesslevel_cache is not None:
    #             self.set_access(int(accesslevel_cache), str(username_cache))


    def run(self,complex_nav=None):
        """
        This method is the entry point for the HydraApp, just like a single Streamlit app, you simply setup the additional apps and then call this method to begin.
        Parameters
        ------------
        complex_nav: Dict
            A dictionary that indicates how the nav items should be structured, each key will be a section title and the value will be a list or array of the names of the apps (as registered with the add_app method). The sections with only a single item will be displayed directly, the sections with more than one will be wrapped in an exapnder for cleaner layout.
        """
        #process url navigation parameters
        #self._do_url_params()

        self._complex_nav = complex_nav
        #A hack to hide the hamburger button and Streamlit footer
        #if self._hide_streamlit_markings is not None:
        #    st.markdown(self._hide_streamlit_markings, unsafe_allow_html=True)

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

            if self._nav_item_count == 0:
                self._default()
            else:
                self._build_nav_menu()
                self._run_selected()
        elif self.session_state.allow_access < self._no_access_level:
            self.session_state.current_user = self._guest_name
            self._unsecure_app.run()
        else:
            self.session_state.logged_in = False
            self.session_state.current_user = None
            self.session_state.access_hash = None
            self._login_app.run()


    def _default(self):
        st.header('Welcome to Hydralit')
        st.write('Thank you for your enthusiasum and looking to run the HydraApp as quickly as possible, for maximum effect, please add a child app by one of the methods below.')

        st.write('For more information, please see the instructions on the home page [Hydralit Home Page](https://github.com/TangleSpace/hydralit)')

        st.write('Method 1 (easiest)')

        st.code("""
#when we import hydralit, we automatically get all of Streamlit
import hydralit as hy

app = hy.HydraApp(title='Simple Multi-Page App')

@app.addapp()
def my_cool_function():
  hy.info('Hello from app 1')
        """
        )

        st.write('Method 2 (more fun)')

        st.code("""
from hydralit import HydraHeadApp
import streamlit as st


#create a child app wrapped in a class with all your code inside the run() method.
class CoolApp(HydraHeadApp):

    def run(self):
        st.info('Hello from cool app 1')



#when we import hydralit, we automatically get all of Streamlit
import hydralit as hy

app = hy.HydraApp(title='Simple Multi-Page App')

app.add_app("My Cool App", icon="📚", app=CoolApp(title="Cool App"))
        """
        )

        st.write('Once we have added atleast one child application, we just run the parent app!')

        st.code("""
app.run()
        """)


        st.write('For example you get can going super quick with a couple of functions and a call to Hydralit App run().')

        st.code("""
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
        """)

    def logout_callback(self,func):
        """
        This is a decorate to add a function to be run when a user is logged out.

        """

        def my_wrap(*args, **kwargs):
            return func(*args, **kwargs)

        self._logout_callback = my_wrap
        return my_wrap


    def login_callback(self,func):
        """
        This is a decorate to add a function to be run when a user is first logged in.

        """

        def my_wrap(*args, **kwargs):
            return func(*args, **kwargs)

        self._login_callback = my_wrap
        return my_wrap



    def addapp(self,title=None,icon=None, is_home=False):
        """
        This is a decorator to quickly add a function as a child app in a style like a Flask route.

        You can do everything you can normally do when adding a class based HydraApp to the parent, except you can not add a login or unsecure app using this method, as
        those types of apps require functions provided from inheriting from HydraAppTemplate.

        Parameters
        ----------
        title: str
            The title of the app. This is the name that will appear on the menu item for this app.
        icon: str
            The icon to use on the navigation button, this will be appended to the title to be used on the navigation control.
        is_home: bool, False
            Is this the first 'page' that will be loaded, if a login app is provided, this is the page that will be kicked to upon successful login.
        """
       
        def decorator(func):

            wrapped_app = Templateapp(mtitle=title,run_method=func)
            app_title = wrapped_app.title
            app_icon = icon

            if is_home and title is None and icon is None:
                app_title = None
                app_icon = "fa fa-home"
            
            self.add_app(title=app_title,app=wrapped_app,icon=app_icon, is_home=is_home)


            return func

        return decorator
