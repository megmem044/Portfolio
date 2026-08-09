class packet_switch_scoreboard extends uvm_scoreboard;

    `uvm_component_utils(packet_switch_scoreboard)

    // Receives one complete interface snapshot from the monitor each cycle.
    uvm_analysis_imp #(packet_switch_transaction, packet_switch_scoreboard) analysis_export;

    // Software-model copy of each input packet queue.
    bit [PACKET_WIDTH-1:0] expected_queue [PORT_COUNT][$];

    // Input number that should receive first priority at each output.
    int unsigned expected_priority [PORT_COUNT];

    function new(string name = "packet_switch_scoreboard", uvm_component parent = null);
        super.new(name, parent);
        analysis_export = new("analysis_export", this);
    endfunction

    function void reset_model();
        for (int input_number = 0; input_number < PORT_COUNT; input_number++) begin
            expected_queue[input_number].delete();
        end

        for (int output_number = 0; output_number < PORT_COUNT; output_number++) begin
            expected_priority[output_number] = 0;
        end
    endfunction

    function void record_accepted_inputs(packet_switch_transaction observed);
        bit [PACKET_WIDTH-1:0] accepted_packet;

        for (int input_number = 0; input_number < PORT_COUNT; input_number++) begin
            if (observed.input_valid[input_number] &&
                observed.input_ready[input_number]) begin
                accepted_packet = observed.input_packet[
                    (input_number*PACKET_WIDTH) +: PACKET_WIDTH
                ];
                expected_queue[input_number].push_back(accepted_packet);
            end
        end
    endfunction

    function int find_expected_input(int output_number);
        int candidate_input;
        bit [DESTINATION_WIDTH-1:0] destination;

        find_expected_input = -1;

        for (int offset = 0; offset < PORT_COUNT; offset++) begin
            candidate_input = (expected_priority[output_number] + offset) % PORT_COUNT;

            if ((find_expected_input == -1) &&
                (expected_queue[candidate_input].size() > 0)) begin
                destination = expected_queue[candidate_input][0][
                    PACKET_WIDTH-1 -: DESTINATION_WIDTH
                ];

                if (destination == output_number)
                    find_expected_input = candidate_input;
            end
        end
    endfunction

    function void check_outputs(packet_switch_transaction observed);
        int expected_input [PORT_COUNT];
        bit expected_valid [PORT_COUNT];
        bit [PACKET_WIDTH-1:0] expected_packet;
        bit [PACKET_WIDTH-1:0] actual_packet;

        // First check every output from the same pre-clock model state.
        for (int output_number = 0; output_number < PORT_COUNT; output_number++) begin
            expected_input[output_number] = find_expected_input(output_number);
            expected_valid[output_number] = (expected_input[output_number] >= 0);

            if (observed.output_valid[output_number] != expected_valid[output_number]) begin
                `uvm_error("OUTPUT_VALID_MISMATCH", $sformatf(
                    "Output %0d valid=%0b, expected=%0b",
                    output_number,
                    observed.output_valid[output_number],
                    expected_valid[output_number]
                ))
            end

            if (expected_valid[output_number] && observed.output_valid[output_number]) begin
                expected_packet = expected_queue[expected_input[output_number]][0];
                actual_packet = observed.output_packet[
                    (output_number*PACKET_WIDTH) +: PACKET_WIDTH
                ];

                if (actual_packet != expected_packet) begin
                    `uvm_error("OUTPUT_PACKET_MISMATCH", $sformatf(
                        "Output %0d packet=0x%0h, expected=0x%0h from input %0d",
                        output_number,
                        actual_packet,
                        expected_packet,
                        expected_input[output_number]
                    ))
                end
            end
        end

        // Then apply all accepted transfers after the cycle has been checked.
        for (int output_number = 0; output_number < PORT_COUNT; output_number++) begin
            if (expected_valid[output_number] &&
                observed.output_valid[output_number] &&
                observed.output_ready[output_number]) begin
                expected_packet = expected_queue[expected_input[output_number]].pop_front();
                expected_priority[output_number] =
                    (expected_input[output_number] + 1) % PORT_COUNT;
            end
        end
    endfunction

    function void write(packet_switch_transaction observed);
        if (observed.reset) begin
            reset_model();
        end else begin
            check_outputs(observed);
            record_accepted_inputs(observed);
        end
    endfunction

endclass
