#!/usr/bin/env python3

import gi

gi.require_version("GimpUi", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import GimpUi, GLib, GObject, Gtk

from recorder import Recorder
from selector import Selector
from utils import _, format_time

import os
import time


class Dialog(GimpUi.ProcedureDialog):
    def __init__(self, _image, procedure, config) -> None:
        super().__init__(procedure=procedure, config=config)

        self.config = config
        self.recorder = None

        builder = Gtk.Builder()
        parent_folder = os.path.dirname(__file__)
        file = os.path.join(parent_folder, "dialog.xml")
        builder.add_from_file(file)

        for widget in builder.get_objects():
            name = Gtk.Buildable.get_name(widget)
            if name and not hasattr(self, name):
                setattr(self, name, widget)

        self.output_label.set_label(_("Output Path"))
        self.capture_mode_label.set_label(_("Capture Mode"))
        self.capture_fps_label.set_label(_("Capture FPS"))
        self.video_fps_label.set_label(_("Video FPS"))
        self.start_button.set_label(_("_Start"))
        self.time_text.set_label(_("Ready"))
        self.draw_label.set_label(_("Show Indicators"))
        self.path_button.set_label(f" {_('_Browse')} ")
        self.clear_button.set_label(f" {_('_Clear')} ")
        self.draw_mouse_check.set_label(f" {_('_Mouse')}")
        self.draw_area_check.set_label(f" {_('Recording _Area')}")
        self.advanced_label.set_label(_("Advanced Options"))
        self.advanced_label.set_tooltip_text(
            _(
                "Add additional arguments to the ffmpeg command. "
                "Only use if you know what you're doing "
                "(Video codec needs to be specified manually).",
            ),
        )

        self.mode_combo.append("screen", f" {_('Screen')}  ")
        self.mode_combo.append("window", f" {_('Window')}  ")
        self.mode_combo.append("area", f" {_('Area')}  ")

        self.capture_fps = Gtk.Adjustment(
            value=config.get_property("capture-fps"),
            lower=1,
            upper=30,
            step_increment=1,
        )
        self.video_fps = Gtk.Adjustment(
            value=config.get_property("video-fps"),
            lower=1,
            upper=60,
            step_increment=1,
        )

        self.capture_spin.set_adjustment(self.capture_fps)
        self.video_spin.set_adjustment(self.video_fps)

        flags = GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE

        config.bind_property("capture-fps", self.capture_fps, "value", flags)
        config.bind_property("video-fps", self.video_fps, "value", flags)
        config.bind_property("output-path", self.path_text, "text", flags)
        config.bind_property("capture-mode", self.mode_combo, "active_id", flags)
        config.bind_property("advanced-options", self.advanced_text, "text", flags)
        config.bind_property("draw-mouse", self.draw_mouse_check, "active", flags)
        config.bind_property("draw-area", self.draw_area_check, "active", flags)

        speed = self.video_fps.get_value() / self.capture_fps.get_value()
        self.speed_text.set_text(f"{speed:.1f}x")

        self.start_button.connect("clicked", self.on_toggle)
        self.path_button.connect("clicked", self.on_browse)
        self.clear_button.connect("clicked", self.on_clear)
        self.capture_spin.connect("value-changed", self.on_speed_changed)
        self.video_spin.connect("value-changed", self.on_speed_changed)
        self.mode_combo.connect("changed", self.on_mode_changed)
        self.connect("destroy", self.on_close)

        self.on_mode_changed(self.mode_combo)

        main_box = builder.get_object("main_box")
        self.get_content_area().pack_start(main_box, True, True, 0)
        self.show_all()

    def on_browse(self, _):
        dialog = Gtk.FileChooserNative(
            title=_("Select Output File"),
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
            accept_label=_("_Save"),
            cancel_label=_("_Cancel"),
        )
        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            self.config.set_property("output-path", dialog.get_filename())

        dialog.destroy()

    def on_clear(self, _):
        self.config.set_property("advanced-options", "")

    def on_speed_changed(self, _):
        speed = self.video_fps.get_value() / self.capture_fps.get_value()
        self.speed_text.set_text(f"{speed:.1f}x")

    def on_mode_changed(self, widget):
        if widget.get_active_id() != "area":
            self.draw_area_check.set_sensitive(False)
            self.draw_area_check.set_active(False)
        else:
            self.draw_area_check.set_sensitive(True)

    def on_toggle(self, _):
        running = isinstance(self.recorder, Recorder)
        if not running:
            self.start_recorder()
        else:
            self.stop_recorder()

    def update_runtime(self):
        running = self.recorder and self.start_time
        if running:
            elapsed = time.time() - self.start_time
            speed = self.video_fps.get_value() / self.capture_fps.get_value()
            projected = int(elapsed / speed)
            self.time_text.set_label(
                f"{format_time(elapsed)}\n🠋\n{format_time(projected)}",
            )
        return running

    def stop_recorder(self, reason=None):
        if self.recorder:
            self.recorder.stop()
            self.recorder.join()
            self.recorder = None

        self.time_text.set_label(_("Error") if reason else _("Ready"))
        self.time_text.set_tooltip_text(reason or "")
        self.start_button.set_label(_("_Start"))

        self.toggle_sensitivity(True)

    def start_recorder(self):
        mode = self.mode_combo.get_active_id()
        crop_rect = None

        if mode == "area":
            selector = Selector(parent=self)
            selector.show_all()
            while selector.get_visible():
                while Gtk.events_pending():
                    Gtk.main_iteration_do(False)
            crop_rect = selector.selected_rect
            if not crop_rect:
                return

        self.recorder = Recorder(
            parent=self,
            config=self.config,
            crop_rect=crop_rect,
        )

        self.recorder.start()
        self.start_time = time.time()

        GLib.timeout_add(500, self.update_runtime)
        self.start_button.set_label(_("Sto_p"))

        self.toggle_sensitivity(False)

    def toggle_sensitivity(self, running):
        self.path_text.set_sensitive(running)
        self.path_button.set_sensitive(running)
        self.mode_combo.set_sensitive(running)
        self.capture_spin.set_sensitive(running)
        self.video_spin.set_sensitive(running)
        self.advanced_text.set_sensitive(running)
        self.clear_button.set_sensitive(running)
        self.draw_mouse_check.set_sensitive(running)
        self.draw_area_check.set_sensitive(running)

    def on_close(self, _):
        if self.recorder:
            self.stop_recorder()
