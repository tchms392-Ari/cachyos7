#!/usr/bin/env bash
# CachyOS 7 uninstall.  Usage: ./uninstall.sh [--dry-run] [--remove-login] [--remove-splash] [--remove-assets]
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"; DRY=0 RL=0 RS=0 RA=0
for a in "$@"; do case $a in --dry-run) DRY=1;; --remove-login) RL=1;; --remove-splash) RS=1;; --remove-assets) RA=1;; *) echo "unknown $a"; exit 2;; esac; done
run(){ if [ $DRY = 1 ]; then echo "  [dry-run] $*"; else "$@"; fi; }
B=$(cat "$HOME/.local/share/cachyos7-backup/LAST" 2>/dev/null || true)
if [ -d "$B" ]; then echo "Restoring settings from $B"
  run rm -rf "$HOME/.config/xfce4"; run rsync -a "$B/" "$HOME/"
else echo "No backup found - removing the CachyOS 7 Xfce config (stock Xfce next login)"; run mv "$HOME/.config/xfce4" "$HOME/.config/xfce4.cachyos7-removed-$(date +%s)" || true; fi
if grep -q '^# --- CachyOS 7: HiDPI/Qt' "$HOME/.xprofile" 2>/dev/null && [ ! -f "$B/.xprofile" ]; then
  [ $DRY = 1 ] && echo "  [dry-run] remove CachyOS 7 block from ~/.xprofile" || sed -i '/^# --- CachyOS 7: HiDPI\/Qt/,/^# --- end CachyOS 7 ---/d' "$HOME/.xprofile"; fi
if [ $RA = 1 ]; then for d in .themes/CachyOS-7 .themes/CachyOS-7-Aero .themes/CachyOS-7-Aero-xhdpi .icons/CachyOS-7 .icons/Windows-7 .icons/Win7OS-cursors .local/share/sounds/CachyOS-7 .local/share/backgrounds/cachyos7 .local/share/cachyos7; do run rm -rf "$HOME/$d"; done; fi
[ $RL = 1 ] && run sudo bash "$REPO/scripts/login-undo.sh"
[ $RS = 1 ] && run sudo bash "$REPO/scripts/splash-undo.sh"
echo "Done. Log out and back in."
