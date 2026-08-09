class packet_switch_base_sequence extends uvm_sequence #(packet_switch_transaction);

    `uvm_object_utils(packet_switch_base_sequence)

    int unsigned transaction_count = 100; // Number of traffic cycles to generate

    function new(string name = "packet_switch_base_sequence");
        super.new(name);
    endfunction

    task send_reset();
        packet_switch_transaction reset_item;

        repeat (2) begin
            reset_item = packet_switch_transaction::type_id::create("reset_item");
            start_item(reset_item);
            reset_item.reset        = 1'b1;
            reset_item.input_packet = '0;
            reset_item.input_valid  = '0;
            reset_item.output_ready = '0;
            finish_item(reset_item);
        end

        reset_item = packet_switch_transaction::type_id::create("reset_release_item");
        start_item(reset_item);
        reset_item.reset        = 1'b0;
        reset_item.input_packet = '0;
        reset_item.input_valid  = '0;
        reset_item.output_ready = '1;
        finish_item(reset_item);
    endtask

    task send_random_traffic();
        packet_switch_transaction traffic_item;

        repeat (transaction_count) begin
            traffic_item = packet_switch_transaction::type_id::create("traffic_item");
            start_item(traffic_item);

            if (!traffic_item.randomize() with { reset == 1'b0; }) begin
                `uvm_fatal("RANDOMIZE_FAILED", "Unable to randomize packet-switch traffic")
            end

            finish_item(traffic_item);
        end
    endtask

    task send_drain();
        packet_switch_transaction drain_item;

        // One setup cycle plus enough cycles to empty all four full input queues.
        repeat ((FIFO_DEPTH * PORT_COUNT) + 1) begin
            drain_item = packet_switch_transaction::type_id::create("drain_item");
            start_item(drain_item);
            drain_item.reset        = 1'b0;
            drain_item.input_packet = '0;
            drain_item.input_valid  = '0;
            drain_item.output_ready = '1;
            finish_item(drain_item);
        end
    endtask

    task body();
        send_reset();
        send_random_traffic();
        send_drain();
    endtask

endclass
