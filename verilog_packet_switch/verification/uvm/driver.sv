class packet_switch_driver extends uvm_driver #(packet_switch_transaction);

    `uvm_component_utils(packet_switch_driver)

    // Connection from the UVM driver to the SystemVerilog interface.
    virtual packet_switch_interface.DRIVER vif;

    function new(string name = "packet_switch_driver", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);

        if (!uvm_config_db#(virtual packet_switch_interface.DRIVER)::get(
                this, "", "driver_vif", vif)) begin
            `uvm_fatal("NO_DRIVER_VIF", "Driver interface was not provided")
        end
    endfunction

    task drive_transaction(packet_switch_transaction transaction);
        @(vif.driver_cb);

        vif.driver_cb.reset         <= transaction.reset;
        vif.driver_cb.input_packet  <= transaction.input_packet;
        vif.driver_cb.input_valid   <= transaction.input_valid;
        vif.driver_cb.output_ready  <= transaction.output_ready;
    endtask

    task run_phase(uvm_phase phase);
        forever begin
            seq_item_port.get_next_item(req);
            drive_transaction(req);
            seq_item_port.item_done();
        end
    endtask

endclass
