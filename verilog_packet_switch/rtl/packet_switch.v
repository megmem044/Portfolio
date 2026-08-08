module packet_switch #(
    parameter PACKET_WIDTH = 16, // Total number of bits in one packet
    parameter FIFO_DEPTH   = 4   // Number of packets stored at each input
) (
    input                         clk,
    input                         reset,

    // Four input ports
    input      [(4*PACKET_WIDTH)-1:0] input_packet,
    input      [3:0]                  input_valid,
    output     [3:0]                  input_ready,

    // Four output ports
    output     [(4*PACKET_WIDTH)-1:0] output_packet,
    output     [3:0]                  output_valid,
    input      [3:0]                  output_ready
);

    // -------------------------------------------------------------------------
    // Internal signals
    // -------------------------------------------------------------------------
    wire [(4*PACKET_WIDTH)-1:0] queue_front_packet; // Oldest packet from each input queue

    wire [3:0] queue_full;  // Full status from each input queue
    wire [3:0] queue_empty; // Empty status from each input queue
    wire [3:0] queue_push;  // Accepted packet arrival for each input queue
    wire [3:0] queue_pop;   // Accepted packet departure for each input queue

    // Bit (input_number * 4 + output_number) is one routing request.
    wire [15:0] routing_request;

    // Bit (output_number * 4 + input_number) is one arbitration grant.
    wire [15:0] output_grant;

    wire [3:0] output_transfer_accepted; // Completed transfer for each output


    // -------------------------------------------------------------------------
    // Four input packet queues
    // -------------------------------------------------------------------------
    assign input_ready = ~queue_full;
    assign queue_push  = input_valid & input_ready;

    genvar input_number;
    generate
        for (input_number = 0; input_number < 4; input_number = input_number + 1) begin : input_queues
            input_packet_queue #(
                .PACKET_WIDTH(PACKET_WIDTH),
                .FIFO_DEPTH(FIFO_DEPTH)
            ) queue (
                .clk(clk),
                .reset(reset),
                .push_packet(queue_push[input_number]),
                .incoming_packet(input_packet[(input_number*PACKET_WIDTH) +: PACKET_WIDTH]),
                .pop_packet(queue_pop[input_number]),
                .front_packet(queue_front_packet[(input_number*PACKET_WIDTH) +: PACKET_WIDTH]),
                .fifo_full(queue_full[input_number]),
                .fifo_empty(queue_empty[input_number])
            );
        end
    endgenerate


    // -------------------------------------------------------------------------
    // Destination decoding for each queued packet
    // -------------------------------------------------------------------------
    genvar decoder_input;
    generate
        for (decoder_input = 0; decoder_input < 4; decoder_input = decoder_input + 1) begin : destination_decoders
            packet_destination_decoder #(
                .PACKET_WIDTH(PACKET_WIDTH)
            ) decoder (
                .front_packet(queue_front_packet[(decoder_input*PACKET_WIDTH) +: PACKET_WIDTH]),
                .queue_empty(queue_empty[decoder_input]),
                .output_request(routing_request[(decoder_input*4) +: 4])
            );
        end
    endgenerate


    // -------------------------------------------------------------------------
    // Fair input selection for each output
    // -------------------------------------------------------------------------
    genvar output_number;
    generate
        for (output_number = 0; output_number < 4; output_number = output_number + 1) begin : output_selectors
            fair_output_selector selector (
                .clk(clk),
                .reset(reset),
                .request({
                    routing_request[12 + output_number],
                    routing_request[8  + output_number],
                    routing_request[4  + output_number],
                    routing_request[0  + output_number]
                }),
                .transfer_accepted(output_transfer_accepted[output_number]),
                .grant(output_grant[(output_number*4) +: 4])
            );
        end
    endgenerate


    // -------------------------------------------------------------------------
    // Output packet and valid selection
    // -------------------------------------------------------------------------
    genvar selected_output;
    generate
        for (selected_output = 0; selected_output < 4; selected_output = selected_output + 1) begin : output_datapaths
            assign output_valid[selected_output] =
                |output_grant[(selected_output*4) +: 4];

            assign output_packet[(selected_output*PACKET_WIDTH) +: PACKET_WIDTH] =
                output_grant[(selected_output*4) + 0] ? queue_front_packet[(0*PACKET_WIDTH) +: PACKET_WIDTH] :
                output_grant[(selected_output*4) + 1] ? queue_front_packet[(1*PACKET_WIDTH) +: PACKET_WIDTH] :
                output_grant[(selected_output*4) + 2] ? queue_front_packet[(2*PACKET_WIDTH) +: PACKET_WIDTH] :
                output_grant[(selected_output*4) + 3] ? queue_front_packet[(3*PACKET_WIDTH) +: PACKET_WIDTH] :
                {PACKET_WIDTH{1'b0}};

            assign output_transfer_accepted[selected_output] =
                output_valid[selected_output] && output_ready[selected_output];
        end
    endgenerate


    // -------------------------------------------------------------------------
    // Input queue pop control
    // -------------------------------------------------------------------------
    genvar popped_input;
    generate
        for (popped_input = 0; popped_input < 4; popped_input = popped_input + 1) begin : queue_pop_controls
            assign queue_pop[popped_input] =
                (output_grant[(0*4) + popped_input] && output_transfer_accepted[0]) ||
                (output_grant[(1*4) + popped_input] && output_transfer_accepted[1]) ||
                (output_grant[(2*4) + popped_input] && output_transfer_accepted[2]) ||
                (output_grant[(3*4) + popped_input] && output_transfer_accepted[3]);
        end
    endgenerate

endmodule
