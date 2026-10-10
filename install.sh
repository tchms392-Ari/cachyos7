#!/usr/bin/env bash
# CachyOS 7 installer - Windows 7 layout + CachyOS colours for Xfce.
# Usage: ./install.sh [--dry-run] [--scale auto|1|2] [--no-lock] [--logo FILE] [--with-login] [--with-splash] [--yes]
# User-level by default. --with-login / --with-splash run a sudo step (asked first).
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"; A="$REPO/assets"
DRY=0 YES=0 LOGIN=0 SPLASH=0; APPLY=()
while [ $# -gt 0 ]; do case "$1" in
  --dry-run) DRY=1;; --yes|-y) YES=1;; --with-login) LOGIN=1;; --with-splash) SPLASH=1;; --no-lock) APPLY+=(--no-lock);;
  --scale) APPLY+=(--scale "$2"); shift;; --logo) APPLY+=(--logo "$(readlink -f "$2")"); shift;;
  -h|--help) sed -n 2,5p "$0"; exit 0;; *) echo "unknown option $1"; exit 2;; esac; shift; done
run(){ if [ $DRY = 1 ]; then echo "  [dry-run] $*"; else "$@"; fi; }
ask(){ [ $YES = 1 ] && return 0; [ $DRY = 1 ] && { echo "  [dry-run] would ask: $1"; return 1; }; read -r -p "$1 [y/N] " r; [[ "$r" =~ ^[Yy] ]]; }
say(){ printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
[ "$(id -u)" != 0 ] || { echo "Run install.sh as your normal user (it asks for sudo only where needed)."; exit 1; }

say "1. Packages"
NEED="xfce4 xfce4-goodies xfce4-docklike-plugin xfce4-whiskermenu-plugin xfce4-pulseaudio-plugin xfce4-notifyd xfce4-screensaver xorg-server network-manager-applet pavucontrol python-pillow python-numpy librsvg ffmpeg ttf-opensans noto-fonts"
if command -v pacman >/dev/null; then
  missing=$(for p in $NEED; do pacman -Qq "$p" >/dev/null 2>&1 || pacman -Qg "$p" >/dev/null 2>&1 || echo -n "$p "; done)
  if [ -n "$missing" ]; then echo "   missing: $missing"
    if ask "   Install them now with: sudo pacman -S --needed $missing ?"; then run sudo pacman -S --needed $missing; else echo "   skipped - install them yourself before logging in to Xfce"; fi
  else echo "   all required packages present"; fi
else
  echo "   Not an Arch-based system. Install the equivalents yourself:"
  echo "   Debian/Ubuntu: sudo apt install xfce4 xfce4-goodies xfce4-whiskermenu-plugin xfce4-pulseaudio-plugin xfce4-notifyd xorg network-manager-gnome pavucontrol python3-pil python3-numpy librsvg2-bin ffmpeg fonts-open-sans fonts-noto  (docklike: build from https://gitlab.xfce.org/panel-plugins/xfce4-docklike-plugin)"
  echo "   Fedora:        sudo dnf install @xfce-desktop-environment xfce4-whiskermenu-plugin xfce4-pulseaudio-plugin xfce4-docklike-plugin python3-pillow python3-numpy librsvg2-tools ffmpeg open-sans-fonts google-noto-sans-mono-fonts"
  echo "   openSUSE:      sudo zypper install -t pattern xfce ; sudo zypper install xfce4-plugin-whiskermenu xfce4-plugin-pulseaudio xfce4-docklike-plugin python3-Pillow python3-numpy rsvg-convert"
fi

say "2. Backup of your current settings"
B="$HOME/.local/share/cachyos7-backup/$(date +%Y%m%d-%H%M%S)"; echo "   -> $B"
run mkdir -p "$B"
for p in .config/xfce4 .xprofile .config/gtk-3.0/settings.ini .config/gtk-4.0/settings.ini; do
  [ -e "$HOME/$p" ] && { run mkdir -p "$B/$(dirname "$p")"; run cp -a "$HOME/$p" "$B/$p"; echo "   saved ~/$p"; } || true; done
[ $DRY = 1 ] || echo "$B" > "$HOME/.local/share/cachyos7-backup/LAST"

say "3. Themes, icons, cursor, sounds, wallpapers"
cp_tree(){ run mkdir -p "$2"; run rsync -a --delete "$1/" "$2/"; echo "   $(basename "$1") -> ${2/#$HOME/~}"; }
for t in CachyOS-7 CachyOS-7-Aero CachyOS-7-Aero-xhdpi; do cp_tree "$A/themes/$t" "$HOME/.themes/$t"; done
for t in CachyOS-7 Windows-7 Win7OS-cursors; do cp_tree "$A/icons/$t" "$HOME/.icons/$t"; done
cp_tree "$A/sounds/CachyOS-7" "$HOME/.local/share/sounds/CachyOS-7"
cp_tree "$A/wallpapers" "$HOME/.local/share/backgrounds/cachyos7"
run mkdir -p "$HOME/.local/share/cachyos7"; run cp -a "$A/shortcuts/." "$HOME/.local/share/cachyos7/"
if [ ! -e "$HOME/.face" ]; then run cp "$A/avatar/cachyos7-avatar.png" "$HOME/.face"; echo "   default picture -> ~/.face"; fi

say "4. Xfce configuration"
if [ $DRY = 1 ]; then CACHYOS7_ASSETS="$A" python3 "$REPO/generators/cachyos7-apply" --dry-run "${APPLY[@]}"
else CACHYOS7_ASSETS="$A" python3 "$REPO/generators/cachyos7-apply" "${APPLY[@]}"; fi
if [ "${XDG_CURRENT_DESKTOP:-}" != XFCE ]; then echo "   Log out and pick 'Xfce Session' on the login screen."; fi

if [ $LOGIN = 1 ]; then say "5. Login screen (LightDM, needs sudo)"
  if ask "   Switch the login screen to the CachyOS 7 LightDM greeter (sudo bash scripts/login-setup.sh)?"; then run sudo bash "$REPO/scripts/login-setup.sh"; fi; fi
if [ $SPLASH = 1 ]; then say "6. Boot splash (plymouth, needs sudo)"
  if ask "   Install the CachyOS 7 boot splash (sudo bash scripts/splash-setup.sh)?"; then run sudo bash "$REPO/scripts/splash-setup.sh"; fi; fi
say "Done.$([ $DRY = 1 ] && echo ' (dry run - nothing was changed)')"
