interface input_packet_queue_interface #(
    parameter int PACKET_WIDTH = 16
) (
    input logic clk
);

    // Queue control signals
    logic reset;
    logic push_packet;
    logic pop_packet;

    // Packet data signals
    logic [PACKET_WIDTH-1:0] incoming_packet;
    logic [PACKET_WIDTH-1:0] front_packet;

    // Queue status signals
    logic fifo_full;
    logic fifo_empty;

endinterface
