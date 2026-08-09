class packet_switch_monitor extends uvm_monitor;

    `uvm_component_utils(packet_switch_monitor)

    // Read-only connection to the packet-switch interface.
    virtual packet_switch_interface.MONITOR vif;

    // Sends observed clock-cycle snapshots to subscribers such as the scoreboard.
    uvm_analysis_port #(packet_switch_transaction) analysis_port;

    function new(string name = "packet_switch_monitor", uvm_component parent = null);
        super.new(name, parent);
        analysis_port = new("analysis_port", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);

        if (!uvm_config_db#(virtual packet_switch_interface.MONITOR)::get(
                this, "", "monitor_vif", vif)) begin
            `uvm_fatal("NO_MONITOR_VIF", "Monitor interface was not provided")
        end
    endfunction

    task sample_transaction();
        packet_switch_transaction observed;

        @(vif.monitor_cb);

        observed = packet_switch_transaction::type_id::create("observed");
        observed.reset         = vif.monitor_cb.reset;
        observed.input_packet  = vif.monitor_cb.input_packet;
        observed.input_valid   = vif.monitor_cb.input_valid;
        observed.input_ready   = vif.monitor_cb.input_ready;
        observed.output_packet = vif.monitor_cb.output_packet;
        observed.output_valid  = vif.monitor_cb.output_valid;
        observed.output_ready  = vif.monitor_cb.output_ready;

        analysis_port.write(observed);
    endtask

    task run_phase(uvm_phase phase);
        forever begin
            sample_transaction();
        end
    endtask

endclass
