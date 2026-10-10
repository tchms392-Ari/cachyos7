#!/usr/bin/env bash
# Undo scripts/splash-setup.sh.   Run: sudo bash scripts/splash-undo.sh
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Run with sudo: sudo bash $0"; exit 1; }
STATE=/var/lib/cachyos7
rest(){ if [ -e "$1.bak-cachyos7" ]; then mv -f "$1.bak-cachyos7" "$1"; echo "   restored $1"; return 0; fi; return 1; }
rest /etc/mkinitcpio.conf || true
if [ -f "$STATE/cmdline-changed" ]; then
  rest /etc/sdboot-manage.conf && sdboot-manage gen || true
  rest /etc/default/limine && limine-update || true
  rest /etc/default/grub && grub-mkconfig -o /boot/grub/grub.cfg || true
  rm -f "$STATE/cmdline-changed"; fi
prev=$(cat "$STATE/plymouth-prev-theme" 2>/dev/null || echo bgrt); echo "   restoring plymouth theme $prev"; plymouth-set-default-theme -R "$prev"
rm -rf /usr/share/plymouth/themes/cachyos7; rm -f "$STATE/plymouth-prev-theme"; echo "Done. Reboot."
