#!/bin/sh

./makeself.sh ./ghdl_32 ghdl_lin32_installer.bin "GHDL" ./install.sh
mv ghdl_lin32_installer.bin ../installers/

./makeself.sh ./ghdl_64 ghdl_lin64_installer.bin "GHDL" ./install.sh
mv ghdl_lin64_installer.bin ../installers/
