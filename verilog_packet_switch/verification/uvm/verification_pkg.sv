`include "uvm_macros.svh"

package packet_switch_uvm_pkg;

    import uvm_pkg::*;
    import packet_switch_parameters_pkg::*;

    `include "transaction.sv"
    `include "sequencer.sv"
    `include "driver.sv"
    `include "monitor.sv"
    `include "agent.sv"

endpackage
