class packet_switch_coverage extends uvm_subscriber #(packet_switch_transaction);

    `uvm_component_utils(packet_switch_coverage)

    covergroup route_coverage with function sample(
        int input_number,
        int destination
    );
        option.per_instance = 1;

        input_port: coverpoint input_number {
            bins ports[] = {[0:PORT_COUNT-1]};
        }

        destination_port: coverpoint destination {
            bins ports[] = {[0:PORT_COUNT-1]};
        }

        input_to_destination: cross input_port, destination_port;
    endgroup

    covergroup flow_control_coverage with function sample(
        int input_number,
        bit valid_signal,
        bit ready_signal
    );
        option.per_instance = 1;

        input_port: coverpoint input_number {
            bins ports[] = {[0:PORT_COUNT-1]};
        }

        handshake_state: coverpoint {valid_signal, ready_signal} {
            bins idle          = {2'b00};
            bins ready_waiting = {2'b01};
            bins backpressured = {2'b10};
            bins accepted      = {2'b11};
        }

        port_by_handshake: cross input_port, handshake_state;
    endgroup

    covergroup output_flow_coverage with function sample(
        int output_number,
        bit valid_signal,
        bit ready_signal
    );
        option.per_instance = 1;

        output_port: coverpoint output_number {
            bins ports[] = {[0:PORT_COUNT-1]};
        }

        handshake_state: coverpoint {valid_signal, ready_signal} {
            bins idle          = {2'b00};
            bins ready_waiting = {2'b01};
            bins backpressured = {2'b10};
            bins accepted      = {2'b11};
        }

        port_by_handshake: cross output_port, handshake_state;
    endgroup

    covergroup simultaneous_transfer_coverage with function sample(
        int accepted_input_count,
        int accepted_output_count
    );
        option.per_instance = 1;

        input_transfers: coverpoint accepted_input_count {
            bins counts[] = {[0:PORT_COUNT]};
        }

        output_transfers: coverpoint accepted_output_count {
            bins counts[] = {[0:PORT_COUNT]};
        }

        input_by_output_count: cross input_transfers, output_transfers;
    endgroup

    covergroup reset_coverage with function sample(bit reset_signal);
        option.per_instance = 1;

        reset_state: coverpoint reset_signal {
            bins deasserted    = {1'b0};
            bins asserted      = {1'b1};
            bins entered_reset = (1'b0 => 1'b1);
            bins left_reset    = (1'b1 => 1'b0);
        }
    endgroup

    function new(string name = "packet_switch_coverage", uvm_component parent = null);
        super.new(name, parent);
        route_coverage = new();
        flow_control_coverage = new();
        output_flow_coverage = new();
        simultaneous_transfer_coverage = new();
        reset_coverage = new();
    endfunction

    function void write(packet_switch_transaction observed);
        bit [PACKET_WIDTH-1:0] accepted_packet;
        int destination;
        int accepted_input_count;
        int accepted_output_count;

        reset_coverage.sample(observed.reset);

        if (!observed.reset) begin
            accepted_input_count = 0;
            accepted_output_count = 0;

            for (int input_number = 0; input_number < PORT_COUNT; input_number++) begin
                flow_control_coverage.sample(
                    input_number,
                    observed.input_valid[input_number],
                    observed.input_ready[input_number]
                );

                if (observed.input_valid[input_number] &&
                    observed.input_ready[input_number]) begin
                    accepted_input_count++;
                    accepted_packet = observed.input_packet[
                        (input_number*PACKET_WIDTH) +: PACKET_WIDTH
                    ];
                    destination = accepted_packet[
                        PACKET_WIDTH-1 -: DESTINATION_WIDTH
                    ];
                    route_coverage.sample(input_number, destination);
                end
            end

            for (int output_number = 0; output_number < PORT_COUNT; output_number++) begin
                output_flow_coverage.sample(
                    output_number,
                    observed.output_valid[output_number],
                    observed.output_ready[output_number]
                );

                if (observed.output_valid[output_number] &&
                    observed.output_ready[output_number]) begin
                    accepted_output_count++;
                end
            end

            simultaneous_transfer_coverage.sample(
                accepted_input_count,
                accepted_output_count
            );
        end
    endfunction

endclass
