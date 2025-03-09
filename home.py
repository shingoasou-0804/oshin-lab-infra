import streamlit as st

import firebase


def login():
    email = st.empty()
    email = email.text_input("Email")
    password = st.text_input("Password", type="password")
    submit = st.button("Login")
    if submit and firebase.authenticate_user(email, password):
        st.rerun()


def index():
    if not firebase.refresh_token():
        st.rerun()
        return

    st.text("Welcome to the labo app")


if "user" not in st.session_state:
    login()
else:
    index()
