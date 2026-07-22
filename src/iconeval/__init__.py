"""ICON model output evaluation with ESMValTool."""

import os
import pwd
from importlib.metadata import version

__version__ = version("iconeval")


def get_user_name(uid: int | None = None) -> str:
    """Get user name."""
    # Get the current user's ID if uid is not provided
    if uid is None:
        uid = os.getuid()

    # Try to return user's full name (i.e.., GECOS entry); if that does not
    # work, return user name; and if that fails simply return the user ID
    user_info = pwd.getpwuid(uid)
    try:
        user_name = user_info.pw_gecos.split(",")[0]
    except KeyError:
        try:
            user_name = user_info.pw_name
        except KeyError:
            user_name = f"UID: {uid}"

    return user_name
