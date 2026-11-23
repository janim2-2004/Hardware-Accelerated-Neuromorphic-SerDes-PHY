`default_nettype none
/*
pattern_gen --> bit_repeater --> tx_phy
*/
module tx_core
  import tx_pkg::*;
(
  input  logic       clk,         // clk_div
  input  logic       rst_n,       // active-low, synchronous
  input  logic       tx_en_i,       // TX_CTRL bit 0
  input  pattern_e   pattern_i,     // PATTERN register
  input  logic [7:0] bit_len_i,     // BIT_LEN register
  output logic [7:0] word_o,        // to tx_phy
  output logic       tx_bit,      // current bit (debug / ILA)
  output logic       bit_req      // bit taken this cycle (debug / ILA)
);

  logic run_n;
  assign run_n = rst_n & tx_en_i;

  pattern_gen u_pat (
    .clk              (clk),
    .rst_n            (run_n),
    .advance_i        (bit_req),
    .pattern_select_i (pattern_i),
    .bit_o            (tx_bit)
  );

  bit_repeater u_rep (
    .clk        (clk),
    .rst_n      (run_n),
    .bit_len_i  (bit_len_i),
    .next_bit_i (tx_bit),
    .bit_req_o  (bit_req),
    .word_o     (word_o)
  );

endmodule
`default_nettype wire
