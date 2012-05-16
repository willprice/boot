--- ##### file: counter_top.vhdl #####
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
