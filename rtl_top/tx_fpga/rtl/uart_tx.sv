`default_nettype none
// -----------------------------------------------------------------------------
// uart_tx : serial transmitter, 8N1 (Step 5)
//
// Pulse start for one clock with the byte on data. busy stays high until the
// stop bit has been sent. The line idles high.
// -----------------------------------------------------------------------------
module uart_tx #(
  parameter int CLKS_PER_BIT = 868
) (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       start,       // 1-cycle pulse: send data
  input  logic [7:0] data,
  output logic       tx,          // usb_tx pin
  output logic       busy
);

  logic        tx_r = 1'b1;       // idle high even before the first reset
  logic [9:0]  shreg;             // {stop, data[7:0], start}, sent from bit 0
  logic [3:0]  nbit;              // which of the 10 bits is being sent
  logic [15:0] cnt;               // clocks within the current bit
  logic        active;

  assign tx   = tx_r;
  assign busy = active;

  always_ff @(posedge clk) begin
    if (!rst_n) begin
      tx_r   <= 1'b1;
      active <= 1'b0;
      shreg  <= '1;
      nbit   <= '0;
      cnt    <= '0;
    end else if (!active) begin
      tx_r <= 1'b1;                                  // idle high
      if (start) begin
        shreg  <= {1'b1, data, 1'b0};
        nbit   <= '0;
        cnt    <= '0;
        active <= 1'b1;
      end
    end else begin
      tx_r <= shreg[0];
      if (cnt == 16'(CLKS_PER_BIT - 1)) begin
        cnt   <= '0;
        shreg <= {1'b1, shreg[9:1]};                 // next bit
        if (nbit == 4'd9) active <= 1'b0;            // stop bit done
        else              nbit   <= nbit + 1'b1;
      end else cnt <= cnt + 1'b1;
    end
  end

endmodule
`default_nettype wire
