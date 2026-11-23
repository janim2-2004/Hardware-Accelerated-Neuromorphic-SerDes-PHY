`timescale 1ns/1ps
`default_nettype none
// -----------------------------------------------------------------------------
// tb_pattern_gen : self-checking testbench for pattern_gen (Step 3)
//
// For each pattern: reset, take N bits (adv = 1 every clock), then check
//   PRBS7/15/23/31 : bit[n] = bit[n-a] ^ bit[n-b], roughly half ones
//   PRBS7          : repeats every 127 bits
//   ZEROS          : all zeros
//   ALT            : every bit differs from the previous one
//   RUNS32         : runs of exactly 32 equal bits
// -----------------------------------------------------------------------------
module tb_pattern_gen;

  import tx_pkg::*;

  localparam int N = 4000;

  logic     clk   = 1'b0;
  logic     rst_n = 1'b0;
  pattern_e sel   = PAT_PRBS7;
  logic     bit_out;

  always #5 clk = ~clk;   // 100 MHz

  pattern_gen dut (
    .clk     (clk),
    .rst_n   (rst_n),
    .adv     (1'b1),       // take a new bit every clock
    .sel     (sel),
    .bit_out (bit_out)
  );

  bit b[N];
  int fails = 0;

  // reset with a new pattern, then record N bits
  task automatic capture(input pattern_e s);
    rst_n = 1'b0;
    sel   = s;
    repeat (3) @(posedge clk);
    #1 rst_n = 1'b1;
    for (int i = 0; i < N; i++) begin
      b[i] = bit_out;        // the bit taken at the next edge
      @(posedge clk);
      #1;
    end
  endtask

  task automatic report(input bit ok, input string msg);
    if (ok) $display("PASS  %s", msg);
    else begin
      $error("FAIL  %s", msg);
      fails++;
    end
  endtask

  // check the PRBS rule bit[n] = bit[n-ta] ^ bit[n-tb]
  task automatic check_prbs(input pattern_e s, input int ta, input int tb);
    int errs = 0, ones = 0;
    capture(s);
    foreach (b[n]) if (b[n]) ones++;
    for (int n = ta; n < N; n++)
      if (b[n] !== (b[n-ta] ^ b[n-tb])) errs++;
    report(errs == 0 && ones > N/4 && ones < 3*N/4,
           $sformatf("%s: %0d rule errors, %0d ones in %0d bits", s.name(), errs, ones, N));
  endtask

  initial begin
    int errs, run, period;

    // PRBS7 + its period
    check_prbs(PAT_PRBS7, 7, 6);
    period = 0;
    for (int p = 1; p <= 200 && period == 0; p++) begin
      errs = 0;
      for (int n = 0; n < 1000; n++) if (b[n] !== b[n+p]) errs++;
      if (errs == 0) period = p;
    end
    report(period == 127, $sformatf("PRBS7 period = %0d (expected 127)", period));

    check_prbs(PAT_PRBS15, 15, 14);
    check_prbs(PAT_PRBS23, 23, 18);
    check_prbs(PAT_PRBS31, 31, 28);

    // all zeros
    capture(PAT_ZEROS);
    errs = 0;
    foreach (b[n]) if (b[n]) errs++;
    report(errs == 0, $sformatf("PAT_ZEROS: %0d non-zero bits", errs));

    // 1010...
    capture(PAT_ALT);
    errs = 0;
    for (int n = 1; n < N; n++) if (b[n] === b[n-1]) errs++;
    report(errs == 0, $sformatf("PAT_ALT: %0d places without a transition", errs));

    // runs of 32 (skip the last, possibly partial, run)
    capture(PAT_RUNS32);
    errs = 0;
    run  = 1;
    for (int n = 1; n < N; n++) begin
      if (b[n] === b[n-1]) run++;
      else begin
        if (run != 32) errs++;
        run = 1;
      end
    end
    report(errs == 0, $sformatf("PAT_RUNS32: %0d runs not 32 long", errs));

    if (fails == 0) $display("ALL PATTERN_GEN TESTS PASSED");
    else            $display("%0d PATTERN_GEN TEST(S) FAILED", fails);
    $finish;
  end

endmodule
`default_nettype wire
