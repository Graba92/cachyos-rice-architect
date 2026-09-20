# ⚡ CachyOS Rice-Architect — Advanced Ricing, Theming & Dotfile Automation

Transform your CachyOS and Arch Linux desktop into a visual masterpiece. **CachyOS Rice-Architect** is a comprehensive, interactive TUI suite and CLI engine tailored for KDE Plasma 6 (Wayland) and modern Linux terminal emulators.

---

### 🌟 Key Capabilities
- **🌐 Bilingual by Design (German & English):** Toggle between English and German on the fly via the <kbd>L</kbd> key or via `--lang de` / `--lang en`.
- **🎨 1-Click Curated Presets:** Instant dotfile deployments for Starship, Fastfetch, Alacritty, Kitty, Ghostty, Konsole, Waybar, and Rofi.
- **🛡️ Safe Theming & Rollback:** Autonomous backup creation before applying any configuration, with single-command rollback.
- **🩺 Rice-Doctor:** Diagnoses installed compositor features, Nerd Fonts, Wayland protocols, and environment variables.
- **📖 Interactive Guide Browser:** Extensive, searchable documentation and markdown tutorials rendered directly inside the terminal.

---

### 🚀 Quick Start

```bash
git clone https://github.com/Graba92/cachyos-rice-architect.git
cd cachyos-rice-architect
./setup.sh
./run.sh

# Run Rice-Doctor or CLI in English
python3 main.py --doctor --lang en
python3 main.py --presets --lang en
```

---
*Created by Matthias Haase (xxgrabaxx) for the CachyOS & Linux Customization Community.*
