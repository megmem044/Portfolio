class packet_switch_parallel_routing_test extends packet_switch_base_test;

    `uvm_component_utils(packet_switch_parallel_routing_test)

    function new(string name = "packet_switch_parallel_routing_test", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    task run_phase(uvm_phase phase);
        packet_switch_parallel_routing_sequence test_sequence;

        phase.raise_objection(this);

        test_sequence = packet_switch_parallel_routing_sequence::type_id::create("test_sequence");
        test_sequence.start(environment.agent.sequencer);

        phase.drop_objection(this);
    endtask

endclass
