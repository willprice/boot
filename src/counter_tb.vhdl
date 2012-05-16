--- ##### file: counter_tb.vhdl #####
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
