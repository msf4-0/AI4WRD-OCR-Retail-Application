import streamlit as st

class MultiApp:
    def __init__(self):
        # List of seperate pages/applications
        self.apps = []

    def add_app(self, title, func):
        """Adds a new application/page.
        Parameters
        ----------
        func:
            the python function to render this app.
        title:
            title of the app. Appears in the dropdown in the sidebar.
        """
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        # gui element to select the page/application
        app = st.selectbox(
            'Navigation',
            self.apps,
            format_func=lambda app: app['title'])

        app['function']()