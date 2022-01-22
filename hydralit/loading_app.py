import streamlit as st
from hydralit_components import HyLoader, Loaders
from hydralit.app_template import HydraHeadApp


class LoadingApp(HydraHeadApp):

    def run(self,app_target):

        try:
            app_title = ''
            if hasattr(app_target,'title'):
                app_title = app_target.title

            with HyLoader("Now loading {}".format(app_title), loader_name=Loaders.standard_loaders,index=[3,0,5]):
                app_target.run()
      
        except Exception as e:
            raise e

