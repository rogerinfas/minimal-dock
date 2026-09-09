#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell

class MinimalClockDock(Gtk.Window):
    def __init__(self, monitor=None):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_name("dock-window")
        
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "minimal-dock")
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        
        if monitor:
            GtkLayerShell.set_monitor(self, monitor)
        
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
        GLib.timeout_add_seconds(2, self.update_volume_status)
        self.update_clock()
        self.update_dnd_status()
        self.update_volume_status()

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
        
        # Botón Campana (DND)
        self.dnd_btn = Gtk.Button()
        self.dnd_btn.get_style_context().add_class("dock-dnd-btn")
        self.dnd_label = Gtk.Label()
        self.dnd_btn.add(self.dnd_label)
        self.dnd_btn.connect("clicked", self.toggle_dnd)
        box.pack_start(self.dnd_btn, False, False, 0)
        
        # Botón Volumen (sin separador, estilo unificado)
        self.vol_btn = Gtk.Button()
        self.vol_btn.get_style_context().add_class("dock-vol-btn")
        self.vol_label = Gtk.Label()
        self.vol_btn.add(self.vol_label)
        self.vol_btn.add_events(Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.BUTTON_PRESS_MASK)
        self.vol_btn.connect("button-press-event", self.on_vol_click)
        self.vol_btn.connect("scroll-event", self.on_vol_scroll)
        box.pack_start(self.vol_btn, False, False, 0)
        
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
            self.dnd_label.set_text("󰂛")
            self.dnd_btn.set_tooltip_text("No Molestar: Activo (Clic para desactivar)")
            ctx.remove_class("dnd-off")
            ctx.add_class("dnd-on")
        else:
            self.dnd_label.set_text("󰂚")
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

    def get_volume_info(self):
        try:
            out = subprocess.check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], text=True, timeout=1).strip()
            is_muted = "[MUTED]" in out
            vol_str = out.replace("Volume:", "").replace("[MUTED]", "").strip()
            vol = int(float(vol_str) * 100)
            return vol, is_muted
        except Exception:
            return 50, False

    def update_volume_status(self):
        vol, is_muted = self.get_volume_info()
        ctx = self.vol_btn.get_style_context()
        
        if is_muted or vol == 0:
            self.vol_label.set_text("󰝟")
            ctx.remove_class("vol-on")
            ctx.add_class("vol-muted")
            self.vol_btn.set_tooltip_text("Volumen: Silenciado")
        else:
            ctx.remove_class("vol-muted")
            ctx.add_class("vol-on")
            if vol < 30:
                icon = "󰕿"
            elif vol < 70:
                icon = "󰖀"
            else:
                icon = "󰕾"
            self.vol_label.set_text(icon)
            self.vol_btn.set_tooltip_text(f"Volumen: {vol}%")
        return True

    def on_vol_click(self, widget, event):
        if event.button == 1:
            subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], check=False)
            self.update_volume_status()
            return True
        elif event.button == 3:
            try:
                subprocess.Popen(["pavucontrol"])
            except Exception:
                pass
            return True
        return False

    def on_vol_scroll(self, widget, event):
        if event.direction == Gdk.ScrollDirection.UP:
            subprocess.run(["wpctl", "set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", "5%+"], check=False)
            self.update_volume_status()
            return True
        elif event.direction == Gdk.ScrollDirection.DOWN:
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"], check=False)
            self.update_volume_status()
            return True
        return False

def get_primary_monitor():
    display = Gdk.Display.get_default()
    if not display:
        return None
    primary = display.get_primary_monitor()
    if primary:
        return primary
    n = display.get_n_monitors()
    if n == 0:
        return None
    best_monitor = display.get_monitor(0)
    max_pixels = 0
    for i in range(n):
        mon = display.get_monitor(i)
        geom = mon.get_geometry()
        pixels = geom.width * geom.height
        if pixels > max_pixels:
            max_pixels = pixels
            best_monitor = mon
    return best_monitor

if __name__ == "__main__":
    primary_mon = get_primary_monitor()
    win = MinimalClockDock(monitor=primary_mon)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
