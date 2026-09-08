# 🐚 Configuración de Terminal Inteligente (Zsh + Oh My Zsh)

Guía para replicar la terminal con:
- 💡 **Autocompletado predictivo en tiempo real** (`zsh-autosuggestions`)
- 🔍 **Completado insensible a mayúsculas/minúsculas con `Tab`**
- 🎨 **Resaltado de sintaxis en vivo** (`zsh-syntax-highlighting`)
- 🔎 **Búsqueda difusa en el historial con <kbd>Ctrl</kbd> + <kbd>R</kbd>** (`fzf`)

---

## 📦 1. Instalación de Paquetes Base

En **Arch Linux / EndeavourOS**:
```bash
sudo pacman -S zsh git fzf curl
```

En **Ubuntu / Debian**:
```bash
sudo apt update && sudo apt install -y zsh git fzf curl
```

---

## 🚀 2. Instalar Oh My Zsh

Ejecuta el script oficial de instalación:
```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```
*(Cuando te pregunte si deseas cambiar tu shell por defecto a Zsh, escribe `Y` y presiona Enter).*

---

## 🔌 3. Instalar Plugins de Autocompletado y Colores

Clona los plugins en el directorio de personalizaciones de Oh My Zsh:

```bash
# 1. Sugerencias y autocompletado en tiempo real (texto gris con Tab/Flecha Derecha)
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# 2. Resaltado de sintaxis en vivo (Verde si el comando existe, Rojo si está mal)
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

---

## ⚙️ 4. Configurar `~/.zshrc`

Abre tu archivo de configuración:
```bash
nano ~/.zshrc
```

### A. Habilitar la lista de plugins
Busca la línea `plugins=(...)` y déjala así:
```bash
plugins=(
    git
    sudo
    zsh-autosuggestions
    zsh-syntax-highlighting
)
```

### B. Habilitar completado inteligente con <kbd>Tab</kbd> (Ignorar Mayúsculas/Minúsculas)
Agrega estas líneas al final de tu `~/.zshrc`:
```bash
# Completado insensible a mayúsculas/minúsculas con TAB
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*' menu select

# Integración con FZF (búsqueda difusa de comandos e historial)
source <(fzf --zsh 2>/dev/null) || true
```

---

## 🔄 5. Aplicar Cambios

Recarga la configuración sin reiniciar la terminal:
```bash
source ~/.zshrc
```

---

## 🎯 ¿Cómo usarlo?

- **Aceptar sugerencia completa**: Presiona <kbd>→</kbd> (Flecha derecha) o <kbd>End</kbd>.
- **Completar palabras y rutas ignorando mayúsculas**: Escribe en minúsculas y presiona <kbd>Tab</kbd>.
- **Buscador interactivo del historial**: Presiona <kbd>Ctrl</kbd> + <kbd>R</kbd> para buscar cualquier comando pasado con `fzf`.
