`timescale 1ps/1ps
`default_nettype none
// -----------------------------------------------------------------------------
// tb_top : whole-design simulation, Steps 1-5
//
// Runs the real top (MMCM, UART, registers, PRBS, serializer, deserializer
// loopback) with SIM = 1, which only makes the UART faster (16 clocks per bit)
// and the loopback lock faster (64 words).
//
// The testbench acts like the PC (UART on usb_rx / usb_tx, same protocol as
// serdes_ctrl.py) and like a scope (samples led[7] every slot, rebuilds bits).
//
// Checks: MMCM lock, loopback lock, ID / BIT_LEN / PATTERN reads, 25 Mbps
// output (32-slot bits, PRBS7 rule), BIT_LEN write, 50 Mbps output, loopback
// still locked with 0 errors.
// -----------------------------------------------------------------------------
module tb_top;

  import tx_pkg::*;

  localparam int CPB    = 16;            // must match CLKS_PER_BIT in top (SIM = 1)
  localparam int BIT_PS = CPB * 10_000;  // one UART bit = 16 x 10 ns

  // ---------------- board ----------------
  logic       clk    = 1'b0;
  logic       rst_n  = 1'b0;
  logic       usb_rx = 1'b1;             // UART line idles high
  wire        usb_tx;
  wire  [7:0] led;

  always #5000 clk = ~clk;               // 100 MHz oscillator

  top #(.SIM(1)) dut (.*);

  int fails = 0;

  task automatic report(input bit ok, input string msg);
    if (ok) $display("PASS  %s", msg);
    else begin
      $error("FAIL  %s", msg);
      fails++;
    end
  endtask

  // ---------------- UART helpers (act like the PC) ----------------
  task automatic uart_send(input logic [7:0] b);
    usb_rx = 1'b0;                       // start bit
    #(BIT_PS);
    for (int i = 0; i < 8; i++) begin    // data, LSB first
      usb_rx = b[i];
      #(BIT_PS);
    end
    usb_rx = 1'b1;                       // stop bit
    #(BIT_PS);
  endtask

  task automatic uart_recv(output logic [7:0] b);
    @(negedge usb_tx);                   // start bit begins
    #(BIT_PS / 2);                       // middle of start bit
    for (int i = 0; i < 8; i++) begin
      #(BIT_PS);                         // middle of each data bit
      b[i] = usb_tx;
    end
    #(BIT_PS);                           // stop bit
  endtask

  task automatic write_reg(input logic [6:0] addr, input logic [7:0] value);
    uart_send({1'b1, addr});
    uart_send(value);
    #(BIT_PS * 2);
  endtask

  task automatic read_reg(input logic [6:0] addr, output logic [7:0] value);
    logic [7:0] v;
    fork                                  // reply can start before our stop bit ends
      uart_send({1'b0, addr});
      uart_recv(v);
    join
    value = v;
    #(BIT_PS * 2);
  endtask

  task automatic expect_reg(input logic [6:0] addr, input logic [7:0] expected, input string name);
    logic [7:0] v;
    read_reg(addr, v);
    report(v === expected,
           $sformatf("read %s (0x%02h) = 0x%02h, expected 0x%02h", name, addr, v, expected));
  endtask

  // ---------------- output checker (acts like a scope) ----------------
  // Samples led[7] in the middle of every slot, turns runs of equal slots
  // into bits, and checks bit length and the PRBS7 rule.
  task automatic check_stream(input int bitlen, input int nbits);
    bit   bits[$];
    int   run = 1, len_errs = 0, prbs_errs = 0;
    logic prev, cur;
    bit   first = 1'b1;                  // first run is only partly seen: skip it

    @(led[7]);                           // an edge = start of a slot
    #(SLOT_PS / 2);                      // middle of the slot
    prev = led[7];

    while (bits.size() < nbits) begin
      #(SLOT_PS);
      cur = led[7];
      if (cur === prev) run++;
      else begin
        if (!first) begin
          if (run % bitlen != 0) begin
            len_errs++;
            if (len_errs <= 5) $display("        run of %0d slots is not a multiple of %0d", run, bitlen);
          end
          repeat (run / bitlen) bits.push_back(prev);
        end
        first = 1'b0;
        run   = 1;
        prev  = cur;
      end
    end

    for (int k = 7; k < nbits; k++)
      if (bits[k] !== (bits[k-7] ^ bits[k-6])) prbs_errs++;

    report(len_errs == 0 && prbs_errs == 0,
           $sformatf("output: %0d bits of %0d slots, %0d length errors, %0d PRBS7 errors",
                     nbits, bitlen, len_errs, prbs_errs));
  endtask

  // ---------------- main test ----------------
  initial begin
    $display("---- tb_top start ----");
    repeat (20) @(posedge clk);
    rst_n = 1'b1;

    // 1. MMCM lock
    wait (led[0] === 1'b1);
    $display("PASS  MMCM locked at %0t ps", $time);

    // 2. internal loopback lock (200 us limit)
    fork
      begin
        wait (led[3] === 1'b1);
        $display("PASS  OFB loopback locked at %0t ps", $time);
      end
      begin
        #200_000_000;
        report(1'b0, "OFB loopback did not lock within 200 us");
      end
    join_any
    disable fork;

    // 3. registers
    expect_reg(ADDR_ID,      BOARD_ID,    "ID");
    expect_reg(ADDR_BIT_LEN, BIT_LEN_RST, "BIT_LEN");
    expect_reg(ADDR_PATTERN, 8'(PATTERN_RST), "PATTERN");

    // 4. output at 25 Mbps
    check_stream(32, 200);

    // 5. change to 50 Mbps
    write_reg(ADDR_BIT_LEN, 8'd16);
    expect_reg(ADDR_BIT_LEN, 8'd16, "BIT_LEN");
    #2_000_000;                          // let the old bit finish
    check_stream(16, 400);

    // 6. loopback still good
    expect_reg(ADDR_OFB_STATUS, 8'h01, "OFB_STATUS");   // locked, no error flag
    expect_reg(ADDR_OFB_ERR_LO, 8'h00, "OFB_ERR_LO");
    expect_reg(ADDR_OFB_ERR_HI, 8'h00, "OFB_ERR_HI");

    if (fails == 0) $display("==== ALL TOP-LEVEL TESTS PASSED ====");
    else            $display("==== %0d TOP-LEVEL TEST(S) FAILED ====", fails);
    $finish;
  end

  // safety timeout: 3 ms
  initial begin
    repeat (3000) #1_000_000;
    $error("FAIL  timeout (3 ms of simulated time)");
    $finish;
  end

endmodule
`default_nettype wire
