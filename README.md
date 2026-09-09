# 🕒 Minimal Clock Dock (Reloj + DND + Volumen)

Dock minimalista, moderno y flotante con:
- 🕒 **Reloj en formato 24 horas** (`HH:MM`).
- 🔕 **Modo No Molestar (DND)** interactivo con `swaync`.
- 🔊 **Control de Volumen General interactivo** con `wpctl`.
- 🪟 **Fondo oscuro translúcido con blur acrílico** y bordes limpios sin halos.
- 📌 **Persistencia sobre pantalla completa (Fullscreen)** y **fijado al monitor principal por defecto**.

---

## 🎛️ Controles del Dock

### 1. Botón de Modo No Molestar (Campana)
- **Clic**: Alterna entre **Modo Normal** (󰂚) y **Modo No Molestar** (󰂛 en rojo).

### 2. Botón de Volumen (Altavoz)
- **Rueda del ratón hacia arriba / abajo**: Sube o baja el volumen (+5% / -5%).
- **Clic izquierdo**: Silencia o desilencia el audio (Mute toggle 󰝟).
- **Clic derecho**: Abre el mezclador gráfico de audio (`pavucontrol`) para configuración avanzada.

---

## 📦 1. Dependencias Requeridas

En **Arch Linux / EndeavourOS**:
```bash
sudo pacman -S python python-gobject gtk3 gtk-layer-shell swaync wireplumber pavucontrol
```

---

## ⚙️ 2. Archivos de Configuración

Crea la carpeta de configuración si aún no existe:
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
    def __init__(self, monitor=None):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_name("dock-window")
        
        # Integración con LayerShell (Hyprland / Wayland)
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "minimal-dock")
        # OVERLAY garantiza que quede visible incluso en pantalla completa (fullscreen)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        
        # Asignar a la pantalla principal
        if monitor:
            GtkLayerShell.set_monitor(self, monitor)
        
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
        
        # Separador vertical
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        separator.get_style_context().add_class("dock-separator")
        box.pack_start(separator, False, False, 0)
        
        # Botón Campana (No Molestar / DND)
        self.dnd_btn = Gtk.Button()
        self.dnd_btn.get_style_context().add_class("dock-icon-btn")
        self.dnd_label = Gtk.Label()
        self.dnd_btn.add(self.dnd_label)
        self.dnd_btn.connect("clicked", self.toggle_dnd)
        box.pack_start(self.dnd_btn, False, False, 0)
        
        # Botón de Volumen interactivo
        self.vol_btn = Gtk.Button()
        self.vol_btn.get_style_context().add_class("dock-icon-btn")
        self.vol_label = Gtk.Label()
        self.vol_btn.add(self.vol_label)
        
        # Habilitar eventos de scroll de ratón para subir/bajar volumen
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
            self.dnd_label.set_text("󰂛") # Campana tachada (DND activo)
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

    def get_volume_info(self):
        try:
            out = subprocess.check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], text=True, timeout=1).strip()
            # Formato: "Volume: 0.40" o "Volume: 0.40 [MUTED]"
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
            self.vol_label.set_text("󰝟") # Silenciado
            ctx.remove_class("vol-icon")
            ctx.add_class("vol-muted")
            self.vol_btn.set_tooltip_text("Volumen: Silenciado (Clic izq: Desmutear | Clic der: Mezclador)")
        else:
            ctx.remove_class("vol-muted")
            ctx.add_class("vol-icon")
            if vol < 30:
                icon = "󰕿"
            elif vol < 70:
                icon = "󰖀"
            else:
                icon = "󰕾"
            self.vol_label.set_text(icon)
            self.vol_btn.set_tooltip_text(f"Volumen: {vol}% (Rueda: Ajustar | Clic izq: Silenciar | Clic der: Mezclador)")
        return True

    def on_vol_click(self, widget, event):
        if event.button == 1: # Clic izquierdo: Mute / Unmute
            subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], check=False)
            self.update_volume_status()
            return True
        elif event.button == 3: # Clic derecho: Abrir pavucontrol
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

.dock-separator {
    background-color: rgba(255, 255, 255, 0.18);
    width: 1px;
    margin: 3px 10px;
}

.dock-icon-btn {
    font-size: 15px;
    padding: 2px 5px;
    border-radius: 8px;
    transition: all 150ms ease;
}

.dock-icon-btn:hover {
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

.vol-icon {
    color: rgba(255, 255, 255, 0.65);
}

.vol-icon:hover {
    color: #ffffff;
}

.vol-muted {
    color: #f87171;
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
