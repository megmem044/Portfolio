`timescale 1ns/1ps

module top;

    import uvm_pkg::*;
    import packet_switch_parameters_pkg::*;
    import packet_switch_uvm_pkg::*;

    bit clk = 1'b0;

    always #5 clk = ~clk;

    packet_switch_interface #(
        .PACKET_WIDTH(PACKET_WIDTH)
    ) switch_interface (
        .clk(clk)
    );

    packet_switch #(
        .PACKET_WIDTH(PACKET_WIDTH),
        .FIFO_DEPTH(FIFO_DEPTH)
    ) dut (
        .clk(clk),
        .reset(switch_interface.reset),
        .input_packet(switch_interface.input_packet),
        .input_valid(switch_interface.input_valid),
        .input_ready(switch_interface.input_ready),
        .output_packet(switch_interface.output_packet),
        .output_valid(switch_interface.output_valid),
        .output_ready(switch_interface.output_ready)
    );

    initial begin
        uvm_config_db#(virtual packet_switch_interface.DRIVER)::set(
            null, "*", "driver_vif", switch_interface.DRIVER
        );

        uvm_config_db#(virtual packet_switch_interface.MONITOR)::set(
            null, "*", "monitor_vif", switch_interface.MONITOR
        );

        run_test("packet_switch_base_test");
    end

endmodule
