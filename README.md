# 🕒 Minimal Clock Dock (con Campana / DND)

Guía completa para replicar el dock minimalista flotante con reloj 24h, botón sutil de **Campana (No Molestar / DND)**, fondo oscuro translúcido, efecto blur acrílico y persistencia sobre ventanas a pantalla completa.

---

## 📦 1. Dependencias Requeridas

En Arch Linux / EndeavourOS:

```bash
sudo pacman -S python python-gobject gtk3 gtk-layer-shell swaync
```

---

## ⚙️ 2. Archivos de Configuración

Crea la carpeta de configuración:
```bash
mkdir -p ~/.config/minimal-dock
```

### 📄 Archivo 1: `~/.config/minimal-dock/dock.py`

Guarda el siguiente script en [`~/.config/minimal-dock/dock.py`](file:///home/roger/.config/minimal-dock/dock.py):

```python
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
        
        # Integración con LayerShell (Hyprland / Wayland)
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "minimal-dock")
        # OVERLAY garantiza que quede visible incluso en pantalla completa (fullscreen)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        
        # Anclar abajo al centro
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, False)
        
        # Margen inferior
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 14)
        
        # Canal alfa / transparencia
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
            
        self.set_app_paintable(True)
        
        # Cargar estilos CSS
        self.load_css()
        
        # Estructura UI
        self.setup_ui()
        
        # Actualizaciones periódicas
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
            self.dnd_label.set_text("󰂛") # Campana tachada (DND activo)
            self.dnd_btn.set_tooltip_text("No Molestar: Activo (Clic para desactivar)")
            ctx.remove_class("dnd-off")
            ctx.add_class("dnd-on")
        else:
            self.dnd_label.set_text("󰂚") # Campana normal (Modo normal)
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
```

Dale permisos de ejecución:
```bash
chmod +x ~/.config/minimal-dock/dock.py
```

---

### 🎨 Archivo 2: `~/.config/minimal-dock/style.css`

Guarda el archivo en [`~/.config/minimal-dock/style.css`](file:///home/roger/.config/minimal-dock/style.css):

```css
* {
    all: unset;
    font-family: "JetBrainsMono Nerd Font", "FiraCode Nerd Font", "Noto Sans", "Roboto", sans-serif;
}

window#dock-window {
    background-color: transparent;
    background: transparent;
}

.dock-capsule {
    background-color: rgba(18, 20, 29, 0.60);
    border: 1.5px solid rgba(255, 255, 255, 0.18);
    border-radius: 20px;
    padding: 8px 20px;
    min-height: 28px;
}

.dock-clock {
    color: #ffffff;
    font-weight: 800;
    font-size: 17px;
    letter-spacing: 2px;
}

.dock-dnd-btn {
    font-size: 15px;
    margin-left: 10px;
    padding: 2px 4px;
    border-radius: 8px;
    transition: all 150ms ease;
}

.dock-dnd-btn:hover {
    background-color: rgba(255, 255, 255, 0.12);
}

.dnd-on {
    color: #f87171; /* Rojo suave cuando está en No Molestar */
}

.dnd-off {
    color: rgba(255, 255, 255, 0.35); /* Campana normal */
}

.dnd-off:hover {
    color: #ffffff;
}
```

---

## 🪟 3. Configuración en Hyprland

### A. Regla de desenfoque (Blur e Ignorealpha)

**En `hyprland.conf` (formato estándar):**
```ini
layerrule = blur, minimal-dock
layerrule = ignorealpha 0.1, minimal-dock
```

**O en formato Lua (`~/.config/hypr/conf/windowrules/default.lua`):**
```lua
hl.config({
    layerrule = {
        "blur, minimal-dock",
        "ignorealpha 0.1, minimal-dock",
    }
})
```

### B. Inicio automático (Autostart)

**En `hyprland.conf`:**
```ini
exec-once = python3 ~/.config/minimal-dock/dock.py
```

**O en Lua (`~/.config/hypr/conf/autostart.lua`):**
```lua
hl.exec_cmd("python3 " .. HOME .. "/.config/minimal-dock/dock.py")
```

---

## 🚀 4. Probar / Reiniciar en caliente

```bash
pkill -f "dock.py" || true; python3 ~/.config/minimal-dock/dock.py &
```
