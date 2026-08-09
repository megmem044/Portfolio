class packet_switch_reset_during_traffic_sequence extends packet_switch_base_sequence;

    `uvm_object_utils(packet_switch_reset_during_traffic_sequence)

    function new(string name = "packet_switch_reset_during_traffic_sequence");
        super.new(name);
    endfunction

    task send_pre_reset_traffic();
        packet_switch_transaction traffic_item;
        bit [PACKET_WIDTH-1:0] packet_value;

        repeat (FIFO_DEPTH) begin
            traffic_item = packet_switch_transaction::type_id::create("pre_reset_item");
            start_item(traffic_item);

            traffic_item.reset        = 1'b0;
            traffic_item.input_packet = '0;
            traffic_item.input_valid  = '1;
            traffic_item.output_ready = '1;
            traffic_item.output_ready[0] = 1'b0;

            for (int input_number = 0; input_number < PORT_COUNT; input_number++) begin
                packet_value = input_number;
                packet_value[PACKET_WIDTH-1 -: DESTINATION_WIDTH] = '0;
                traffic_item.input_packet[
                    (input_number*PACKET_WIDTH) +: PACKET_WIDTH
                ] = packet_value;
            end

            finish_item(traffic_item);
        end
    endtask

    task send_mid_traffic_reset();
        packet_switch_transaction reset_item;

        repeat (2) begin
            reset_item = packet_switch_transaction::type_id::create("mid_traffic_reset_item");
            start_item(reset_item);

            reset_item.reset        = 1'b1;
            reset_item.input_packet = '0;
            reset_item.input_valid  = '0;
            reset_item.output_ready = '0;

            finish_item(reset_item);
        end
    endtask

    task send_post_reset_traffic();
        packet_switch_transaction traffic_item;
        bit [PACKET_WIDTH-1:0] packet_value;

        repeat (4) begin
            traffic_item = packet_switch_transaction::type_id::create("post_reset_item");
            start_item(traffic_item);

            traffic_item.reset        = 1'b0;
            traffic_item.input_packet = '0;
            traffic_item.input_valid  = '1;
            traffic_item.output_ready = '1;

            for (int input_number = 0; input_number < PORT_COUNT; input_number++) begin
                packet_value = (16 * PORT_COUNT) + input_number;
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
        send_pre_reset_traffic();
        send_mid_traffic_reset();
        send_post_reset_traffic();
        send_drain();
    endtask

endclass
