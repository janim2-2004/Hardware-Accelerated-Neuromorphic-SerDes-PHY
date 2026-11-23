`default_nettype none
// -----------------------------------------------------------------------------
// top : TX bring-up, Steps 1-5
//
//   clk_rst_gen -> clocks + reset
//   uart_rx/uart_tx + cfg_regs -> registers set from the PC
//   tx_core (pattern_gen + bit_repeater) -> 8-slot words
//   tx_phy (OSERDESE2) -> serial stream
//       oq  -> OBUF -> led[7] pin  (TEMPORARY single-ended output)
//       ofb -> ofb_check (ISERDESE2 + compare): internal loopback
//
// LEDs
//   0 MMCM locked              4 loopback error seen (cleared by reg 0x31)
//   1 1 Hz blink (clk_div)     5 toggles on every byte received over UART
//   2 in reset                 6 TX enabled (TX_CTRL bit 0)
//   3 loopback locked          7 serializer output (glows when sending)
//
// SIM = 1 is only for simulation: faster UART and faster loopback lock.
// -----------------------------------------------------------------------------
module top
  import tx_pkg::*;
#(
  parameter int SIM = 0
) (
  input  wire       clk,      // 100 MHz board clock (only goes to the MMCM)
  input  wire       rst_n,    // reset button, active low
  output wire [7:0] led,
  input  wire       usb_rx,   // from PC
  output wire       usb_tx    // to PC
);

  localparam int CLKS_PER_BIT = (SIM != 0) ? 16 : UART_CLKS_PER_BIT;
  localparam int LOCK_WORDS   = (SIM != 0) ? 64 : 1024;

  // ---------------- clocks and reset ----------------
  logic clk_fast, clk_div, locked, rst_n_sync;

  clk_rst_gen u_clk (
    .clk_i      (clk),
    .rst_n_i    (rst_n),
    .clk_fast_o (clk_fast),
    .clk_div_o  (clk_div),
    .locked_o   (locked),
    .rst_n_o    (rst_n_sync)
  );

  // ---------------- 1 Hz blink on clk_div ----------------
  logic [25:0] div_cnt;
  logic        led_1hz;

  always_ff @(posedge clk_div) begin
    if (!rst_n_sync) begin
      div_cnt <= '0;
      led_1hz <= 1'b0;
    end else if (div_cnt == 26'd49_999_999) begin
      div_cnt <= '0;
      led_1hz <= ~led_1hz;
    end else begin
      div_cnt <= div_cnt + 1'b1;
    end
  end

  // ---------------- UART + registers ----------------
  logic       rx_valid;
  logic [7:0] rx_data;
  logic       utx_start, utx_busy;
  logic [7:0] utx_data;

  uart_rx #(.CLKS_PER_BIT(CLKS_PER_BIT)) u_urx (
    .clk   (clk_div),
    .rst_n (rst_n_sync),
    .rx    (usb_rx),
    .valid (rx_valid),
    .data  (rx_data)
  );

  uart_tx #(.CLKS_PER_BIT(CLKS_PER_BIT)) u_utx (
    .clk   (clk_div),
    .rst_n (rst_n_sync),
    .start (utx_start),
    .data  (utx_data),
    .tx    (usb_tx),
    .busy  (utx_busy)
  );

  logic [7:0]  tx_ctrl, bit_len, chemu_ctrl;
  pattern_e    pattern;
  logic        ofb_locked, ofb_err_flag, ofb_err_clr;
  logic [15:0] ofb_err_cnt;

  cfg_regs u_cfg (
    .clk          (clk_div),
    .rst_n        (rst_n_sync),
    .rx_valid     (rx_valid),
    .rx_data      (rx_data),
    .tx_start     (utx_start),
    .tx_data      (utx_data),
    .tx_busy      (utx_busy),
    .tx_ctrl      (tx_ctrl),
    .pattern      (pattern),
    .bit_len      (bit_len),
    .chemu_ctrl   (chemu_ctrl),
    .ofb_locked   (ofb_locked),
    .ofb_err_flag (ofb_err_flag),
    .ofb_err_cnt  (ofb_err_cnt),
    .ofb_err_clr  (ofb_err_clr)
  );

  // ---------------- TX data path ----------------
  logic [7:0] tx_word;
  logic       tx_bit, bit_req;

  tx_core u_txc (
    .clk       (clk_div),
    .rst_n     (rst_n_sync),
    .tx_en_i   (tx_ctrl[0]),
    .pattern_i (pattern),
    .bit_len_i (bit_len),
    .word_o    (tx_word),
    .tx_bit    (tx_bit),
    .bit_req   (bit_req)
  );

  // ---------------- serializer ----------------
  logic tx_oq, tx_ofb;

  tx_phy u_tx (
    .clk_fast (clk_fast),
    .clk_div  (clk_div),
    .rst_n    (rst_n_sync),
    .word     (tx_word),
    .oq       (tx_oq),
    .ofb      (tx_ofb)
  );

  // TEMPORARY output buffer: single-ended LVCMOS33 on led[7] (pin P14).
  // Replace with OBUFDS on LVDS pair A once the breakout + 2.5 V jumper are in.
  OBUF #(.IOSTANDARD("LVCMOS33")) u_txbuf (
    .I (tx_oq),
    .O (led[7])
  );

  // ---------------- internal loopback check: removed for now ----------------
  // Status registers report "not locked, no errors" until ofb_check returns.
  assign ofb_locked   = 1'b0;
  assign ofb_err_flag = 1'b0;
  assign ofb_err_cnt  = '0;

  // ---------------- LEDs ----------------
  logic rx_toggle;

  always_ff @(posedge clk_div) begin
    if (!rst_n_sync)   rx_toggle <= 1'b0;
    else if (rx_valid) rx_toggle <= ~rx_toggle;
  end

  assign led[0] = locked;
  assign led[1] = led_1hz;
  assign led[2] = ~rst_n_sync;
  assign led[3] = ofb_locked;
  assign led[4] = ofb_err_flag;
  assign led[5] = rx_toggle;
  assign led[6] = tx_ctrl[0];

endmodule
`default_nettype wire
