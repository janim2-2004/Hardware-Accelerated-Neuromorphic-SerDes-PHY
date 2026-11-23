`default_nettype none

/*
bit_repeater : sets the TX bit rate

Holds each bit for a whole number of 10 ns words.
  bit_len_i (slots per bit, 1 slot = 1.25 ns), multiple of 8:
    32 -> 4 words = 40 ns = 25 Mbps
    16 -> 2 words = 20 ns = 50 Mbps
     8 -> 1 word  = 10 ns = 100 Mbps
  Values below 8 act as 8; the lowest 3 bits are ignored.

bit_req_o = 1 means "taking next_bit_i on this clock edge"
*/

module bit_repeater (
  input  logic       clk,         // clk_div (100 MHz)
  input  logic       rst_n,       // active-low, synchronous
  input  logic [7:0] bit_len_i,     // bit_len_i register
  input  logic       next_bit_i,    // the bit to send next
  output logic       bit_req_o,     // taking next_bit_i now
  output logic [7:0] word_o         // 8 slots for tx_phy
);

  logic [4:0] word_cnt;           // words left in the current bit
  logic [4:0] words_per_bit;

  assign words_per_bit = (bit_len_i[7:3] == '0) ? 5'd1 : bit_len_i[7:3]; //bit_len_i[7:3] divides the value by 8 (right shift by 3)
  assign bit_req_o       = (word_cnt == '0);                             // Request a new bit when the current bit has finished

  always_ff @(posedge clk) begin
    if (!rst_n) begin
      word_cnt <= '0;
      word_o     <= '0;
    end else if (bit_req_o) begin
      word_o     <= {8{next_bit_i}};            // all 8 slots = the new bit
      word_cnt <= words_per_bit - 1'b1;
    end else begin
      word_cnt <= word_cnt - 1'b1;          // keep sending the same word
    end
  end

endmodule
`default_nettype wire
