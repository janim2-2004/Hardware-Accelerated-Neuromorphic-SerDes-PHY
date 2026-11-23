`default_nettype none
/*
-----------------------------------------------------------------------------
tx_phy : TX serializer (test lane)

OSERDESE2 in 8:1 DDR mode.
  - Every clk_div cycle (10 ns) it loads one 8-bit word.
  - It shifts the 8 bits out on both edges of clk_fast (400 MHz),
    so each bit ("slot") lasts 1.25 ns.
  - word[0] (D1) goes out FIRST, word[7] (D8) last.

Outputs:
  oq  : serial stream for the pin. Must connect DIRECTLY to an output
        buffer (OBUF now, OBUFDS on LVDS pair A later). Nothing else.
  ofb : the same serial stream, fed back inside the chip. Connect it to an
        ISERDESE2 OFB input (OFB_USED = "TRUE") for the internal loopback.

Reset: rst_n is active low and synchronous to clk_div (from clk_rst_gen).
       OSERDESE2 wants an active-high reset released on a clk_div edge,
       which ~rst_n gives us.

The word input should come straight from a register clocked by clk_div.
-----------------------------------------------------------------------------
*/
module tx_phy (
  input  wire       clk_fast,   // 400 MHz (CLK)
  input  wire       clk_div,    // 100 MHz (CLKDIV), same MMCM as clk_fast
  input  wire       rst_n,      // active-low reset, synced to clk_div
  input  wire [7:0] word,       // 8 slots, word[0] is sent first
  output wire       oq,         // serial out -> main data output
  output wire       ofb         // serial feedback (ofb == output feedback) -> ISERDESE2.OFB (feedback instead of out to a pin)
);

  OSERDESE2 #(
    .DATA_RATE_OQ   ("DDR"),    // shift on both edges of CLK (DDR = double data rate)
    .DATA_RATE_TQ   ("SDR"),    // tristate path unused (SDR = single data rate)
    .DATA_WIDTH     (8),        // 8:1 serialization
    .INIT_OQ        (1'b0),     // output value after configuration
    .INIT_TQ        (1'b0),
    .SERDES_MODE    ("MASTER"), // single OSERDESE2, no width expansion
    .SRVAL_OQ       (1'b0),     // output value while in reset
    .SRVAL_TQ       (1'b0),
    .TBYTE_CTL      ("FALSE"),
    .TBYTE_SRC      ("FALSE"),
    .TRISTATE_WIDTH (1)
  ) u_oserdes (
    // serial outputs
    .OQ        (oq),
    .OFB       (ofb),
    // unused outputs
    .SHIFTOUT1 (),
    .SHIFTOUT2 (),
    .TBYTEOUT  (),
    .TFB       (),
    .TQ        (),
    // clocks and control
    .CLK       (clk_fast),
    .CLKDIV    (clk_div),
    .OCE       (1'b1),          // output clock enable: always on
    .RST       (~rst_n),        // active-high reset
    // parallel data: D1 goes out first
    .D1        (word[0]),
    .D2        (word[1]),
    .D3        (word[2]),
    .D4        (word[3]),
    .D5        (word[4]),
    .D6        (word[5]),
    .D7        (word[6]),
    .D8        (word[7]),
    // unused inputs (width expansion and tristate)
    .SHIFTIN1  (1'b0),
    .SHIFTIN2  (1'b0),
    .T1        (1'b0),
    .T2        (1'b0),
    .T3        (1'b0),
    .T4        (1'b0),
    .TBYTEIN   (1'b0),
    .TCE       (1'b0)
  );

endmodule
`default_nettype wire