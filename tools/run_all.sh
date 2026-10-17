#!/bin/bash
# convert each board STEP -> hw/mesh/<name>.npz  (args: min_diag_mm deflection_mm)
cd /c/Users/Utsav/rp1-viewer
conv(){ python -I tools/step2mesh.py "$1" "hw/mesh/$2.npz" "$3" "$4" 2>&1 | tail -1; }
export -f conv
P=hw/pcb/02_PCB__
printf '%s\n' \
 "${P}02_RBE-COMM-433TX__03_3D_433TX_2026-09-20.step|comm433|1.5|0.15" \
 "${P}03_RBE-MAIN-RK3588S__03_3D_MAIN_2026-09-09.step|main|1.5|0.2" \
 "${P}04_RBE-PWR-FAN__03_3D_FAN_V2.0.step|fan|1.5|0.15" \
 "${P}05_RBE-PWR-HANDPlusPro__03_3D_HAND.step|hand|1.5|0.15" \
 "${P}06_RBE-PWR-HEAD__03_3D_HEAD_2026-09-28.step|head|1.5|0.2" \
 "${P}07_RBE-PWR-HOTSWAP__03_3D_HOTSWAP_2026-09-18.step|hotswap|1.5|0.15" \
 "${P}08_RBE-PWR-MCAP__03_3D_MCAP_2026-09-16.step|mcap|1.2|0.15" \
 "${P}09_RBE-PWR-MINGMEI-BC__03_3D_MINGMEI-BC_2026-09-16.step|mingmei|1.0|0.15" \
 "${P}10_RBE-SENS-IMU__03_3D_IMU_2026-09-16.step|imu|1.5|0.15" \
 "${P}11_RBE_PWR_140WCHG__03_3D_140WCHG_2026-09-16.step|chg140|1.5|0.2" \
 "hw/bh/03_3D_BACKHUB_2026-09-28.step|backhub|1.5|0.2" \
 "${P}13_____03_3D_LAMP_2026-09-16.step|lamp|1.0|0.15" \
 "${P}14__________03_3D_INDICATOR_2026-09-16.step|indicator|1.0|0.15" \
 | xargs -P 4 -I{} bash -c 'IFS="|" read -r f n a b <<< "{}"; conv "$f" "$n" "$a" "$b"'
echo ALLDONE
