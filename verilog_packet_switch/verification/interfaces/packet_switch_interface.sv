interface packet_switch_interface #(
    parameter int PACKET_WIDTH = 16 // Total number of bits in one packet
) (
    input logic clk // Clock shared by the DUT and verification environment
);

    // Reset control
    logic reset;

    // Four switch input ports
    logic [(4*PACKET_WIDTH)-1:0] input_packet;
    logic [3:0]                  input_valid;
    logic [3:0]                  input_ready;

    // Four switch output ports
    logic [(4*PACKET_WIDTH)-1:0] output_packet;
    logic [3:0]                  output_valid;
    logic [3:0]                  output_ready;

    // Signals used by the UVM driver on each rising clock edge.
    clocking driver_cb @(posedge clk);
        default input #1step output #0;

        output reset;
        output input_packet;
        output input_valid;
        output output_ready;

        input  input_ready;
        input  output_packet;
        input  output_valid;
    endclocking

    // Signals sampled by the UVM monitor on each rising clock edge.
    clocking monitor_cb @(posedge clk);
        default input #1step;

        input reset;
        input input_packet;
        input input_valid;
        input input_ready;
        input output_packet;
        input output_valid;
        input output_ready;
    endclocking

    // Verification components receive only the signals they are allowed to use.
    modport DRIVER  (clocking driver_cb);
    modport MONITOR (clocking monitor_cb);

    // Signal directions as seen by the packet-switch RTL.
    modport DUT (
        input  clk,
        input  reset,
        input  input_packet,
        input  input_valid,
        output input_ready,
        output output_packet,
        output output_valid,
        input  output_ready
    );

endinterface
