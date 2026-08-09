class packet_switch_parallel_routing_sequence extends packet_switch_base_sequence;

    `uvm_object_utils(packet_switch_parallel_routing_sequence)

    int unsigned parallel_cycle_count = 16;

    function new(string name = "packet_switch_parallel_routing_sequence");
        super.new(name);
    endfunction

    task send_parallel_traffic();
        packet_switch_transaction traffic_item;
        bit [PACKET_WIDTH-1:0] packet_value;

        for (int cycle_number = 0;
             cycle_number < parallel_cycle_count;
             cycle_number++) begin
            traffic_item = packet_switch_transaction::type_id::create("parallel_item");
            start_item(traffic_item);

            traffic_item.reset        = 1'b0;
            traffic_item.input_packet = '0;
            traffic_item.input_valid  = '1;
            traffic_item.output_ready = '1;

            for (int input_number = 0; input_number < PORT_COUNT; input_number++) begin
                packet_value = (cycle_number * PORT_COUNT) + input_number;
                packet_value[PACKET_WIDTH-1 -: DESTINATION_WIDTH] = input_number;
                traffic_item.input_packet[
                    (input_number*PACKET_WIDTH) +: PACKET_WIDTH
                ] = packet_value;
            end

            finish_item(traffic_item);
        end
    endtask

    task body();
        send_reset();
        send_parallel_traffic();
        send_drain();
    endtask

endclass
