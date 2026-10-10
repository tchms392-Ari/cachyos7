#!/usr/bin/env bash
# CachyOS 7: switch the login screen from GDM to LightDM (lightdm-gtk-greeter), themed CachyOS 7.
# Run:  sudo bash scripts/login-setup.sh (or install.sh --with-login)      then REBOOT.     Undo: sudo bash scripts/login-undo.sh
# Every step checks first and prints what it does. Edited files are saved as <file>.bak-cachyos7.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Run with sudo: sudo bash $0"; exit 1; }
U=${SUDO_USER:?run with sudo from your user account}; H=$(getent passwd "$U" | cut -d: -f6)
REPO="$(cd "$(dirname "$0")/.." && pwd)"; A7="$REPO/assets"; STATE=/var/lib/cachyos7; mkdir -p "$STATE"
TH() { if [ -d "$H/$1" ]; then echo "$H/$1"; else echo "$2"; fi; }
say(){ printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
bak(){ if [ -e "$1" ] && [ ! -e "$1.bak-cachyos7" ]; then cp -a "$1" "$1.bak-cachyos7"; echo "   backup: $1.bak-cachyos7"; fi; }
copytree(){ # src dst  (records that we created it, for undo)
  if [ -d "$2" ] && [ ! -f "$STATE/created$(echo "$2" | tr / _)" ]; then echo "   $2 exists (not ours) - updating in place, original saved as $2.bak-cachyos7"; [ -e "$2.bak-cachyos7" ] || cp -a "$2" "$2.bak-cachyos7"; fi
  [ -d "$2" ] || touch "$STATE/created$(echo "$2" | tr / _)"
  mkdir -p "$2"; cp -a "$1/." "$2/"; chmod -R a+rX "$2"; echo "   $1 -> $2"; }

say "1. Packages"
if ! command -v pacman >/dev/null; then echo "   Not Arch/CachyOS: install lightdm + lightdm-gtk-greeter with your package manager, then re-run."; command -v lightdm >/dev/null || exit 1; fi
if command -v lightdm >/dev/null && [ -x /usr/bin/lightdm-gtk-greeter ] >/dev/null 2>&1; then echo "   lightdm + lightdm-gtk-greeter already installed"
else echo "   installing lightdm lightdm-gtk-greeter lightdm-gtk-greeter-settings"
  pacman -S --needed --noconfirm lightdm lightdm-gtk-greeter lightdm-gtk-greeter-settings || true
  for p in lightdm lightdm-gtk-greeter; do pacman -Q $p >/dev/null 2>&1 || { echo "!! $p failed to install - NOT switching. GDM stays your login screen."; exit 1; }; done
  touch "$STATE/installed-lightdm"; fi
[ -x /usr/bin/lightdm-gtk-greeter ] || { echo "!! /usr/bin/lightdm-gtk-greeter missing - NOT switching."; exit 1; }

say "2. Theme files system-wide (the greeter runs as user 'lightdm' and cannot read your home)"
copytree "$(TH .themes/CachyOS-7 "$A7/themes/CachyOS-7")" /usr/share/themes/CachyOS-7
copytree "$A7/themes/CachyOS-7-Greeter" /usr/share/themes/CachyOS-7-Greeter
copytree "$A7/icons/CachyOS-7" /usr/share/icons/CachyOS-7
copytree "$A7/icons/Windows-7" /usr/share/icons/Windows-7
copytree "$A7/icons/Win7OS-cursors" /usr/share/icons/Win7OS-cursors
for t in CachyOS-7 Windows-7; do gtk-update-icon-cache -qf /usr/share/icons/$t 2>/dev/null || rm -f /usr/share/icons/$t/icon-theme.cache; done
install -Dm644 "$A7/wallpapers/cachyos7-login.jpg" /usr/share/backgrounds/cachyos7/cachyos7-login.jpg
install -Dm644 "$A7/wallpapers/cachyos7-3840x2160.png" /usr/share/backgrounds/cachyos7/cachyos7.png
echo "   backgrounds -> /usr/share/backgrounds/cachyos7/"

say "3. Your picture on the login screen"
install -d /var/lib/AccountsService/icons /var/lib/AccountsService/users
I=/var/lib/AccountsService/icons/$U; A=/var/lib/AccountsService/users/$U
bak "$I"; FACE="$H/.face"; [ -f "$FACE" ] || FACE="$A7/avatar/cachyos7-avatar.png"; install -m644 "$FACE" "$I"; echo "   $FACE -> $I"
bak "$A"; touch "$A"; grep -q '^\[User\]' "$A" || echo '[User]' >> "$A"
for kv in "Icon=$I" "Session=xfce" "XSession=xfce"; do k=${kv%%=*}
  if grep -q "^$k=" "$A"; then sed -i "s|^$k=.*|$kv|" "$A"; else sed -i "/^\[User\]/a $kv" "$A"; fi; done
echo "   $A: Icon, Session=xfce"

say "4. Greeter config (2x for the 4K screen)"
install -Dm755 "$A7/greeter/cachyos7-greeter" /usr/local/bin/cachyos7-greeter
SC=$(grep -o 'WindowScalingFactor" type="int" value="[0-9]' "$H/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml" 2>/dev/null | grep -o '[0-9]$' || true); SC=${SC:-1}
sed -i "s/GDK_SCALE=2/GDK_SCALE=$SC/; s/XCURSOR_SIZE=48/XCURSOR_SIZE=$((24*SC))/" /usr/local/bin/cachyos7-greeter; echo "   greeter scale: ${SC}x (from your Xfce setting)"
install -Dm644 "$A7/greeter/cachyos7-greeter.desktop" /usr/share/xgreeters/cachyos7-greeter.desktop
bak /etc/lightdm/lightdm-gtk-greeter.conf; install -Dm644 "$A7/greeter/lightdm-gtk-greeter.conf" /etc/lightdm/lightdm-gtk-greeter.conf
echo "   /etc/lightdm/lightdm-gtk-greeter.conf written; greeter wrapper /usr/local/bin/cachyos7-greeter"
bak /etc/lightdm/lightdm.conf   # untouched, saved for safety
install -d /etc/lightdm/lightdm.conf.d
cat > /etc/lightdm/lightdm.conf.d/50-cachyos7.conf <<'C'
# CachyOS 7 (remove this file to undo)
[Seat:*]
greeter-session=cachyos7-greeter
user-session=xfce
greeter-hide-users=false
greeter-show-manual-login=true
C
echo "   /etc/lightdm/lightdm.conf.d/50-cachyos7.conf: greeter cachyos7-greeter, default session xfce, user list shown"
echo "   sessions offered: $(ls /usr/share/xsessions /usr/share/wayland-sessions 2>/dev/null | grep desktop | tr '\n' ' ')"
lightdm --show-config >/dev/null 2>&1 && echo "   lightdm config parses OK" || echo "   (lightdm --show-config not available; skipped check)"

say "5. Switch display manager (takes effect at next boot; your current session keeps running)"
cur=$(basename "$(readlink -f /etc/systemd/system/display-manager.service 2>/dev/null)" .service 2>/dev/null || echo none)
echo "$cur" > "$STATE/previous-dm"; echo "   current display manager: $cur"
if [ "$cur" != lightdm ]; then [ "$cur" != none ] && systemctl disable "$cur"; systemctl enable lightdm; fi
echo "   now enabled: $(basename "$(readlink -f /etc/systemd/system/display-manager.service)")"
say "Done. REBOOT to get the CachyOS 7 login screen.
If it does not appear: press Ctrl+Alt+F3, log in as $U, run  sudo bash $REPO/scripts/login-undo.sh  then  reboot"
