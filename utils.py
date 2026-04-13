#!/usr/bin/env python3

from gi.repository import GLib

import ctypes
import winreg


def _(message):
    return GLib.dgettext(None, message)


def get_title():
    titles = []
    user32 = ctypes.windll.user32

    def callback(hwnd, _):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            titles.append(buff.value)
        return True

    enum_windows_proc = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.c_int,
        ctypes.c_int,
    )
    user32.EnumWindows(enum_windows_proc(callback), 0)

    for title in titles:
        if "GIMP" in title:
            return f"title={title}"

    return ""


def get_path():
    keys = [
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            "Path",
        ),
        (
            winreg.HKEY_CURRENT_USER,
            "Environment",
            "Path",
        ),
    ]
    paths = []

    for key in keys:
        with winreg.OpenKey(*key[:-1]) as path:
            name = key[-1]
            value, _ = winreg.QueryValueEx(path, name)
            paths.append(value)

    return ";".join(paths)


def format_time(seconds):
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    return f"{h:02d}:{m:02d}:{s:02d}"
