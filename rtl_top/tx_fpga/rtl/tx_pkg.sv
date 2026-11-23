// -----------------------------------------------------------------------------
// tx_pkg : shared constants and types for the TX design
//
// Every module that needs a register address, a reset default or a pattern
// code imports this package, so the numbers live in exactly one place.
// The Python script (sw/serdes_ctrl.py) uses the same addresses.
// -----------------------------------------------------------------------------
package tx_pkg;

  // ---------------- timing ----------------
  localparam int SLOT_PS          = 1250;   // one serializer slot = 1.25 ns
  localparam int SLOTS_PER_WORD   = 8;      // OSERDESE2 8:1
  localparam int CLKDIV_HZ        = 100_000_000;
  localparam int UART_BAUD        = 115_200;
  localparam int UART_CLKS_PER_BIT = CLKDIV_HZ / UART_BAUD;   // 868

  // ---------------- test patterns (PATTERN register) ----------------
  typedef enum logic [2:0] {
    PAT_PRBS7   = 3'd0,   // x^7  + x^6  + 1
    PAT_PRBS15  = 3'd1,   // x^15 + x^14 + 1
    PAT_PRBS23  = 3'd2,   // x^23 + x^18 + 1
    PAT_PRBS31  = 3'd3,   // x^31 + x^28 + 1
    PAT_ZEROS   = 3'd4,   // all zeros (no transitions)
    PAT_ALT     = 3'd5,   // 1010...
    PAT_RUNS32  = 3'd6,   // 32 ones, 32 zeros
    PAT_PRBS31B = 3'd7    // same as PRBS31
  } pattern_e;

  // ---------------- register addresses ----------------
  // TX registers 0x00-0x0F
  localparam logic [6:0] ADDR_TX_CTRL   = 7'h00;  // bit0 TX enable
  localparam logic [6:0] ADDR_PATTERN   = 7'h01;
  localparam logic [6:0] ADDR_BIT_LEN   = 7'h02;  // slots per bit
  localparam logic [6:0] ADDR_ERR_INJ   = 7'h03;  // Step 6
  // channel emulator registers 0x10-0x1F
  localparam logic [6:0] ADDR_CHEMU_CTRL = 7'h10;
  // TX status / debug 0x30-0x3F
  localparam logic [6:0] ADDR_OFB_STATUS = 7'h30; // bit0 locked, bit1 error flag
  localparam logic [6:0] ADDR_OFB_ERR_LO = 7'h31; // write any value = clear
  localparam logic [6:0] ADDR_OFB_ERR_HI = 7'h32;
  localparam logic [6:0] ADDR_ID         = 7'h3F;

  // ---------------- reset defaults ----------------
  localparam logic [7:0] TX_CTRL_RST    = 8'h01;   // TX enabled
  localparam pattern_e   PATTERN_RST    = PAT_PRBS7;
  localparam logic [7:0] BIT_LEN_RST    = 8'd32;   // 25 Mbps
  localparam logic [7:0] CHEMU_CTRL_RST = 8'h00;   // emulator off
  localparam logic [7:0] BOARD_ID       = 8'hA5;

endpackage
