#
# this file is part of the software tool BOOT
# URL: freerangefactory.org
# (C) 2012 Fabrizio Tappero
#
import os
from subprocess import call

def make_vhdl_counter_project(_where):
    ''' make_vhdl_counter_project(_where):
        Create a _where folder and put in it two basic VHDL files as well as a
        constraints file. This is just to help beginners to get started 
        with boot.
    '''

    call('clear'.split())

    content_fl1 = '''--- ##### file: counter_top.vhdl #####
-- This is the VHDL top-level design file. This file defines the top-level 
-- entity of your VHDL design.
-- library
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all; 
 
-- entity
entity counter_top is
port (
     cout     :out std_logic_vector (7 downto 0); -- Output signal (bus)
     up_down  :in  std_logic;                     -- up down control for counter
     fpga_clk :in  std_logic;                     -- Input clock
     reset    :in  std_logic);                    -- Input reset
end entity;

-- architecture
architecture rtl of counter_top is
    signal count :std_logic_vector (7 downto 0);
    begin
        process (fpga_clk, reset) begin 
            if (reset = '1') then  
                count <= (others=>'0');
            elsif (rising_edge(fpga_clk)) then
                if (up_down = '1') then
                    count <= std_logic_vector(unsigned(count) + 1);
                else
                    count <= std_logic_vector(unsigned(count) - 1);
                end if;
            end if;
        end process;
        cout <= count;
end architecture;
'''

    content_fl2 = '''--- ##### file: counter_tb.vhdl #####
-- This is the test-bench file and is used to drive the simulation of 
-- your design. This file is not used during synthesis.
-- library
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- entity
entity counter_tb is
end entity;

-- architecture
architecture TB of counter_tb is
 
    component counter_top
    port( cout:     out std_logic_vector(7 downto 0);
          up_down:  in std_logic;
          reset:    in std_logic;
          fpga_clk: in std_logic);
    end component;
 
    signal cout:    std_logic_vector(7 downto 0);
    signal up_down: std_logic; 
    signal reset:   std_logic; 
    signal cin:     std_logic; 
 
begin
 
    dut: counter_top port map (cout, up_down, reset, cin); 
 
    process
    begin
        cin <= '0';  
        wait for 10 ns;
        cin <= '1';
        wait for 10 ns;
    end process;

    process
    begin
        up_down <= '1';
        reset <= '1';
        wait for 10 ns;
        reset <= '0';
        wait for 500 ns;
 
        up_down <= '0';
        wait for 500 ns;
    end process;
end;
'''

    content_fl3 = '''##### file: board.ucf #####
# This is a simplified version of a .ucf file that can be used
# for the Xula-200 board. 
# The Xula-200 board has a Spartan3A XC3S200A, VQ100, speed grade: -4

# used by counter_top.vhdl
net fpga_clk       loc = p43;
net cin            loc = p50;
net reset          loc = p52;
net up_down        loc = p56;
net cout<0>        loc = p57;
net cout<1>        loc = p61;
net cout<2>        loc = p62;

net sdram_clk      loc = p40;
net sdram_clk_fb   loc = p41;
net ras_n          loc = p59;
net cas_n          loc = p60;
net we_n           loc = p64;
net bs             loc = p53;

net a<0>           loc = p49;
net a<1>           loc = p48;
net a<2>           loc = p46;
net a<3>           loc = p31;
net a<4>           loc = p30;
net a<5>           loc = p29;
net a<6>           loc = p28;
net a<7>           loc = p27;

net fpga_clk       IOSTANDARD = LVTTL;
net sdram_clk      IOSTANDARD = LVTTL | SLEW=FAST | DRIVE=8;
net a*             IOSTANDARD = LVTTL | SLEW=SLOW | DRIVE=6;
net bs             IOSTANDARD = LVTTL | SLEW=SLOW | DRIVE=6;
net ras_n          IOSTANDARD = LVTTL | SLEW=SLOW | DRIVE=6;
net cas_n          IOSTANDARD = LVTTL | SLEW=SLOW | DRIVE=6;
net we_n           IOSTANDARD = LVTTL | SLEW=SLOW | DRIVE=6;

NET "fpga_clk" TNM_NET = "fpga_clk";
TIMESPEC "TS_fpga_clk" = PERIOD "fpga_clk" 83 ns HIGH 50%;

'''
    if not os.path.isdir(_where):
        try:
            # make a dir called _where
            os.path.os.mkdir(_where)
            # make a dir called build inside _where
            os.path.os.mkdir(os.path.join(_where,'build'))
        except:
            print 'Not able to create the directory:',_where, 'and its content.'
            return 1
    try:
        open(os.path.join(_where,'counter_top.vhdl'),'w').write(content_fl1)
        open(os.path.join(_where,'counter_tb.vhdl'),'w').write(content_fl2)
        open(os.path.join(_where,'board.ucf'),'w').write(content_fl3)            
    except:
        print 'Problems in writing. You might have permission problems or\n', \
                  'the "src" folder already exists.\n'
        return 1

    print 'Building a basic VHDL working environment.'
    return 0

    

