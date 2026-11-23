`timescale 1ps/1ps
`default_nettype none
// -----------------------------------------------------------------------------
// tb_tx_phy : self-checking testbench for tx_phy (OSERDESE2)
//
//   1. Makes a 400 MHz clk_fast and a 100 MHz clk_div with aligned rising edges.
//   2. Sends NWORDS words:
//        0-3 : 8'hF0  (100 MHz square wave)
//        4-7 : 8'hFF / 8'h00 alternating (50 MHz)
//        8   : 8'h01  (only the FIRST slot high: proves word[0] goes first)
//        rest: random
//   3. Samples oq and ofb in the middle of every 1.25 ns slot.
//   4. Finds the serializer delay (latency) and checks every slot sent came out.
// -----------------------------------------------------------------------------
module tb_tx_phy;

  import tx_pkg::*;

  localparam int NWORDS  = 200;
  localparam int NSLOTS  = NWORDS * 8;
  localparam int MAX_LAT = 128;              // largest delay searched, in slots

  // ---------------- clocks: both start high so rising edges line up ----------------
  logic clk_fast = 1'b1;
  logic clk_div  = 1'b1;
  always #(SLOT_PS)     clk_fast = ~clk_fast;   // 2.5 ns period = 400 MHz
  always #(4 * SLOT_PS) clk_div  = ~clk_div;    // 10 ns period  = 100 MHz

  // ---------------- DUT ----------------
  logic       rst_n = 1'b0;
  logic [7:0] word  = '0;
  logic       oq, ofb;

  tx_phy dut (.*);

  // ---------------- storage ----------------
  bit   exp_slot[$];                   // slots sent, in time order
  logic obs_slot[NSLOTS + MAX_LAT];    // slots seen on oq
  logic ofb_slot[NSLOTS + MAX_LAT];    // slots seen on ofb
  event started;

  // ---------------- stimulus ----------------
  initial begin
    logic [7:0] nxt;
    repeat (10) @(posedge clk_div);
    rst_n <= 1'b1;                     // release reset on a clk_div edge
    repeat (20) @(posedge clk_div);    // let the serializer settle

    -> started;
    for (int w = 0; w < NWORDS; w++) begin
      if      (w < 4)  nxt = 8'hF0;
      else if (w < 8)  nxt = (w % 2) ? 8'h00 : 8'hFF;
      else if (w == 8) nxt = 8'h01;
      else             nxt = 8'($urandom);
      for (int i = 0; i < 8; i++) exp_slot.push_back(nxt[i]);   // nxt[0] first
      word <= nxt;
      @(posedge clk_div);
    end
    word <= '0;
  end

  // ---------------- sampler + checker ----------------
  initial begin
    int found, errs, ofb_errs;

    @(started);
    #(SLOT_PS / 2);                    // middle of a slot
    for (int k = 0; k < NSLOTS + MAX_LAT; k++) begin
      obs_slot[k] = oq;
      ofb_slot[k] = ofb;
      #(SLOT_PS);
    end

    // smallest latency where every sent slot matches
    found = -1;
    for (int lat = 0; lat <= MAX_LAT && found < 0; lat++) begin
      errs = 0;
      foreach (exp_slot[s])
        if (obs_slot[s + lat] !== exp_slot[s]) errs++;
      if (errs == 0) found = lat;
    end

    // ofb must carry the same stream as oq
    ofb_errs = 0;
    foreach (obs_slot[k])
      if (ofb_slot[k] !== obs_slot[k]) ofb_errs++;

    if (found >= 0 && ofb_errs == 0)
      $display("PASS: %0d words / %0d slots matched, latency %0d slots (%0d ps), ofb == oq",
               NWORDS, NSLOTS, found, found * SLOT_PS);
    else if (found < 0)
      $error("FAIL: no latency from 0 to %0d slots makes oq match the sent slots", MAX_LAT);
    else
      $error("FAIL: oq is correct but ofb differs in %0d slots", ofb_errs);

    $finish;
  end

  // safety timeout
  initial begin
    #20_000_000;
    $error("FAIL: timeout");
    $finish;
  end

endmodule
`default_nettype wire
