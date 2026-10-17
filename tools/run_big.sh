#!/bin/bash
# re-convert the five dense boards, dropping components under 3 mm so decimation does not shred them
cd /c/Users/Utsav/rp1-viewer
P=hw/pcb/02_PCB__
conv(){ python -I tools/step2mesh.py "$1" "hw/mesh/$2.npz" 3.0 0.3 2>&1 | tail -1; }
conv "${P}03_RBE-MAIN-RK3588S__03_3D_MAIN_2026-09-09.step" main &
conv "hw/bh/03_3D_BACKHUB_2026-09-28.step" backhub &
conv "${P}06_RBE-PWR-HEAD__03_3D_HEAD_2026-09-28.step" head &
conv "${P}11_RBE_PWR_140WCHG__03_3D_140WCHG_2026-09-16.step" chg140 &
conv "${P}07_RBE-PWR-HOTSWAP__03_3D_HOTSWAP_2026-09-18.step" hotswap &
wait
echo ALLDONE
