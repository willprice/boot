#
# this file is part of the software tool BOOT
# URL: freerangefactory.org
# (C) 2012 Fabrizio Tappero
#
# Xilinx devices list:
# http://www.xilinx.com/support/index.htm

dev_manufacturer  = ['Xilinx'] # now, only Xilinx devices are supported
#dev_manufacturer  = ['Xilinx', 'Altera', 'Actel']

dev_family=['Spartan6','Spartan3','Spartan3A','Spartan3E','Artix','Kintex',
            'Virtex4','Virtex5','Virtex6','Virtex7','Zynq','CoolRunner',
            'XC9500X']

dev_device=['Zynq7000 XC7Z010','Zynq7000 XC7Z020','Zynq7000 XC7Z030',
            'Zynq7000 XC7Z045','Artix7 XC7A100T','Artix7 XC7A200T',
            'Artix7 XC7A350T','Kintex7 XC7K70T','Kintex7 XC7K160T',
            'Kintex7 XC7K325T','Kintex7 XC7K355T','Kintex7 XC7K410T',
            'Kintex7 XC7K420T','Kintex7 XC7K480T','Virtex7 XC7V585T',
            'Virtex7 XC7V1500T','Virtex7 XC7V2000T','Virtex7 XC7VX330T',
            'Virtex7 XC7VX415T','Virtex7 XC7VX485T','Virtex7 XC7VX550T',
            'Virtex7 XC7VX690T','Virtex7 XC7VX980T','Virtex7 XC7VX1140T',
            'Virtex7 XC7VH290T','Virtex7 XC7VH580T','Virtex7 XC7VH870T',
            'Virtex6 XC6VLX75T','Virtex6 XC6VLX130T','Virtex6 XC6VLX195T',
            'Virtex6 XC6VLX240T ','Virtex6 XC6VLX365T','Virtex6 XC6VLX550T',
            'Virtex6 XC6VLX760','Virtex6 XC6VSX315T','Virtex6 XC6VSX475T',
            'Virtex6 XC6VHX250T','Virtex6 XC6VHX255T','Virtex6 XC6VHX380T',
            'Virtex6 XC6VHX565T','Virtex6Q XQ6VLX130T','Virtex6Q XQ6VLX240T',
            'Virtex6Q XQ6VLX550T','Virtex6Q XQ6VSX315T','Virtex6Q XQ6VSX475T',
            'Virtex5 XC5VLX30','Virtex5 XC5VLX50','Virtex5 XC5VLX85',
            'Virtex5 XC5VLX110','Virtex5 XC5VLX155','Virtex5 XC5VLX220',
            'Virtex5 XC5VLX330','Virtex5 XC5VLX20T','Virtex5 XC5VLX30T',
            'Virtex5 XC5VLX50T','Virtex5 XC5VLX85T','Virtex5 XC5VLX110T',
            'Virtex5 XC5VLX155T','Virtex5 XC5VLX220T','Virtex5 XC5VLX330T',
            'Virtex5 XC5VSX35T','Virtex5 XC5VSX50T','Virtex5 XC5VSX95T',
            'Virtex5 XC5VSX240T','Virtex5 XC5VFX30T','Virtex5 XC5VFX70T',
            'Virtex5 XC5VFX100T','Virtex5 XC5VFX130T','Virtex5 XC5VFX200T',
            'Virtex5Q XQ5VLX85','Virtex5Q XQ5VLX110','Virtex5Q XQ5VLX30T',
            'Virtex5Q XQ5VLX110T','Virtex5Q XQ5VLX155T','Virtex5Q XQ5VLX220T',
            'Virtex5Q XQ5VLX330T','Virtex5Q XQ5VSX50T','Virtex5Q XQ5VSX95T',
            'Virtex5Q XQ5VSX240T','Virtex5Q XQ5VFX70T','Virtex5Q XQ5VFX100T',
            'Virtex5Q XQ5VFX130T','Virtex5Q XQ5VFX200T','Virtex5QV XQR5VFX130',
            'Virtex4 XC4VLX15','Virtex4 XC4VLX25','Virtex4 XC4VLX40',
            'Virtex4 XC4VLX60','Virtex4 XC4VLX80','Virtex4 XC4VLX100',
            'Virtex4 XC4VLX160','Virtex4 XC4VLX200','Virtex4 XC4VSX25',
            'Virtex4 XC4VSX35','Virtex4 XC4VSX55','Virtex4 XC4VFX12',
            'Virtex4 XC4VFX20','Virtex4 XC4VFX40','Virtex4 XC4VFX60',
            'Virtex4 XC4VFX100','Virtex4 XC4VFX140','Virtex4Q XQ4VLX25',
            'Virtex4Q XQ4VLX40','Virtex4Q XQ4VLX60','Virtex4Q XQ4VLX80',
            'Virtex4Q XQ4VLX100','Virtex4Q XQ4VLX160','Virtex4Q XQ4VSX55',
            'Virtex4Q XQ4VFX60','Virtex4Q XQ4VFX100','Virtex4QV XQR4VSX55',
            'Virtex4QV XQR4VFX60','Virtex4QV XQR4VFX140','Virtex4QV XQR4VLX200',
            'Spartan6 XC6SLX4','Spartan6 XC6SLX9','Spartan6 XC6SLX16',
            'Spartan6 XC6SLX25','Spartan6 XC6SLX45','Spartan6 XC6SLX75',
            'Spartan6 XC6SLX100','Spartan6 XC6SLX150','Spartan6 XC6SLX25T',
            'Spartan6 XC6SLX45T','Spartan6 XC6SLX75T','Spartan6 XC6SLX100T',
            'Spartan6 XC6SLX150T','Spartan6Q XQ6SLX75','Spartan6Q XQ6SLX150',
            'Spartan6Q XQ6SLX75T','Spartan6Q XQ6SLX150T',
            'Spartan3A_DSP XC3SD1800A','Spartan3A_DSP XC3SD3400A',
            'Spartan3AN XC3S50AN','Spartan3AN XC3S200AN','Spartan3AN XC3S400AN',
            'Spartan3AN XC3S700AN','Spartan3AN XC3S1400AN','Spartan3A XC3S50A',
            'Spartan3A XC3S200A','Spartan3A XC3S400A','Spartan3A XC3S700A',
            'Spartan3A XC3S1400A','Spartan3L XC3S1000L','Spartan3L XC3S1500L',
            'Spartan3L XC3S4000L','Spartan3E XC3S100E','Spartan3E XC3S250E',
            'Spartan3E XC3S500E','Spartan3E XC3S1200E','Spartan3E XC3S1600E',
            'Spartan3 XC3S50','Spartan3 XC3S200','Spartan3 XC3S400',
            'Spartan3 XC3S1000','Spartan3 XC3S1500','Spartan3 XC3S2000',
            'Spartan3 XC3S4000','Spartan3 XC3S5000','CoolRunnerII XC2C32A',
            'CoolRunnerII XC2C64A','CoolRunnerII XC2C128',
            'CoolRunnerII XC2C256','CoolRunnerII XC2C384',
            'CoolRunnerII XC2C512','XC9500XL XC9536XL','XC9500XL XC9572XL',
            'XC9500XL XC95144XL','XC9500XL XC95288XL']


dev_package=['BG256','CP132','CP56','CPG132','CPG196','CPG236','CS144','CS280',
             'CS48','CS484','CSG144','CSG225','CSG324','CSG484','FBG484',
             'FBG676','FBG900','FF1136','FF1136','FF1148','FF1152','FF1153',
             'FF1154','FF1155','FF1156','FF1517','FF1738','FF1759','FF1760',
             'FF1760','FF1923','FF1924','FF323','FF324','FF484','FF665','FF668',
             'FF672','FF676','FF784','FFG1155','FFG1156','FFG1157','FFG1158',
             'FFG1159','FFG1761','FFG1925','FFG1926','FFG1927','FFG1928',
            'FFG1929','FFG1930','FFG1931','FFG1932','FFG484','FFG676','FFG784',
            'FFG900','FG208','FG256','FG320','FG324','FG400','FG456','FG484',
            'FG484','FG676','FG900','FGG484','FGG676','FGG784','FGG900','FT256',
            'FTG256','PC44','PQ208','PQG208','QF32','QF48','RF1156','RF1759',
            'RF784','SBG324','SF363','TQ100','TQ144','TQG100','TQG144','VQ100',
            'VQ44','VQ64','VQG100']


dev_speed = ['-L1','-1','-2','-3','-3N','-4','-5','-6','-7','-10','-11','-12']



