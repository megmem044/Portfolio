package packet_switch_parameters_pkg;

    parameter int PACKET_WIDTH      = 16; // Total number of bits in one packet
    parameter int PORT_COUNT        = 4;  // Number of switch inputs and outputs
    parameter int FIFO_DEPTH        = 4;  // Number of packets stored at each input
    parameter int DESTINATION_WIDTH = 2;  // Bits used to identify one of four outputs

endpackage
