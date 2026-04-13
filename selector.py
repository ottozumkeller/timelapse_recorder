#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

import math


class Selector(Gtk.Window):
    def __init__(self, parent=None):
        super().__init__(transient_for=parent)

        self.start_x = self.start_y = 0
        self.end_x = self.end_y = 0
        self.selected_rect = None

        self.set_modal(True)
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.fullscreen()

        visual = self.get_screen().get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_mouse_move)
        self.connect("key-press-event", self.on_key_press)
        self.connect("realize", self.on_realize)

        mask = (
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )

        self.add_events(mask)

        self.drawing_area = Gtk.DrawingArea()
        self.add(self.drawing_area)
        self.drawing_area.connect("draw", self.on_draw)

        self.show_all()

        self.drawing_area.queue_draw()
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)

    def on_button_press(self, _, event):
        self.start_x, self.start_y = int(event.x), int(event.y)
        self.end_x, self.end_y = self.start_x, self.start_y
        return True

    def on_mouse_move(self, _, event):
        self.end_x, self.end_y = int(event.x), int(event.y)
        self.drawing_area.queue_draw()
        return True

    def on_button_release(self, _, event):
        self.end_x, self.end_y = int(event.x), int(event.y)
        x = math.floor(min(self.start_x, self.end_x) / 2.0) * 2
        y = math.floor(min(self.start_y, self.end_y) / 2.0) * 2
        w = math.floor(abs(self.end_x - self.start_x) / 2.0) * 2
        h = math.floor(abs(self.end_y - self.start_y) / 2.0) * 2

        if w == 0 or h == 0:
            self.selected_rect = None
            self.destroy()
            return True

        self.selected_rect = (x, y, w, h)
        self.destroy()
        return True

    def on_key_press(self, _, event):
        key = Gdk.keyval_name(event.keyval)
        if key == "Escape":
            self.selected_rect = None
            self.destroy()
            return True
        return False

    def on_realize(self, _):
        display = Gdk.Display.get_default()
        cursor = Gdk.Cursor.new_from_name(display, "crosshair")
        self.get_window().set_cursor(cursor)

    def on_draw(self, _, cr):
        cr.set_source_rgba(1, 1, 1, 0.005)
        cr.paint()

        if self.start_x and self.start_y:
            x = min(self.start_x, self.end_x)
            y = min(self.start_y, self.end_y)
            w = abs(self.end_x - self.start_x)
            h = abs(self.end_y - self.start_y)

            cr.set_source_rgba(1, 0, 0, 0.25)
            cr.rectangle(x, y, w, h)
            cr.fill()

        return False
