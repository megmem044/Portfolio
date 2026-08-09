class packet_switch_base_test extends uvm_test;

    `uvm_component_utils(packet_switch_base_test)

    packet_switch_environment environment;

    function new(string name = "packet_switch_base_test", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        environment = packet_switch_environment::type_id::create("environment", this);
    endfunction

    task run_phase(uvm_phase phase);
        packet_switch_base_sequence test_sequence;

        phase.raise_objection(this);

        test_sequence = packet_switch_base_sequence::type_id::create("test_sequence");
        test_sequence.start(environment.agent.sequencer);

        phase.drop_objection(this);
    endtask

endclass
