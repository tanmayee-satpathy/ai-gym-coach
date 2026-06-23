import hashlib
import hmac
import os

import streamlit as st

from services.persistence.exercise_repository import create_user, get_user, set_user_password


def _normalize_username(username: str) -> str:
    return username.strip().lower()


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"{salt.hex()}:{digest.hex()}"


def _verify_password(password: str, stored_hash: str | None) -> bool:
    if not stored_hash or ":" not in stored_hash:
        return False

    salt_hex, digest_hex = stored_hash.split(":", 1)
    expected = bytes.fromhex(digest_hex)
    actual = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        120_000,
    )
    return hmac.compare_digest(actual, expected)


def _start_session(user) -> None:
    st.session_state["user_id"] = user["id"]
    st.session_state["username"] = user["username"]
    st.session_state["display_name"] = user["display_name"] or user["username"]
    st.rerun()


def _render_auth_hero() -> None:
    st.markdown(
        """
        <section class="auth-snap-hero">
            <div class="auth-snap-pill">Welcome to AI Gym Coach</div>
            <h1>AI Powered<br><span>Fitness Coach</span></h1>
            <p>
                Real-time pose detection, rep counting, workout history, and
                voice coaching in one clean training dashboard.
            </p>
            <div class="auth-snap-actions">
                <span>Live form tracking</span>
                <span>Personal progress</span>
                <span>Voice feedback</span>
            </div>
            <div class="auth-snap-orb auth-snap-orb--one"></div>
            <div class="auth-snap-orb auth-snap-orb--two"></div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_auth_card_header() -> None:
    st.markdown(
        """
        <div class="auth-snap-card-heading">
            <h2>Start your training</h2>
            <p>Log in or create your account to continue.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _set_auth_mode(mode: str) -> None:
    st.session_state["auth_mode"] = mode


def _render_auth_mode_buttons() -> str:
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "Log In"

    st.markdown(
        f"""
        <div class="auth-mode-state auth-mode-state--{st.session_state["auth_mode"].lower().replace(" ", "-")}"></div>
        """,
        unsafe_allow_html=True,
    )

    login_col, signup_col = st.columns(2, gap="small")

    with login_col:
        st.button(
            "Log In",
            key="auth_mode_login_button",
            width="stretch",
            on_click=_set_auth_mode,
            args=("Log In",),
        )

    with signup_col:
        st.button(
            "Sign Up",
            key="auth_mode_signup_button",
            width="stretch",
            on_click=_set_auth_mode,
            args=("Sign Up",),
        )

    return st.session_state["auth_mode"]


def _render_auth_card_open() -> None:
    st.markdown(
        """
        <div class="auth-snap-card-bg"></div>
        """,
        unsafe_allow_html=True,
    )


def _render_auth_card_close() -> None:
    return None


def _render_mobile_brand() -> None:
    st.markdown(
        """
        <div class="auth-mobile-brand">
            <span>AI Gym Coach</span>
            <strong>Train smarter today.</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_auth_shell_open() -> None:
    return None


def _render_login_form() -> None:
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="your username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="your password", key="login_password")
        submit_button = st.form_submit_button("Log In", width="stretch")

    if not submit_button:
        return

    username = _normalize_username(username)

    if not username or not password:
        st.error("Enter both username and password.")
        return

    user = get_user(username)

    if user is None:
        st.error("No account found with that username. Create one in Sign Up.")
        return

    if not user["password_hash"]:
        user = set_user_password(username, _hash_password(password))
        st.success("Password added to your existing account. Signing you in...")
        _start_session(user)
        return

    if not _verify_password(password, user["password_hash"]):
        st.error("That password does not match this account.")
        return

    _start_session(user)


def _render_signup_form() -> None:
    with st.form("signup_form", clear_on_submit=False):
        display_name = st.text_input("Display name", placeholder="e.g: Tanmayee", key="signup_display_name")
        username = st.text_input("Username", placeholder="e.g: tanmayee26", key="signup_username")
        password = st.text_input("Password", type="password", placeholder="At least 6 characters", key="signup_password")
        confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm_password")
        submit_button = st.form_submit_button("Create Account", width="stretch")

    if not submit_button:
        return

    username = _normalize_username(username)
    display_name = display_name.strip()

    if not display_name or not username or not password or not confirm_password:
        st.error("Fill all fields to create your account.")
        return

    if len(username) < 3:
        st.error("Username must be at least 3 characters.")
        return

    if len(password) < 6:
        st.error("Password must be at least 6 characters.")
        return

    if password != confirm_password:
        st.error("Passwords do not match.")
        return

    if get_user(username) is not None:
        st.error("That username is already taken. Try logging in instead.")
        return

    user = create_user(username, _hash_password(password), display_name)
    st.success("Account created. Taking you to your dashboard...")
    _start_session(user)


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True

    st.markdown('<div class="auth-page-marker"></div>', unsafe_allow_html=True)
    _render_auth_shell_open()
    _render_mobile_brand()
    hero_col, form_col = st.columns([1.05, 0.95], gap="large")

    with hero_col:
        _render_auth_hero()

    with form_col:
        _render_auth_card_open()
        _render_auth_card_header()
        auth_mode = _render_auth_mode_buttons()

        if auth_mode == "Log In":
            _render_login_form()
        else:
            _render_signup_form()

        _render_auth_card_close()

    return False
