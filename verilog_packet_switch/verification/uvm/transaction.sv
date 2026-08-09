class packet_switch_transaction extends uvm_sequence_item;

    `uvm_object_utils(packet_switch_transaction)

    // Values driven into the packet switch.
    rand bit                              reset;
    rand bit [(PORT_COUNT*PACKET_WIDTH)-1:0] input_packet;
    rand bit [PORT_COUNT-1:0]             input_valid;
    rand bit [PORT_COUNT-1:0]             output_ready;

    // Values observed from the packet switch.
    bit [PORT_COUNT-1:0]                  input_ready;
    bit [(PORT_COUNT*PACKET_WIDTH)-1:0]   output_packet;
    bit [PORT_COUNT-1:0]                  output_valid;

    function new(string name = "packet_switch_transaction");
        super.new(name);
    endfunction

endclass
