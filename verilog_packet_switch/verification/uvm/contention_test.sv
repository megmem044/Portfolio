class packet_switch_contention_test extends packet_switch_base_test;

    `uvm_component_utils(packet_switch_contention_test)

    function new(string name = "packet_switch_contention_test", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    task run_phase(uvm_phase phase);
        packet_switch_contention_sequence sequence;

        phase.raise_objection(this);

        sequence = packet_switch_contention_sequence::type_id::create("sequence");
        sequence.start(environment.agent.sequencer);

        phase.drop_objection(this);
    endtask

endclass
