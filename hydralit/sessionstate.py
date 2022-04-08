import streamlit
st_ver = int(streamlit.__version__.replace('.',''))

if st_ver < 140:
    import streamlit.report_thread as ReportThread
elif st_ver < 180:
    from streamlit.script_run_context import get_script_run_ctx
else:
    from streamlit.scriptrunner.script_run_context import get_script_run_ctx
from streamlit.server.server import Server
    

#All credit goes to TVST https://gist.github.com/tvst/036da038ab3e999a64497f42de966a92 for this very good sessionstate class implementation

class SessionState(object):

    def __init__(self, **kwargs):
        """
        
        A new SessionState object.

        Parameters
        ----------
        **kwargs : any
            Default values for the session state.

        Example
        -------
        >>> session_state = SessionState(user_name='', favorite_color='black')
        >>> session_state.user_name = 'Mary'
        ''
        >>> session_state.favorite_color
        'black'

        """
        for key, val in kwargs.items():
            setattr(self, key, val)


    def get(**kwargs):
        """
        
        Gets a SessionState object for the current session.
        Creates a new object if necessary.

        Parameters
        ----------
        **kwargs : any
            Default values you want to add to the session state, if we're creating a
            new one.

        Example
        -------
        >>> session_state = get(user_name='', favorite_color='black')
        >>> session_state.user_name
        ''
        >>> session_state.user_name = 'Mary'
        >>> session_state.favorite_color
        'black'
        Since you set user_name above, next time your script runs this will be the
        result:
        >>> session_state = get(user_name='', favorite_color='black')
        >>> session_state.user_name
        'Mary'
        """

        if st_ver < 140:
            session_id = ReportThread.get_report_ctx().session_id
        else:
            session_id = get_script_run_ctx().session_id

        # Hack to get the session object from Streamlit.
        #session_id = self._get_session_id()
        session_info = Server.get_current()._get_session_info(session_id)

        if session_info is None:
            raise RuntimeError('Could not get Streamlit session object.')

        this_session = session_info.session

        # Got the session object! Now let's attach some state into it.

        if not hasattr(this_session, '_custom_session_state'):
            this_session._custom_session_state = SessionState(**kwargs)

        return this_session._custom_session_state


