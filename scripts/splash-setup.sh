#!/usr/bin/env bash
# CachyOS 7 boot splash (plymouth).  Run: sudo bash scripts/splash-setup.sh   (or install.sh --with-splash)
# Checks before acting, prints every step, backs up edited files as <file>.bak-cachyos7.  Undo: sudo bash scripts/splash-undo.sh
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Run with sudo: sudo bash $0"; exit 1; }
REPO="$(cd "$(dirname "$0")/.." && pwd)"; STATE=/var/lib/cachyos7; mkdir -p "$STATE"
say(){ printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
bak(){ if [ -e "$1" ] && [ ! -e "$1.bak-cachyos7" ]; then cp -a "$1" "$1.bak-cachyos7"; echo "   backup: $1.bak-cachyos7"; fi; }
say "Plymouth boot splash"
command -v plymouth-set-default-theme >/dev/null || { echo "   plymouth is not installed. Arch/CachyOS: pacman -S plymouth ; Debian/Ubuntu: apt install plymouth ; Fedora: dnf install plymouth-plugin-script"; exit 1; }
T=/usr/share/plymouth/themes/cachyos7
[ -f "$STATE/plymouth-prev-theme" ] || plymouth-set-default-theme > "$STATE/plymouth-prev-theme"
echo "   previous theme: $(cat "$STATE/plymouth-prev-theme")"
rm -rf "$T"; install -d "$T"; install -m644 "$REPO"/assets/plymouth/cachyos7/* "$T/"; echo "   theme files -> $T"
REGEN_INITRD=1
if [ -f /etc/mkinitcpio.conf ]; then
  if grep -Eq '^HOOKS=.*\bplymouth\b' /etc/mkinitcpio.conf; then echo "   mkinitcpio HOOKS already contain plymouth"
  else bak /etc/mkinitcpio.conf; sed -i -E '/^HOOKS=/ s/\b(kms)\b/\1 plymouth/; /^HOOKS=/{/plymouth/! s/\bfilesystems\b/plymouth filesystems/}' /etc/mkinitcpio.conf
       echo "   added plymouth to HOOKS: $(grep ^HOOKS= /etc/mkinitcpio.conf)"; fi
elif command -v dracut >/dev/null || command -v update-initramfs >/dev/null; then echo "   dracut/initramfs-tools include plymouth automatically when it is installed"
else echo "   unknown initramfs generator - make sure plymouth is in your initramfs (manual)"; REGEN_INITRD=0; fi
add_args(){ # file var  -> adds quiet splash to VAR="..." in file
  local f=$1 v=$2 cur need=""; cur=$(grep -E "^$v=" "$f" | head -1 || true)
  for a in quiet splash; do echo "$cur" | grep -qw "$a" || need="$need $a"; done
  if [ -z "$need" ]; then echo "   $f: quiet splash already present"; return 1; fi
  bak "$f"; sed -i -E "s/^$v=\"(.*)\"/$v=\"\1$need\"/" "$f"; echo "   $f: added$need"; touch "$STATE/cmdline-changed"; return 0; }
if [ -f /etc/sdboot-manage.conf ] && command -v sdboot-manage >/dev/null; then echo "   bootloader: systemd-boot (sdboot-manage)"
  if add_args /etc/sdboot-manage.conf LINUX_OPTIONS; then sdboot-manage gen; fi
elif [ -f /etc/default/limine ] && command -v limine-update >/dev/null; then echo "   bootloader: limine"
  grep -qw splash /etc/default/limine && echo "   splash already set" || echo "   add 'quiet splash' to KERNEL_CMDLINE[default] in /etc/default/limine, then run limine-update (manual, skipped)"
elif [ -f /etc/default/grub ] && command -v grub-mkconfig >/dev/null; then echo "   bootloader: GRUB"
  if add_args /etc/default/grub GRUB_CMDLINE_LINUX_DEFAULT; then grub-mkconfig -o /boot/grub/grub.cfg; fi
elif grep -qw splash /proc/cmdline; then echo "   bootloader not recognised, but 'splash' is already on the kernel command line"
else echo "   bootloader not recognised - add 'quiet splash' to your kernel command line yourself (skipped)"; fi
if command -v mkinitcpio >/dev/null || [ $REGEN_INITRD = 1 ]; then echo "   setting theme cachyos7 + rebuilding initramfs"; plymouth-set-default-theme -R cachyos7
else plymouth-set-default-theme cachyos7; echo "   theme set; rebuild your initramfs manually"; fi
say "Done. Reboot to see it. Undo: sudo bash $REPO/scripts/splash-undo.sh"
