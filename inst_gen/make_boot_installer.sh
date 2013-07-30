#!/bin/sh
#
# GENERATE BOOT INSTALLER FOR LINUX 32 BIT AND 64 BIT
#
# the boot installer is actually the same, what changes between 32 and 64 is
# is the version of GHDL that gets packed in it

mkdir -p tmp tmp/boot
cp ../boot_scr/* tmp/boot/
rm tmp/boot/*~

# add GHDL 32 bit binary files
cp -vR ../ghdl/ghdl_32 tmp/

# 32 BIT
echo "#!/bin/sh
# GHDL 
cp -vR ./ghdl_32/usr/* /usr/

# BOOT
rm -Rf /opt/boot
cp -vR ./boot /opt/
cp ./boot/boot /usr/local/bin/
cp ./boot/boot.desktop /usr/share/applications/boot.desktop
cp ./boot/boot-icon.png /usr/share/pixmaps/boot-icon.png
cp ./boot/boot-icon.svg /usr/share/pixmaps/boot-icon.svg
" > tmp/install.sh

chmod a+x ./tmp/install.sh
./makeself.sh ./tmp boot_lin32_installer.bin "Boot" ./install.sh
mv boot_lin32_installer.bin ../installers/

# add GHDL 64 bit binary files
rm -Rf tmp/ghdl_32
cp -vR ../ghdl/ghdl_64 tmp/

# 64 BIT
echo "#!/bin/sh
# GHDL 
cp -vR ./ghdl_64/usr/* /usr/

# BOOT
rm -Rf /opt/boot
cp -vR ./boot /opt/
cp ./boot/boot /usr/local/bin/
cp ./boot/boot.desktop /usr/share/applications/boot.desktop
cp ./boot/boot-icon.png /usr/share/pixmaps/boot-icon.png
cp ./boot/boot-icon.svg /usr/share/pixmaps/boot-icon.svg
" > ./tmp/install.sh

chmod a+x ./tmp/install.sh
./makeself.sh ./tmp boot_lin64_installer.bin "Boot" ./install.sh
mv boot_lin64_installer.bin ../installers/

rm -rf ./tmp

