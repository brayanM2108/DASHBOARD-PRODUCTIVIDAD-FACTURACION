import streamlit as st


def logout():
    st.session_state.pop("token", None)
    st.session_state.pop("refresh_token", None)
    st.session_state.pop("user", None)
    st.rerun()
