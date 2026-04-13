#!/usr/bin/env python3

from gi.repository import GLib

from utils import get_path, get_title

import re
import shlex
import shutil
import subprocess
import threading


class Recorder(threading.Thread):
    def __init__(self, parent, config, crop_rect):
        super().__init__()
        self.parent = parent
        self.crop_rect = crop_rect

        for prop in config.list_properties():
            name = prop.name.replace("-", "_")
            value = config.get_property(prop.name)
            setattr(self, name, value)

    def run(self):
        path = get_path()
        ffmpeg = shutil.which("ffmpeg.exe", path=path)

        command = [ffmpeg, "-hide_banner", "-y", "-loglevel", "error"]

        input_args = [
            "-f",
            "gdigrab",
            "-framerate",
            str(self.capture_fps),
        ]

        if self.draw_mouse:
            input_args += ["-draw_mouse", "1"]

        if self.draw_area:
            input_args += ["-show_region", "1"]

        if self.capture_mode == "window":
            input_args += ["-i", get_title()]

        elif self.capture_mode == "screen":
            input_args += ["-i", "desktop"]

        elif self.capture_mode == "area":
            x, y, w, h = self.crop_rect
            input_args += [
                "-video_size",
                f"{w}x{h}",
                "-offset_x",
                str(x),
                "-offset_y",
                str(y),
                "-i",
                "desktop",
            ]

        output_args = [
            "-vf",
            f"setpts={self.capture_fps / self.video_fps}*PTS,fps={self.video_fps}",
        ]

        default_options = ["-c", "libx264", "-pix_fmt", "yuv420p"]
        advanced_options = shlex.split(self.advanced_options)

        output_args += advanced_options or default_options

        command += input_args + output_args + [self.output_path]

        print(f"Recording with {' '.join(command)}\n\n\n")

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
            text=True,
        )

        reason = ""

        print("\033[91m")
        for letter in self.process.stderr:
            print(letter)
            reason += letter
        print("\033[0m")

        if self.process.wait() != 0:
            GLib.idle_add(
                self.parent.stop_recorder,
                re.sub(r"\[.*\] ", "", reason),
            )
            return

    def stop(self):
        if not self.process:
            return

        if self.process.poll() is None and self.process.stdin:
            try:
                self.process.stdin.write("q\n")
                self.process.stdin.flush()
                self.process.stdin.close()
            except OSError, ValueError, BrokenPipeError:
                pass

            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.terminate()
