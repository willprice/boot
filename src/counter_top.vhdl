-- library
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all; 
 
-- entity
entity counter_top is
port (
     cout    :out std_logic_vector (7 downto 0);
     up_down :in  std_logic;               -- up down control for counter
     clk     :in  std_logic;               -- Input clock
     reset   :in  std_logic);              -- Input reset
end entity;

-- architecture
architecture rtl of counter_top is
    signal count :std_logic_vector (7 downto 0);
    begin
        process (clk, reset) begin 
            if (reset = '1') then  
                count <= (others=>'0');
            elsif (rising_edge(clk)) then
                if (up_down = '1') then
                    count <= std_logic_vector(unsigned(count) + 1);
                else
                    count <= std_logic_vector(unsigned(count) - 1);
                end if;
            end if;
        end process;
        cout <= count;
end architecture;

