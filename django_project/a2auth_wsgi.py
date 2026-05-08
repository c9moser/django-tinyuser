#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Apache mod_wsgi authentication handler for Django.

Integrates Django's session-based authentication with Apache's form-based auth.
Validates users against Django's session cache rather than password file.
"""

import sys
import os
from pathlib import Path

print("Starting Apache mod_wsgi authentication handler for Django", file=sys.stderr)
from .env import ENV  # noqa: E402

APACHE_AUTH_KEY = u"RestrictedAccess"
APACHE_USER_KEY = u"user"
APACHE_PASS_KEY = u"pw"

# Add the project directory and virtualenv site-packages to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
venv_dir = ENV("VENV_DIR")
if venv_dir and Path(venv_dir).is_dir():
    sys.path.insert(0, str(Path(venv_dir) / "lib" / "python" / f"{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"))
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module environment variable before importing Django
os.environ['DJANGO_SETTINGS_MODULE'] = ENV('DJANGO_SETTINGS_MODULE')

# Import and setup Django
import django  # noqa: E402
django.setup()


def __get_apache_keys_(environ):
    user_key = APACHE_USER_KEY
    pw_key = APACHE_PASS_KEY
    if APACHE_AUTH_KEY in environ:
        authname = environ[APACHE_AUTH_KEY]
        if authname is not None:
            user_key = authname + u"-" + user_key
            pw_key = authname + u"-" + pw_key

    return (user_key, pw_key)


def __get_session_id_(environ):
    from django.conf import settings
    from django.http import parse_cookie

    if u"HTTP_COOKIE" in environ:
        cookies = parse_cookie(environ[u"HTTP_COOKIE"])
        if settings.SESSION_COOKIE_NAME in cookies:
            return cookies[settings.SESSION_COOKIE_NAME]


def __get_session_(environ):
    """Retrieve Django session object from database."""
    from django.contrib.sessions.models import Session

    session_id = __get_session_id_(environ)
    if session_id is not None:
        try:
            return Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            pass
    return None


def __encode_data_(data):
    from importlib import import_module
    from django.conf import settings

    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
    s = SessionStore()
    return s.encode(data)


def __decode_data_(data):
    from importlib import import_module
    from django.conf import settings

    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
    s = SessionStore()
    return s.decode(data)


def check_password(environ, username, password):
    """
    Validate user credentials against Django session.

    Returns True if user has active Django session, False otherwise.
    Apache passes username and password; we verify the session exists.
    """
    print(f"Checking password for user: {username}", file=sys.stderr)

    s = __get_session_(environ)
    if s is None:
        return False

    try:
        session_data = s.get_decoded()
    except Exception:
        return False

    if not session_data:
        return False

    from django.contrib.auth import SESSION_KEY
    if SESSION_KEY in session_data and session_data[SESSION_KEY] is not None:
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(pk=session_data[SESSION_KEY])
            # Verify username matches
            if user.get_username() == username:
                return True
        except UserModel.DoesNotExist:
            pass

    return False


def load_session(environ):
    s = __get_session_(environ)
    if s is not None:
        return s.session_data


def decode_session(environ, data):
    """
    Decode session data and convert to bytes for Apache.

    Injects current username into session data if user is authenticated.
    """
    session_data = __decode_data_(data) if data else {}

    (user_key, pw_key) = __get_apache_keys_(environ)
    if user_key not in session_data:
        from django.contrib.auth import SESSION_KEY
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()

        user = None
        if SESSION_KEY in session_data:
            uid = session_data[SESSION_KEY]
            if uid is not None:
                try:
                    user = UserModel.objects.get(pk=uid)
                except UserModel.DoesNotExist:
                    pass

        if user is not None:
            session_data[user_key] = user.get_username()
            if pw_key not in session_data:
                session_data[pw_key] = u"<fake>"

    # Convert to bytes for Apache
    return {k.encode(u"utf-8"): v.encode(u"utf-8")
            for (k, v) in session_data.items()}


def encode_session(environ, data):
    """
    Encode session data back to Django format.

    Removes Apache auth keys before storing in session.
    """
    (user_key, pw_key) = __get_apache_keys_(environ)
    if user_key in data:
        del data[user_key]
    if pw_key in data:
        del data[pw_key]

    s = __get_session_(environ)
    if s is None:
        return None

    try:
        session_data = __decode_data_(s.session_data)
    except Exception:
        return None

    for key in data:
        if not key.startswith(u"_"):
            session_data[key] = data[key]

    return __encode_data_(session_data)


def save_session(environ, data):
    s = __get_session_(environ)
    if s is not None:
        s.session_data = data
        s.save()
        return True

    return False


# Required: groups_for_user function for Apache mod_wsgi
from django.contrib.auth.handlers.modwsgi import groups_for_user  # noqa: F401, E402
