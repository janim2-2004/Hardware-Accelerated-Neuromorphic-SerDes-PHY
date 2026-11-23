/*
Clock and Reset Generator
100 Mhz Crystal Clock --> MMCM (Mixed-Mode Clock Manager) --> 400 MHz (CLK) + 100 MHz (CLKDIV)
rst_n_o is held LOW until the MMCM is locked (the PLL is locked)
rst_n_o is held HIGH (synchronized to CLKDIV) once MMCM is locked

All the modules are held at reset when the MMCM is not locket yet.
This ensures that all the registers and modules are in a known state
*/

module clk_rst_gen (
    input clk_i,
    input rst_n_i,
    output clk_fast_o,
    output clk_div_o,
    output locked_o,
    output rst_n_o
);

clk_wiz_0 u_mmcm (
    .clk_in1  (clk_i),
    .resetn   (rst_n_i),   // button held -> MMCM resets -> locked drops
    .clk_out1 (clk_fast_o),
    .clk_out2 (clk_div_o),
    .locked   (locked_o)
);

reg [1:0] rst_sync = 2'b00;

// 2-flop syncronizer for reset signal
always @(posedge clk_div_o or negedge locked_o) begin
    if(!locked_o) rst_sync <= 2'b00;               // not locked
    else          rst_sync <= {rst_sync[0], 1'b1}; // locked
end

assign rst_n_o = rst_sync[1];

endmodule

