class packet_switch_sequencer extends uvm_sequencer #(packet_switch_transaction);

    `uvm_component_utils(packet_switch_sequencer)

    function new(string name = "packet_switch_sequencer", uvm_component parent = null);
        super.new(name, parent);
    endfunction

endclass
