#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell

class MinimalClockDock(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_name("dock-window")
        
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "minimal-dock")
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, False)
        
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 14)
        
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
            
        self.set_app_paintable(True)
        
        self.load_css()
        self.setup_ui()
        
        GLib.timeout_add_seconds(1, self.update_clock)
        GLib.timeout_add_seconds(2, self.update_dnd_status)
        self.update_clock()
        self.update_dnd_status()

    def load_css(self):
        provider = Gtk.CssProvider()
        try:
            css_path = os.path.expanduser("~/.config/minimal-dock/style.css")
            provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"Error cargando CSS: {e}")

    def setup_ui(self):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.get_style_context().add_class("dock-capsule")
        
        # Reloj 24h
        self.clock_label = Gtk.Label()
        self.clock_label.get_style_context().add_class("dock-clock")
        box.pack_start(self.clock_label, True, True, 0)
        
        # Botón Campana (No Molestar)
        self.dnd_btn = Gtk.Button()
        self.dnd_btn.get_style_context().add_class("dock-dnd-btn")
        self.dnd_label = Gtk.Label()
        self.dnd_btn.add(self.dnd_label)
        self.dnd_btn.connect("clicked", self.toggle_dnd)
        box.pack_start(self.dnd_btn, False, False, 0)
        
        self.add(box)

    def update_clock(self):
        now = datetime.now()
        self.clock_label.set_text(now.strftime("%H:%M"))
        return True

    def get_dnd_state(self):
        try:
            out = subprocess.check_output(["swaync-client", "-D"], text=True, timeout=1).strip()
            return out.lower() == "true"
        except Exception:
            return False

    def update_dnd_status(self):
        is_dnd = self.get_dnd_state()
        ctx = self.dnd_btn.get_style_context()
        if is_dnd:
            self.dnd_label.set_text("󰂛") # Campana tachada / DND
            self.dnd_btn.set_tooltip_text("No Molestar: Activo (Clic para desactivar)")
            ctx.remove_class("dnd-off")
            ctx.add_class("dnd-on")
        else:
            self.dnd_label.set_text("󰂚") # Campana normal
            self.dnd_btn.set_tooltip_text("No Molestar: Desactivado (Clic para activar)")
            ctx.remove_class("dnd-on")
            ctx.add_class("dnd-off")
        return True

    def toggle_dnd(self, widget):
        try:
            subprocess.run(["swaync-client", "-d"], check=False)
            self.update_dnd_status()
        except Exception as e:
            print(f"Error cambiando DND: {e}")

if __name__ == "__main__":
    win = MinimalClockDock()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
