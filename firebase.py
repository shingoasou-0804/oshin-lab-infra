import json

import pyrebase
import requests
import streamlit as st

from config import firebase as cfg

firebase = pyrebase.initialize_app(cfg)
auth = firebase.auth()


def authenticate_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.user = user
        return True
    except requests.exceptions.HTTPError as e:
        msg = json.loads(e.args[1])["error"]["message"]
        if msg == "EMAIL_NOT_FOUND" or "INVALID_PASSWORD":
            st.error("Invalid email or password")
        elif msg == "USER_DISABLED":
            st.error("Account is disabled")
        elif msg == "TOO_MANY_ATTEMPTS":
            st.error("Too many attempts")
        else:
            st.error("An error occurred")

        if "user" in st.session_state:
            del st.session_state.user
    return False


def refresh_token():
    if "user" not in st.session_state:
        return False
    try:
        user = auth.refresh(st.session_state.user["refreshToken"])
        st.session_state.user = user
        return True
    except Exception:
        del st.session_state.user
    return False
