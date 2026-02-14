from __future__ import annotations

import os

import streamlit as st


def _expected_admin_password() -> str:
    try:
        secret_value = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        secret_value = None
    value = secret_value or os.getenv("ADMIN_PASSWORD")
    return str(value) if value else "admin123"


def is_admin() -> bool:
    return bool(st.session_state.get("is_admin"))


def render_sidebar_auth() -> None:
    with st.sidebar:
        st.markdown("### Admin Access")
        if is_admin():
            st.success("Admin session active")
            if st.button("Logout", width="stretch"):
                st.session_state["is_admin"] = False
                st.rerun()
            return

        password = st.text_input("Password", type="password", key="admin_password")
        if st.button("Login", type="primary", width="stretch"):
            if password == _expected_admin_password():
                st.session_state["is_admin"] = True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid password")


def require_admin() -> None:
    if is_admin():
        return
    st.warning("Admin page is protected. Use the sidebar to sign in.")
    st.stop()
