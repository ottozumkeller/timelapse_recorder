#!/usr/bin/env python3

import gi

gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")
from gi.repository import Gimp, GimpUi, GObject

from dialog import Dialog
from utils import _

import sys


class Plugin(Gimp.PlugIn):
    def __init__(self):
        super().__init__()

    def do_query_procedures(self):
        return ["timelapse-recorder"]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            self.run,
            None,
        )

        procedure.set_image_types("*")

        procedure.set_menu_label(_("Timelapse _Recorder"))
        procedure.set_icon_name(GimpUi.ICON_GEGL)
        procedure.add_menu_path("<Image>/Tools")

        procedure.set_documentation(
            _("Record a timelapse video of your editing process"),
            None,
            name,
        )
        procedure.set_attribution(
            "Otto Zumkeller",
            "Otto Zumkeller",
            "2026",
        )

        procedure.add_string_argument(
            "output-path",
            _("Output Path"),
            _("The output file path of the timelapse"),
            "output.mp4",
            GObject.ParamFlags.READWRITE,
        )

        procedure.add_int_argument(
            "capture-fps",
            _("Capture FPS"),
            _("How many times per second a frame should be captured"),
            1,
            30,
            6,
            GObject.ParamFlags.READWRITE,
        )

        procedure.add_int_argument(
            "video-fps",
            _("Video FPS"),
            _("How many times per second a new frame "
              "should be displayed in the final video"),
            1,
            60,
            60,
            GObject.ParamFlags.READWRITE,
        )

        procedure.add_string_argument(
            "capture-mode",
            _("Capture Mode"),
            _("The recording mode"),
            "window",
            GObject.ParamFlags.READWRITE,
        )

        procedure.add_string_argument(
            "advanced-options",
            _("Advanced Options"),
            _("Set additional parameters for ffmpeg"),
            "",
            GObject.ParamFlags.READWRITE,
        )

        procedure.add_boolean_argument(
            "draw-mouse",
            _("Draw Mouse"),
            _("Show mouse cursor in recording"),
            False,
            GObject.ParamFlags.READWRITE,
        )

        procedure.add_boolean_argument(
            "draw-area",
            _("Draw Area"),
            _("Highlight capture region"),
            False,
            GObject.ParamFlags.READWRITE,
        )

        return procedure

    def run(self, procedure, _run_mode, image, _drawables, config, _data):
        GimpUi.init("timelapse-recorder")

        dialog = Dialog(image, procedure, config)
        dialog.run()

        config.set_property("capture-fps", dialog.capture_fps.get_value())
        config.set_property("video-fps", dialog.video_fps.get_value())
        config.set_property("output-path", dialog.path_text.get_text())
        config.set_property("capture-mode", dialog.mode_combo.get_active_id())
        config.set_property("advanced-options", dialog.advanced_text.get_text())

        dialog.destroy()

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)


Gimp.main(Plugin.__gtype__, sys.argv)
