#!/usr/bin/env bash
# Undo ~/CachyOS7/lightdm-setup.sh: back to GDM.   Run: sudo bash scripts/login-undo.sh   then reboot.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Run with sudo: sudo bash $0"; exit 1; }
U=${SUDO_USER:?run with sudo}; STATE=/var/lib/cachyos7; say(){ printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
rest(){ if [ -e "$1.bak-cachyos7" ]; then rm -rf "$1"; mv -f "$1.bak-cachyos7" "$1"; echo "   restored $1"; fi; }
say "Display manager"
prev=$(cat "$STATE/previous-dm" 2>/dev/null || echo gdm); [ "$prev" = none ] || [ "$prev" = lightdm ] && prev=gdm
systemctl disable lightdm 2>/dev/null || true; systemctl enable "$prev"; echo "   enabled $prev (active after reboot)"
say "Config"
rm -f /etc/lightdm/lightdm.conf.d/50-cachyos7.conf /usr/local/bin/cachyos7-greeter /usr/share/xgreeters/cachyos7-greeter.desktop
rest /etc/lightdm/lightdm-gtk-greeter.conf; rest /etc/lightdm/lightdm.conf
rest /var/lib/AccountsService/users/$U
if [ -e /var/lib/AccountsService/icons/$U.bak-cachyos7 ]; then rest /var/lib/AccountsService/icons/$U; fi
say "Theme copies"
for d in /usr/share/themes/CachyOS-7 /usr/share/themes/CachyOS-7-Greeter /usr/share/icons/CachyOS-7 /usr/share/icons/Windows-7 /usr/share/icons/Win7OS-cursors; do
  f="$STATE/created$(echo "$d" | tr / _)"
  if [ -f "$f" ]; then rm -rf "$d" "$f"; echo "   removed $d"; else rest "$d"; fi; done
rm -f /usr/share/backgrounds/cachyos7/cachyos7.png /usr/share/backgrounds/cachyos7/cachyos7-login.jpg
[ -f "$STATE/installed-lightdm" ] && echo "   lightdm packages were installed by setup; remove with: sudo pacman -Rns lightdm-gtk-greeter-settings lightdm-gtk-greeter lightdm"
rm -f "$STATE/previous-dm"
say "Done. Reboot to get GDM back."
