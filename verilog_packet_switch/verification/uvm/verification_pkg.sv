`include "uvm_macros.svh"

package packet_switch_uvm_pkg;

    import uvm_pkg::*;
    import packet_switch_parameters_pkg::*;

    `include "transaction.sv"
    `include "sequence.sv"
    `include "contention_sequence.sv"
    `include "fifo_full_sequence.sv"
    `include "parallel_routing_sequence.sv"
    `include "reset_during_traffic_sequence.sv"
    `include "sequencer.sv"
    `include "driver.sv"
    `include "monitor.sv"
    `include "agent.sv"
    `include "scoreboard.sv"
    `include "coverage.sv"
    `include "environment.sv"
    `include "test.sv"
    `include "contention_test.sv"
    `include "fifo_full_test.sv"
    `include "parallel_routing_test.sv"
    `include "reset_during_traffic_test.sv"

endpackage
