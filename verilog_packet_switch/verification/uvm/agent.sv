class packet_switch_agent extends uvm_agent;

    `uvm_component_utils(packet_switch_agent)

    packet_switch_sequencer sequencer;
    packet_switch_driver    driver;
    packet_switch_monitor   monitor;

    function new(string name = "packet_switch_agent", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);

        sequencer = packet_switch_sequencer::type_id::create("sequencer", this);
        driver    = packet_switch_driver::type_id::create("driver", this);
        monitor   = packet_switch_monitor::type_id::create("monitor", this);
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        driver.seq_item_port.connect(sequencer.seq_item_export);
    endfunction

endclass
