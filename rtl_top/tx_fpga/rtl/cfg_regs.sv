`default_nettype none
/*
cfg_regs : register file + UART command decoder

Protocol (bytes from the PC):
  write : [0x80 | addr] [value]   -> register addr = value, no reply
  read  : [addr]  (bit 7 = 0)     -> FPGA replies with 1 byte

  0x00 TX_CTRL     R/W  bit0 TX enable
  0x01 PATTERN     R/W  pattern_e (0 = PRBS7 ...)
  0x02 BIT_LEN     R/W  slots per bit
  0x10 CHEMU_CTRL  R/W  stored only
  0x30 OFB_STATUS  R    bit0 locked, bit1 error flag
  0x31 OFB_ERR_LO  R    error count low byte (write any value = clear)
  0x32 OFB_ERR_HI  R    error count high byte
  0x3F ID          R    0xA5
*/
module cfg_regs
  import tx_pkg::*;
(
  input  logic        clk,
  input  logic        rst_n,
  // from uart_rx
  input  logic        rx_valid,
  input  logic [7:0]  rx_data,
  // to uart_tx
  output logic        tx_start,
  output logic [7:0]  tx_data,
  input  logic        tx_busy,
  // registers
  output logic [7:0]  tx_ctrl,
  output pattern_e    pattern,
  output logic [7:0]  bit_len,
  output logic [7:0]  chemu_ctrl,
  // status in
  input  logic        ofb_locked,
  input  logic        ofb_err_flag,
  input  logic [15:0] ofb_err_cnt,
  output logic        ofb_err_clr      // 1-cycle pulse
);

  typedef enum logic [1:0] {
    S_CMD,     // waiting for a command byte
    S_WDATA,   // waiting for the value of a write
    S_READ     // sending the reply of a read
  } state_e;

  state_e     state;
  logic [6:0] addr;
  logic [7:0] rdata;

  // value of the addressed register
  always_comb begin
    case (addr)
      ADDR_TX_CTRL:    rdata = tx_ctrl;
      ADDR_PATTERN:    rdata = {5'b00000, pattern};
      ADDR_BIT_LEN:    rdata = bit_len;
      ADDR_CHEMU_CTRL: rdata = chemu_ctrl;
      ADDR_OFB_STATUS: rdata = {6'b000000, ofb_err_flag, ofb_locked};
      ADDR_OFB_ERR_LO: rdata = ofb_err_cnt[7:0];
      ADDR_OFB_ERR_HI: rdata = ofb_err_cnt[15:8];
      ADDR_ID:         rdata = BOARD_ID;
      default:         rdata = 8'h00;
    endcase
  end

  always_ff @(posedge clk) begin
    tx_start    <= 1'b0;
    ofb_err_clr <= 1'b0;

    if (!rst_n) begin
      state      <= S_CMD;
      addr       <= '0;
      tx_data    <= '0;
      tx_ctrl    <= TX_CTRL_RST;
      pattern    <= PATTERN_RST;
      bit_len    <= BIT_LEN_RST;
      chemu_ctrl <= CHEMU_CTRL_RST;
    end else begin
      case (state)
        S_CMD: begin
          if (rx_valid) begin
            addr  <= rx_data[6:0];
            state <= rx_data[7] ? S_WDATA : S_READ;
          end
        end

        S_WDATA: begin
          if (rx_valid) begin
            case (addr)
              ADDR_TX_CTRL:    tx_ctrl     <= rx_data;
              ADDR_PATTERN:    pattern     <= pattern_e'(rx_data[2:0]);
              ADDR_BIT_LEN:    bit_len     <= rx_data;
              ADDR_CHEMU_CTRL: chemu_ctrl  <= rx_data;
              ADDR_OFB_ERR_LO: ofb_err_clr <= 1'b1;
              default: ;                               // read-only / unused
            endcase
            state <= S_CMD;
          end
        end

        S_READ: begin
          if (!tx_busy) begin
            tx_data  <= rdata;
            tx_start <= 1'b1;
            state    <= S_CMD;
          end
        end

        default: state <= S_CMD;
      endcase
    end
  end

endmodule
`default_nettype wire
