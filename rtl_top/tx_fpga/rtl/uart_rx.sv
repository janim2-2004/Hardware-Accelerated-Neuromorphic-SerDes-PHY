`default_nettype none
// -----------------------------------------------------------------------------
// uart_rx : serial receiver, 8N1 (Step 5)
//
// Idle line is high. A byte = start bit (0), 8 data bits (LSB first),
// stop bit (1), each CLKS_PER_BIT clocks long (868 at 115200 baud, 100 MHz).
// Waits for a falling edge, checks the line is still low half a bit later,
// then samples each bit in its middle. valid pulses for one clock when a byte
// with a good stop bit has arrived.
// -----------------------------------------------------------------------------
module uart_rx #(
  parameter int CLKS_PER_BIT = 868
) (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       rx,          // usb_rx pin
  output logic       valid,       // 1-cycle pulse: new byte in data
  output logic [7:0] data
);

  // rx is not timed to clk: 2-flip-flop synchronizer
  (* ASYNC_REG = "TRUE" *) logic rx_s1 = 1'b1;
  (* ASYNC_REG = "TRUE" *) logic rx_s2 = 1'b1;

  always_ff @(posedge clk) begin
    rx_s1 <= rx;
    rx_s2 <= rx_s1;
  end

  typedef enum logic [1:0] {S_IDLE, S_START, S_DATA, S_STOP} state_e;

  state_e      state;
  logic [15:0] cnt;      // clocks within the current bit
  logic [2:0]  idx;      // which data bit

  always_ff @(posedge clk) begin
    valid <= 1'b0;
    if (!rst_n) begin
      state <= S_IDLE;
      cnt   <= '0;
      idx   <= '0;
      data  <= '0;
    end else begin
      case (state)
        S_IDLE: begin
          cnt <= '0;
          if (!rx_s2) state <= S_START;                // line went low
        end

        S_START: begin                                 // middle of start bit
          if (cnt == 16'(CLKS_PER_BIT/2 - 1)) begin
            cnt <= '0;
            if (!rx_s2) begin
              idx   <= '0;
              state <= S_DATA;
            end else begin
              state <= S_IDLE;                         // glitch
            end
          end else cnt <= cnt + 1'b1;
        end

        S_DATA: begin                                  // middle of each data bit
          if (cnt == 16'(CLKS_PER_BIT - 1)) begin
            cnt       <= '0;
            data[idx] <= rx_s2;                        // LSB first
            if (idx == 3'd7) state <= S_STOP;
            else             idx   <= idx + 1'b1;
          end else cnt <= cnt + 1'b1;
        end

        S_STOP: begin
          if (cnt == 16'(CLKS_PER_BIT - 1)) begin
            cnt   <= '0;
            state <= S_IDLE;
            if (rx_s2) valid <= 1'b1;                  // good stop bit
          end else cnt <= cnt + 1'b1;
        end

        default: state <= S_IDLE;
      endcase
    end
  end

endmodule
`default_nettype wire
