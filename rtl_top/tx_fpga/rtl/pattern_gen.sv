`default_nettype none

module pattern_gen
  import tx_pkg::*;
(
    input logic clk,
    input logic rst_n,
    input logic advance_i,            // Tells generator when to move to next bit
    input pattern_e pattern_select_i, // Which pattern to generate (from PATTERN register)
    output logic bit_o                // the current outputted bit
);

    logic [30:0] shift_reg;     // last 31 bits produced, shift_reg[0] = newest
    logic [5:0]  run_cnt;       // bit counter for the fixed patterns
    logic        feedback_bit;  // next PRBS bit

    // feedback = XOR of the two tap bits for the selected PRBS
    always_comb begin
    case (pattern_select_i)
        PAT_PRBS7:  feedback_bit = shift_reg[6]  ^ shift_reg[5];
        PAT_PRBS15: feedback_bit = shift_reg[14] ^ shift_reg[13];
        PAT_PRBS23: feedback_bit = shift_reg[22] ^ shift_reg[17];
        PAT_PRBS31: feedback_bit = shift_reg[30] ^ shift_reg[27];
        default:    feedback_bit = shift_reg[30] ^ shift_reg[27];   // PRBS31 
    endcase
    end

    // Shift Register Logic --> Shift bits only when advance_i signal is ON
    always_ff @(posedge clk) begin
    if (!rst_n) begin
        shift_reg    <= '1;                    // any non-zero start; all zeros would get stuck
        run_cnt <= '0;
    end else if (advance_i) begin
        shift_reg    <= {shift_reg[29:0], feedback_bit};      // shift the new bit in
        run_cnt <= run_cnt + 1'b1;
    end
    end

    // Pattern Select
    always_comb begin
    case (pattern_select_i)
        PAT_ZEROS:  bit_o = 1'b0;
        PAT_ALT:    bit_o = run_cnt[0];
        PAT_RUNS32: bit_o = run_cnt[5];
        default:    bit_o = feedback_bit;           // PRBS
    endcase
    end

endmodule
`default_nettype wire