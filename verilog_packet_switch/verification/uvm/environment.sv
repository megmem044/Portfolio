class packet_switch_environment extends uvm_env;

    `uvm_component_utils(packet_switch_environment)

    packet_switch_agent      agent;
    packet_switch_scoreboard scoreboard;
    packet_switch_coverage   coverage;

    function new(string name = "packet_switch_environment", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);

        agent = packet_switch_agent::type_id::create("agent", this);
        scoreboard = packet_switch_scoreboard::type_id::create("scoreboard", this);
        coverage = packet_switch_coverage::type_id::create("coverage", this);
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        agent.monitor.analysis_port.connect(scoreboard.analysis_export);
        agent.monitor.analysis_port.connect(coverage.analysis_export);
    endfunction

endclass
